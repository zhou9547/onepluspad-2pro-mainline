#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import tempfile
import unittest


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
                {"usb_devices", "xhci_platform_devices", "udc"},
            )

    def test_platform_device_mode_file_is_discovered(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            mode = root / "a600000.usb" / "mode"
            mode.parent.mkdir()
            mode.write_text("device\n", encoding="utf-8")
            self.assertEqual(USB.mode_paths(root), mode)

    def test_multiple_mode_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for parent in ("a600000.usb", "dwc3.duplicate"):
                mode = root / parent / "mode"
                mode.parent.mkdir()
                mode.write_text("device\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "found 2"):
                USB.mode_paths(root)


if __name__ == "__main__":
    unittest.main()
