#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock


PATH = (
    Path(__file__).resolve().parents[1]
    / "tools/oneplus13/ram-usb-role-check.py"
)
SPEC = importlib.util.spec_from_file_location("ram_usb_role", PATH)
USB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(USB)


class UsbRolePathTests(unittest.TestCase):
    def test_read_write_and_inventory_shape(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "mode"
            path.write_text("device\n", encoding="utf-8")
            USB.write(path, "host")
            self.assertEqual(USB.read(path), "host")
            rows = USB.inventory()
            self.assertEqual(
                set(rows),
                {
                    "usb_devices",
                    "xhci_platform_devices",
                    "udc",
                    "usb_peripherals",
                    "usb_storage_bound",
                    "usb_hid_bound",
                },
            )

    def test_external_peripherals_exclude_interfaces_and_omit_serials(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            device = root / "bus/usb/devices/1-1"
            interface = root / "bus/usb/devices/1-1:1.0"
            driver = root / "bus/usb/drivers/usb-storage"
            for path in (
                device,
                interface,
                driver,
                root / "bus/platform/drivers/xhci-hcd",
                root / "class/udc",
            ):
                path.mkdir(parents=True)
            (device / "idVendor").write_text("abcd\n", encoding="utf-8")
            (device / "idProduct").write_text("1234\n", encoding="utf-8")
            (device / "product").write_text("Flash drive\n", encoding="utf-8")
            (device / "serial").write_text("private-serial\n", encoding="utf-8")
            (device / "driver").symlink_to(driver, target_is_directory=True)
            rows = USB.inventory(root)
            self.assertEqual([row["path"] for row in rows["usb_peripherals"]], ["1-1"])
            self.assertEqual(rows["usb_peripherals"][0]["product"], "Flash drive")
            self.assertNotIn("serial", rows["usb_peripherals"][0])
            self.assertTrue(rows["usb_storage_bound"])

    def test_platform_device_mode_file_is_discovered(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            mode = root / "usb" / "a600000.usb" / "mode"
            mode.parent.mkdir(parents=True)
            mode.write_text("device\n", encoding="utf-8")
            self.assertEqual(USB.mode_paths(root), mode)

    def test_multiple_mode_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for parent in ("usb/a600000.usb", "dwc3.duplicate"):
                mode = root / parent / "mode"
                mode.parent.mkdir(parents=True)
                mode.write_text("device\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "found 2"):
                USB.mode_paths(root)

    def test_host_driver_wait_uses_fresh_inventory(self):
        sequence = [
            {"usb_storage_bound": False, "usb_hid_bound": False},
            {"usb_storage_bound": True, "usb_hid_bound": False},
        ]
        with unittest.mock.patch.object(
            USB, "inventory", side_effect=sequence
        ) as inventory:
            facts, samples = USB.wait_for_host_driver(5, sleep=lambda _: None)
        self.assertTrue(facts["usb_storage_bound"])
        self.assertEqual(samples, 2)
        self.assertEqual(inventory.call_count, 2)

    def test_storage_probe_mounts_read_only_and_unmounts(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.write_bytes(b"usb-read-proof")
            calls = []

            def fake_run(args, **kwargs):
                calls.append(args)
                if args[0] == "mount":
                    Path(args[-1], "proof.txt").write_bytes(source.read_bytes())
                    return Mock(returncode=0, stdout="", stderr="")
                return Mock(returncode=0, stdout="", stderr="")

            result = USB.storage_read_only_probe(
                run=fake_run,
                partitions=lambda: [
                    {"device": "/dev/sda1", "size_sectors": 2048}
                ],
                temporary_root=temporary,
            )
        self.assertTrue(result["read_only_io_pass"])
        self.assertEqual(calls[0][0], "mount")
        self.assertIn("ro,nosuid,nodev,noexec", calls[0])
        self.assertEqual(calls[-1][0], "umount")


if __name__ == "__main__":
    unittest.main()
