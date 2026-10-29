#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import gzip
import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest


PATH = (
    Path(__file__).resolve().parents[1]
    / "tools/oneplus13/ram-modem-gnss-check.py"
)
SPEC = importlib.util.spec_from_file_location("ram_modem", PATH)
MODEM = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODEM)


class ModemFirmwareInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.original_marker = MODEM.RAM_MARKER
        self.original_firmware = MODEM.FIRMWARE_ROOT
        MODEM.RAM_MARKER = self.root / "ram-session"
        MODEM.FIRMWARE_ROOT = self.root / "firmware"
        MODEM.FIRMWARE_ROOT.mkdir()
        MODEM.RAM_MARKER.write_text("", encoding="utf-8")
        self.archive = self.root / "modem.tar.gz"
        self.review = self.root / "review.json"
        self.files = {
            "modem.mdt": b"metadata",
            "modem.b00": b"segment",
            "modem_dtb.mdt": b"dtb metadata",
            "modem_dtb.b00": b"dtb segment",
            "modemr.jsn": b"{}",
        }
        with tarfile.open(self.archive, "w:gz") as archive:
            for name, value in self.files.items():
                info = tarfile.TarInfo("qcom/sm8750/oneplus/dodge/" + name)
                info.size = len(value)
                archive.addfile(info, io.BytesIO(value))
        self.review.write_text(
            MODEM.json.dumps(
                {
                    "firmware_sha256": {
                        "modem.mdt": hashlib.sha256(b"metadata").hexdigest(),
                        "modem.b00": hashlib.sha256(b"segment").hexdigest(),
                        "modem_dtb.mdt": hashlib.sha256(b"dtb metadata").hexdigest(),
                        "modem_dtb.b00": hashlib.sha256(b"dtb segment").hexdigest(),
                    },
                    "resource_json_sha256": hashlib.sha256(b"{}").hexdigest(),
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        MODEM.RAM_MARKER = self.original_marker
        MODEM.FIRMWARE_ROOT = self.original_firmware
        self.temp.cleanup()

    def test_safe_archive_installs_exact_reviewed_files(self):
        digest = MODEM.sha256(self.archive)
        result = MODEM.install_firmware(self.archive, self.review, digest)
        self.assertEqual(result["file_count"], 5)
        self.assertEqual(
            (MODEM.FIRMWARE_ROOT / "qcom/sm8750/oneplus/dodge/modem.mdt").read_bytes(),
            b"metadata",
        )

    def test_archive_hash_and_ram_marker_are_required(self):
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            MODEM.install_firmware(self.archive, self.review, "0" * 64)
        MODEM.RAM_MARKER.unlink()
        with self.assertRaisesRegex(RuntimeError, "RAM session"):
            MODEM.install_firmware(
                self.archive, self.review, MODEM.sha256(self.archive)
            )

    def test_review_mismatch_is_rejected(self):
        review = MODEM.json.loads(self.review.read_text())
        review["firmware_sha256"]["modem.b00"] = "0" * 64
        self.review.write_text(MODEM.json.dumps(review), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs"):
            MODEM.install_firmware(
                self.archive, self.review, MODEM.sha256(self.archive)
            )


if __name__ == "__main__":
    unittest.main()
