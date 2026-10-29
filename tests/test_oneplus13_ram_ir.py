#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import tempfile
import unittest


PATH = Path(__file__).resolve().parents[1] / "tools/oneplus13/ram-ir-check.py"
SPEC = importlib.util.spec_from_file_location("ram_ir_check", PATH)
IR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(IR)


class IrPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.original_policy = IR.POLICY
        self.original_marker = IR.RAM_MARKER
        IR.POLICY = root / "policy.conf"
        IR.RAM_MARKER = root / "ram-session"

    def tearDown(self):
        IR.POLICY = self.original_policy
        IR.RAM_MARKER = self.original_marker
        self.temp.cleanup()

    def test_exact_denies_are_removed(self):
        IR.RAM_MARKER.write_text("", encoding="utf-8")
        IR.POLICY.write_text(
            "blacklist ir_dodge_spi\n"
            "install ir_dodge_spi /bin/false\n"
            "blacklist unrelated\n",
            encoding="utf-8",
        )
        IR.allow_module()
        self.assertEqual(
            IR.POLICY.read_text(encoding="utf-8"),
            "blacklist unrelated\n",
        )

    def test_missing_or_ambiguous_rules_are_rejected(self):
        IR.RAM_MARKER.write_text("", encoding="utf-8")
        for value in (
            "",
            "blacklist ir_dodge_spi\n",
            "blacklist ir_dodge_spi\n"
            "install ir_dodge_spi /bin/false\n"
            "install ir_dodge_spi /bin/false\n",
        ):
            IR.POLICY.write_text(value, encoding="utf-8")
            with self.subTest(value=value), self.assertRaises(ValueError):
                IR.allow_module()

    def test_marker_is_required(self):
        IR.POLICY.write_text(
            "blacklist ir_dodge_spi\n"
            "install ir_dodge_spi /bin/false\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(RuntimeError, "RAM session"):
            IR.allow_module()


if __name__ == "__main__":
    unittest.main()
