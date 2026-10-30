#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Switch the reviewed DWC3 controller to host briefly, then restore device."""

import json
from pathlib import Path
import subprocess
import time


RAM_MARKER = Path("/run/oneplus13/ram-session")
STATE = Path("/run/oneplus13/usb-role")
DEBUGFS = Path("/sys/kernel/debug")


def ensure_debugfs():
    if not (DEBUGFS / "tracing").exists():
        mounted = subprocess.run(
            ["mount", "-t", "debugfs", "debugfs", str(DEBUGFS)],
            capture_output=True,
            text=True,
            timeout=6,
            check=False,
        )
        if mounted.returncode not in (0, 32):
            raise RuntimeError("Could not mount debugfs")


def mode_paths(root=None):
    if root is None:
        ensure_debugfs()
        root = DEBUGFS
    root = Path(root)
    rows = []
    candidates = [root / "usb/a600000.usb/mode", root / "a600000.usb/mode"]
    candidates += [path / "mode" for path in sorted(root.glob("dwc3*"))]
    candidates += [path / "mode" for path in sorted(root.glob("*/dwc3*"))]
    for mode in candidates:
        if mode.is_file():
            rows.append(mode)
    if len(rows) != 1:
        found = ",".join(str(path) for path in rows) or "none"
        raise RuntimeError(
            f"Expected one DWC3 debugfs mode file, found {len(rows)}: {found}"
        )
    return rows[0]


def read(path):
    return path.read_text(encoding="utf-8").strip()


def write(path, value):
    path.write_text(value + "\n", encoding="utf-8")


def inventory():
    return {
        "usb_devices": sorted(
            path.name for path in Path("/sys/bus/usb/devices").glob("*")
        )[:64],
        "xhci_platform_devices": sorted(
            path.name
            for path in Path("/sys/bus/platform/drivers/xhci-hcd").glob("*")
        )[:16],
        "udc": sorted(path.name for path in Path("/sys/class/udc").glob("*")),
    }


def main():
    if not RAM_MARKER.is_file():
        raise RuntimeError("Protected phone RAM session required")
    mode = mode_paths()
    before = read(mode)
    if before != "device":
        raise RuntimeError("USB must begin in device role")
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    result = {
        "scope": "ONEPLUS13_RAM_DWC3_ROLE_SWITCH",
        "mode_file": str(mode),
        "role_before": before,
        "host_role_requested": False,
        "host_inventory": None,
        "role_restored": False,
        "cleanup_complete": False,
        "host_peripheral_receipt": False,
    }
    try:
        write(mode, "host")
        result["host_role_requested"] = True
        time.sleep(3)
        result["role_after_host_request"] = read(mode)
        result["host_role_verified"] = result["role_after_host_request"] == "host"
        result["host_inventory"] = inventory()
    finally:
        write(mode, "device")
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            result["role_after_restore"] = read(mode)
            if result["role_after_restore"] == "device" and inventory()["udc"]:
                result["role_restored"] = True
                break
            time.sleep(0.25)
        result["cleanup_inventory"] = inventory()
        result["cleanup_complete"] = bool(result["role_restored"])
        result["pass"] = bool(
            result["host_role_requested"] and result.get("host_role_verified", False)
            and result["role_restored"]
        )
        (STATE / "result.json").write_text(
            json.dumps(result, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("RAM_USB_ROLE_RESULT " + json.dumps(result, sort_keys=True), flush=True)
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
