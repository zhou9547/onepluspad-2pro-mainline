#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise QMI location over QRTR after reviewed MPSS startup."""

import argparse
import json
import math
import os
from pathlib import Path
import re
import subprocess
import signal
import time


NMEA = re.compile(r"^\$(?:GP|GN|GL|GA|GB)(?:GGA|RMC),.*\*[0-9A-Fa-f]{2}$")


def bounded_stdout(output):
    """Retain lifecycle evidence when a long NMEA stream fills the tail."""
    tail = output[-8192:]
    markers = []
    for prefix in ("LOCATION_SESSION_NMEA_DEFAULTS ",
                   "LOCATION_SESSION_POSITION_EVENTS ", "LOCATION_SESSION_NO_SESSION ",
                   "LOCATION_SESSION_STARTED ", "LOCATION_SESSION_STOPPED "):
        marker = next((line for line in output.splitlines()
                       if line.startswith(prefix) and len(line) <= 512), None)
        if marker is not None and marker not in tail.splitlines():
            markers.append(marker)
    return "\n".join(markers + [tail])


def run(args, timeout):
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "returncode": result.returncode,
            "stdout": bounded_stdout(result.stdout),
            "stderr": result.stderr[-8192:],
        }
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else error.stdout or ""
        stderr = error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else error.stderr or ""
        return {
            "returncode": 124,
            "timed_out": True,
            "stdout": stdout[-8192:],
            "stderr": stderr[-8192:],
        }


def nmea_coordinate(value, direction):
    if not value or direction not in ("N", "S", "E", "W"):
        return None
    split = 2 if direction in ("N", "S") else 3
    if len(value) <= split:
        return None
    try:
        degrees = int(value[:split])
        minutes = float(value[split:])
    except ValueError:
        return None
    limit = 90 if direction in ("N", "S") else 180
    if not math.isfinite(minutes) or not 0 <= minutes < 60 or not 0 <= degrees <= limit:
        return None
    if degrees == limit and minutes != 0:
        return None
    result = degrees + minutes / 60
    return -result if direction in ("S", "W") else result


def parse_fix(lines):
    fixes = []
    for line in lines:
        if not NMEA.fullmatch(line):
            continue
        payload, checksum = line[1:].rsplit("*", 1)
        actual = 0
        for character in payload:
            actual ^= ord(character)
        if actual != int(checksum, 16):
            continue
        fields = line[1:].split("*", 1)[0].split(",")
        if fields[0].endswith("RMC") and len(fields) >= 7 and fields[2] == "A":
            latitude = nmea_coordinate(fields[3], fields[4])
            longitude = nmea_coordinate(fields[5], fields[6])
            if latitude is not None and longitude is not None:
                fixes.append(
                    {
                        "type": "RMC",
                        "latitude": latitude,
                        "longitude": longitude,
                        "date": fields[9] if len(fields) > 9 else None,
                    }
                )
        if (fields[0].endswith("GGA") and len(fields) >= 8
                and fields[6] in ("1", "2", "3", "4", "5")
                and fields[7].isdigit()):
            latitude = nmea_coordinate(fields[2], fields[3])
            longitude = nmea_coordinate(fields[4], fields[5])
            if latitude is not None and longitude is not None:
                fixes.append(
                    {
                        "type": "GGA",
                        "latitude": latitude,
                        "longitude": longitude,
                        "quality": int(fields[6]),
                        "satellites": int(fields[7]) if len(fields) > 7 and fields[7] else None,
                    }
                )
    return fixes[-8:]


def probe_devices(qmicli, candidates, ready_seconds):
    """Wait briefly for modem QRTR services to publish before failing."""
    probes = []
    deadline = time.monotonic() + ready_seconds
    while True:
        for device in candidates:
            if device is None:
                continue
            probe = run([qmicli, "-d", device, "--loc-get-operation-mode"], 12)
            probes.append({"device": device, **probe})
            if probe["returncode"] == 0:
                return device, probes
        if time.monotonic() >= deadline:
            return None, probes
        time.sleep(1)


def collect_session(qmicli, device, seconds):
    """Keep one LOC client/session across separate start, follow and stop actions."""
    base = [qmicli, "-d", device]
    setup = run(base + ["--loc-noop", "--client-no-release-cid"], 15)
    result = {
        "setup": setup,
        "start_attempts": [],
        "fixes": [],
        "fix_acquired": False,
        "engine_control_qualified": False,
        "cleanup_complete": False,
    }
    match = re.search(r"CID:\s*'?(\d+)'?", setup.get("stdout", ""))
    if setup["returncode"] != 0 or not match:
        return result
    base.append("--client-cid=" + match[1])
    result["nmea_types"] = run(
        base + ["--loc-set-nmea-types=gga|rmc", "--client-no-release-cid"], 15
    )
    result["engine_lock"] = run(
        base + ["--loc-set-engine-lock=none", "--client-no-release-cid"], 15
    )
    started = None
    for attempt in range(1, 4):
        started = run(
            base + ["--loc-start", "--loc-session-id=1", "--client-no-release-cid"], 15
        )
        result["start_attempts"].append({"attempt": attempt, **started})
        if started["returncode"] == 0:
            break
        time.sleep(2)
    result["start"] = started
    if not started or started["returncode"] != 0:
        failed_stop = run(base + ["--loc-stop", "--loc-session-id=1"], 15)
        result["failed_start_stop"] = failed_stop
        result["cleanup_complete"] = failed_stop["returncode"] == 0
        return result
    process = None
    try:
        result["engine_control_qualified"] = True
        # libqmi rejects --loc-start and --loc-get-position-report together.
        # A follow is bounded here, then interrupted gracefully before LOC stop.
        process = subprocess.Popen(
            base + ["--loc-follow-nmea", "--client-no-release-cid"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=seconds)
        except subprocess.TimeoutExpired:
            process.send_signal(signal.SIGINT)
            try:
                stdout, stderr = process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate(timeout=5)
        result["follow_returncode"] = process.returncode
        result["follow_stderr"] = stderr[-4096:]
        result["nmea"] = [line.strip() for line in stdout.splitlines()
                          if NMEA.fullmatch(line.strip())][-64:]
        result["fixes"] = parse_fix(result["nmea"])
        result["fix_acquired"] = bool(result["fixes"])
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
        stopped = run(base + ["--loc-stop", "--loc-session-id=1"], 15)
        result["stop"] = stopped
        result["cleanup_complete"] = stopped["returncode"] == 0
    return result


def collect_native_session(native, seconds):
    """Run one native QRTR client for setup, start, follow and stop."""
    if not 5 <= seconds <= 180:
        raise ValueError('Native GNSS collection must stay between 5 and 180 seconds')
    native = str(native)
    # Native soft deadline is seconds+45; pending start and stop take up to
    # 20 seconds each. Keep ten more for GLib timer granularity/process exit.
    process = run([native, "--seconds", str(seconds)], seconds + 95)
    lines = process.get("stdout", "").splitlines()
    nmea = [
        line[5:].strip()
        for line in lines
        if line.startswith("NMEA ") and line[5:].strip()
    ][-64:]
    fixes = parse_fix(nmea)
    positions = []
    for line in lines:
        if not line.startswith("LOCATION_SESSION_POSITION "):
            continue
        try:
            value = json.loads(line.split(" ", 1)[1])
            latitude, longitude = value["latitude"], value["longitude"]
            if (value.get("status") == "success" and value.get("satellite") is True
                    and type(latitude) in (int, float) and type(longitude) in (int, float)
                    and math.isfinite(latitude) and math.isfinite(longitude)
                    and -90 <= latitude <= 90 and -180 <= longitude <= 180):
                positions.append({"type": "QMI_LOC_SATELLITE", "latitude": latitude,
                                  "longitude": longitude})
        except (ValueError, KeyError, TypeError):
            continue
    fixes = (fixes + positions)[-8:]
    started = any(
        line.startswith("LOCATION_SESSION_STARTED") for line in lines
    )
    stopped = any(
        line.startswith("LOCATION_SESSION_STOPPED") for line in lines
    )
    no_session = ("LOCATION_SESSION_NO_SESSION start_requested=0" in lines
                  and not started and not stopped and process.get("returncode") == 1
                  and process.get("timed_out", False) is False)
    return {
        "native": native,
        "returncode": process.get("returncode"),
        "timed_out": process.get("timed_out", False),
        "started": started,
        "stopped": stopped,
        "no_session_started": no_session,
        "cleanup_not_needed": no_session,
        "position_events_fallback": any(
            line.startswith("LOCATION_SESSION_POSITION_EVENTS ") for line in lines
        ),
        "nmea_defaults_used": any(
            line.startswith("LOCATION_SESSION_NMEA_DEFAULTS ") for line in lines
        ),
        "stderr": process.get("stderr", "")[-8192:],
        "nmea": nmea,
        "fixes": fixes,
        "fix_acquired": bool(fixes),
        "engine_control_qualified": started and stopped,
        "cleanup_complete": (stopped and process.get("returncode") == 0) or no_session,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=None)
    parser.add_argument("--seconds", type=int, default=45)
    parser.add_argument("--ready-seconds", type=int, default=60)
    args = parser.parse_args()
    if not 5 <= args.seconds <= 180:
        raise ValueError("GNSS collection must stay between 5 and 180 seconds")
    if not 0 <= args.ready_seconds <= 90:
        raise ValueError("GNSS readiness wait must stay between 0 and 90 seconds")
    if not Path("/run/oneplus13/ram-session").is_file():
        raise RuntimeError("Protected phone RAM session required")
    qmicli = next(
        (path for path in ("/usr/bin/qmicli", "/usr/local/bin/qmicli") if Path(path).is_file()),
        None,
    )
    if not qmicli:
        raise RuntimeError("qmicli is unavailable")
    native = Path("/usr/libexec/oneplus13-location-session")
    if native.is_file() and os.access(native, os.X_OK):
        result = collect_native_session(native, args.seconds)
        result["scope"] = "ONEPLUS13_RAM_QMI_GNSS"
        result["pass"] = bool(
            result["engine_control_qualified"]
            and result["fix_acquired"]
            and result["cleanup_complete"]
        )
        print("RAM_GNSS_RESULT " + json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["pass"] else 1)
    candidates = (
        [args.device]
        if args.device
        else ["qrtr://0", "qrtr://1"]
    )
    selected, probes = probe_devices(qmicli, candidates, args.ready_seconds)
    result = {
        "scope": "ONEPLUS13_RAM_QMI_GNSS",
        "qmicli": qmicli,
        "device_probes": probes,
        "selected_device": selected,
        "nmea": [],
        "fixes": [],
        "fix_acquired": False,
    }
    if selected is None:
        print("RAM_GNSS_RESULT " + json.dumps(result, sort_keys=True))
        raise SystemExit(1)
    result.update(collect_session(qmicli, selected, args.seconds))
    result["pass"] = (result["engine_control_qualified"] and result["fix_acquired"]
                      and result["cleanup_complete"])
    print("RAM_GNSS_RESULT " + json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
