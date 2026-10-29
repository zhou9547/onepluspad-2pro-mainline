#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Load, transmit through and unload the reviewed OnePlus 13 IR driver."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time


POLICY = Path("/etc/modprobe.d/91-oneplus13-unreviewed-peripherals.conf")
RAM_MARKER = Path("/run/oneplus13/ram-session")
MODULE = "ir_dodge_spi"


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(args, timeout=8):
    return subprocess.run(
        args, capture_output=True, text=True, timeout=timeout, check=False
    )


def allow_module():
    if not RAM_MARKER.is_file():
        raise RuntimeError("Protected phone RAM session required")
    text = POLICY.read_text(encoding="utf-8")
    denied = (
        "blacklist " + MODULE,
        "install " + MODULE + " /bin/false",
    )
    if any(text.splitlines().count(line) != 1 for line in denied):
        raise ValueError("Exact IR module deny policy is absent")
    lines = [line for line in text.splitlines() if line not in denied]
    POLICY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def devices():
    result = []
    for path in sorted(Path("/sys/class/rc").glob("rc[0-9]*")):
        result.append(
            {
                "name": path.name,
                "driver": (path / "device/driver").resolve(strict=False).name
                if (path / "device/driver").exists()
                else None,
                "device": str(path.resolve(strict=False)),
                "protocols": (path / "protocols").read_text().strip()
                if (path / "protocols").is_file()
                else None,
            }
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy-sha256", required=True)
    parser.add_argument("--transmit", action="store_true")
    args = parser.parse_args()
    before_policy = sha256(POLICY)
    if before_policy != args.policy_sha256:
        raise ValueError("Module policy hash mismatch")
    allow_module()
    result = {
        "scope": "ONEPLUS13_RAM_SPI_INFRARED_CONTROL",
        "policy_sha256_before": before_policy,
        "policy_sha256_after": sha256(POLICY),
        "driver_loaded": False,
        "rc_device_present": False,
        "transmit_syscall_pass": False,
        "optical_output_qualified": False,
        "cleanup_complete": False,
    }
    load = run(["modprobe", "--ignore-install", MODULE], timeout=15)
    result["load"] = {
        "returncode": load.returncode,
        "stdout": load.stdout[-2048:],
        "stderr": load.stderr[-2048:],
    }
    if load.returncode:
        print("RAM_IR_RESULT " + json.dumps(result, sort_keys=True))
        raise SystemExit(1)
    result["driver_loaded"] = Path("/sys/module", MODULE).is_dir()
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        rows = devices()
        selected = [
            row for row in rows if row["driver"] == "ir-dodge-spi"
        ]
        if selected:
            break
        time.sleep(0.25)
    result["devices"] = rows
    result["selected"] = selected
    result["rc_device_present"] = bool(selected)
    pass_ = result["driver_loaded"] and result["rc_device_present"]
    if args.transmit and selected:
        lirc = "/dev/lirc0"
        pattern = Path("/run/oneplus13-ir-check.lirc")
        pattern.parent.mkdir(parents=True, exist_ok=True)
        pattern.write_text(
            "carrier 38000\n"
            "duty_cycle 33\n"
            "pulse 560\n"
            "space 560\n"
            "pulse 560\n"
            "space 1690\n",
            encoding="ascii",
        )
        transmit = run(
            [
                "ir-ctl",
                "-d",
                lirc,
                "-c",
                "38000",
                "-D",
                "33",
                "-s",
                str(pattern),
            ],
            timeout=15,
        )
        result["transmit"] = {
            "returncode": transmit.returncode,
            "stdout": transmit.stdout[-2048:],
            "stderr": transmit.stderr[-2048:],
        }
        result["transmit_syscall_pass"] = transmit.returncode == 0
        pass_ = pass_ and result["transmit_syscall_pass"]
    unload = run(["modprobe", "-r", MODULE], timeout=15)
    result["unload"] = {
        "returncode": unload.returncode,
        "stdout": unload.stdout[-2048:],
        "stderr": unload.stderr[-2048:],
    }
    cleanup = not Path("/sys/module", MODULE).exists() and not any(
        row["driver"] == "ir-dodge-spi" for row in devices()
    )
    result["cleanup_complete"] = unload.returncode == 0 and cleanup
    result["pass"] = pass_ and result["cleanup_complete"]
    print("RAM_IR_RESULT " + json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
