#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise QMI location over QRTR after reviewed MPSS startup."""

import argparse
import json
from pathlib import Path
import re
import subprocess


NMEA = re.compile(r"^\$(?:GP|GN|GL|GA|GB)(?:GGA|RMC),.*\*[0-9A-Fa-f]{2}$")


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
            "stdout": result.stdout[-8192:],
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
    degrees = int(value[:split])
    minutes = float(value[split:])
    result = degrees + minutes / 60
    return -result if direction in ("S", "W") else result


def parse_fix(lines):
    fixes = []
    for line in lines:
        if not NMEA.fullmatch(line):
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
        if fields[0].endswith("GGA") and len(fields) >= 6 and fields[6] not in ("", "0"):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default=None)
    parser.add_argument("--seconds", type=int, default=45)
    args = parser.parse_args()
    if not 5 <= args.seconds <= 240:
        raise ValueError("GNSS collection must stay between 5 and 240 seconds")
    if not Path("/run/oneplus13/ram-session").is_file():
        raise RuntimeError("Protected phone RAM session required")
    qmicli = next(
        (path for path in ("/usr/bin/qmicli", "/usr/local/bin/qmicli") if Path(path).is_file()),
        None,
    )
    if not qmicli:
        raise RuntimeError("qmicli is unavailable")
    candidates = [args.device] if args.device else ["qrtr://", "qrtr://0", "qrtr://1"]
    selected = None
    probes = []
    for device in candidates:
        if device is None:
            continue
        probe = run([qmicli, "-d", device, "--loc-get-operation-mode"], 12)
        probes.append({"device": device, **probe})
        if probe["returncode"] == 0:
            selected = device
            break
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
    started = run(
        [qmicli, "-d", selected, "--loc-start", "--loc-get-position-report",
         "--loc-timeout", str(args.seconds)],
        args.seconds + 8,
    )
    result["position_start"] = started
    follow = run(
        [qmicli, "-d", selected, "--loc-follow-nmea"],
        args.seconds,
    )
    result["nmea_follow"] = {
        key: value for key, value in follow.items() if key not in ("stdout",)
    }
    lines = []
    for document in (started, follow):
        lines.extend(document.get("stdout", "").splitlines())
        lines.extend(document.get("stderr", "").splitlines())
    result["nmea"] = [line for line in lines if NMEA.fullmatch(line)][-64:]
    result["fixes"] = parse_fix(result["nmea"])
    result["fix_acquired"] = bool(result["fixes"]) and (
        started["returncode"] == 0 or follow["returncode"] in (0, 124)
    )
    stopped = run([qmicli, "-d", selected, "--loc-stop"], 12)
    result["stop"] = {
        key: value for key, value in stopped.items() if key not in ("stdout",)
    }
    result["cleanup_complete"] = stopped["returncode"] == 0
    result["engine_control_qualified"] = True
    result["pass"] = result["engine_control_qualified"] and result["fix_acquired"]
    print("RAM_GNSS_RESULT " + json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
