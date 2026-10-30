#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Switch the reviewed DWC3 controller to host briefly, then restore device."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
import time


RAM_MARKER = Path("/run/oneplus13/ram-session")
STATE = Path("/run/oneplus13/usb-role")
DEBUGFS = Path("/sys/kernel/debug")
USB_DEVICE = re.compile(r"\d+-\d+(?:\.\d+)*")


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


def usb_peripherals(root):
    """Describe attached devices without publishing serial numbers."""
    base = root / "bus/usb/devices"
    rows = []
    entries = sorted(base.iterdir()) if base.is_dir() else []
    for path in entries:
        if not USB_DEVICE.fullmatch(path.name):
            continue
        interfaces = sorted(
            item.name for item in base.glob(path.name + ":*")
        )
        drivers = []
        for item in [path] + [base / name for name in interfaces]:
            link = item / "driver"
            if link.exists():
                drivers.append(link.resolve(strict=False).name)
        def value(name):
            candidate = path / name
            if not candidate.is_file():
                return None
            text = candidate.read_text(encoding="utf-8", errors="replace").strip()
            return text[:80] or None
        rows.append({
            "path": path.name,
            "vendor_id": value("idVendor"),
            "product_id": value("idProduct"),
            "device_class": value("bDeviceClass"),
            "manufacturer": value("manufacturer"),
            "product": value("product"),
            "interfaces": interfaces[:16],
            "drivers": sorted(set(drivers)),
        })
    return rows[:32]


def inventory(root=None):
    root = Path("/sys") if root is None else Path(root)
    peripherals = usb_peripherals(root)
    drivers = {
        driver
        for row in peripherals
        for driver in row["drivers"]
    }
    return {
        "usb_devices": sorted(
            path.name for path in (root / "bus/usb/devices").glob("*")
        )[:64],
        "xhci_platform_devices": sorted(
            path.name
            for path in (root / "bus/platform/drivers/xhci-hcd").glob("*")
        )[:16],
        "udc": sorted(path.name for path in (root / "class/udc").glob("*")),
        "usb_peripherals": peripherals,
        "usb_storage_bound": "usb-storage" in drivers,
        "usb_hid_bound": "usbhid" in drivers,
    }


def wait_for_host_driver(seconds, sleep=time.sleep):
    deadline = time.monotonic() + seconds
    facts = inventory()
    samples = 1
    while time.monotonic() < deadline:
        facts = inventory()
        samples += 1
        if facts["usb_storage_bound"] or facts["usb_hid_bound"]:
            return facts, samples
        sleep(0.5)
    return facts, samples


def storage_partitions(root=Path("/sys/class/block")):
    """Return bounded block-partition names without assuming a device letter."""
    rows = []
    for path in sorted(Path(root).glob("sd*")):
        name = path.name
        if not re.fullmatch(r"sd[a-z][0-9]+", name):
            continue
        if not (path / "partition").is_file() or not (path / "dev").is_file():
            continue
        try:
            size_sectors = int((path / "size").read_text().strip())
        except (OSError, ValueError):
            continue
        if not 1 <= size_sectors:
            continue
        rows.append({
            "device": "/dev/" + name,
            "size_sectors": size_sectors,
        })
    return rows[:8]


def storage_read_only_probe(
    run=subprocess.run,
    partitions=storage_partitions,
    temporary_root=Path("/run/oneplus13"),
):
    """Mount the first usable partition read-only and hash a bounded file."""
    rows = partitions()
    attempts = []
    for row in rows:
        with tempfile.TemporaryDirectory(
            dir=temporary_root, prefix="usb-mount-"
        ) as mountpoint:
            mounted = run(
                ["mount", "-o", "ro,nosuid,nodev,noexec", row["device"], mountpoint],
                capture_output=True,
                text=True,
                timeout=12,
                check=False,
            )
            attempt = {
                "device": row["device"],
                "mount_returncode": mounted.returncode,
                "read_pass": False,
            }
            if mounted.returncode == 0:
                read_payload = None
                try:
                    import hashlib

                    candidates = []
                    for path in Path(mountpoint).rglob("*"):
                        if len(candidates) >= 8:
                            break
                        try:
                            if path.is_file() and not path.is_symlink():
                                candidates.append(path)
                        except OSError:
                            continue
                    if candidates:
                        payload = candidates[0].read_bytes()[:4096]
                        attempt.update(
                            read_bytes=len(payload),
                            read_sha256=hashlib.sha256(payload).hexdigest(),
                        )
                        read_payload = payload
                finally:
                    unmounted = run(
                        ["umount", mountpoint],
                        capture_output=True,
                        text=True,
                        timeout=12,
                        check=False,
                    )
                    attempt["unmount_returncode"] = unmounted.returncode
                attempt["read_pass"] = bool(
                    read_payload is not None and unmounted.returncode == 0
                )
            attempts.append(attempt)
            if attempt["read_pass"]:
                break
    return {
        "partitions": rows,
        "attempts": attempts,
        "read_only_io_pass": any(row["read_pass"] for row in attempts),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait-seconds", type=int, default=75)
    args = parser.parse_args()
    if not 3 <= args.wait_seconds <= 120:
        parser.error("--wait-seconds must be between 3 and 120")
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
        result["host_inventory"], result["host_inventory_samples"] = (
            wait_for_host_driver(args.wait_seconds)
        )
        result["host_peripheral_receipt"] = bool(
            result["host_inventory"]["usb_peripherals"]
        )
        if result["host_inventory"]["usb_storage_bound"]:
            result["storage_read_only"] = storage_read_only_probe()
        result["hid_input_present"] = bool(
            result["host_inventory"]["usb_hid_bound"]
            and list(Path("/dev/input").glob("event*"))
        )
        result["host_peripheral_i_o_qualified"] = bool(
            result.get("storage_read_only", {}).get("read_only_io_pass")
            or result["hid_input_present"]
        )
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
        result["functional_pass"] = bool(
            result["pass"] and result["host_peripheral_i_o_qualified"]
        )
        (STATE / "result.json").write_text(
            json.dumps(result, sort_keys=True) + "\n", encoding="utf-8"
        )
        print("RAM_USB_ROLE_RESULT " + json.dumps(result, sort_keys=True), flush=True)
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
