#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import unittest


PATH = Path(__file__).resolve().parents[1] / "tools/oneplus13/ram-gnss-check.py"
SPEC = importlib.util.spec_from_file_location("ram_gnss", PATH)
GNSS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GNSS)


class GnssNmeaTests(unittest.TestCase):
    def test_rmc_and_gga_fix_are_parsed(self):
        fixes = GNSS.parse_fix(
            [
                "$GNRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A",
                "$GNGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47",
            ]
        )
        self.assertEqual([row["type"] for row in fixes], ["RMC", "GGA"])
        self.assertAlmostEqual(fixes[0]["latitude"], 48.1173)
        self.assertAlmostEqual(fixes[0]["longitude"], 11.5166667)
        self.assertEqual(fixes[1]["satellites"], 8)

    def test_invalid_quality_is_ignored(self):
        self.assertEqual(
            GNSS.parse_fix(
                ["$GNGGA,123519,4807.038,N,01131.000,E,0,00,99.9,545.4,M,46.9,M,,*64"]
            ),
            [],
        )

    def test_malformed_and_non_nmea_lines_are_ignored(self):
        self.assertEqual(
            GNSS.parse_fix(
                [
                    "not nmea",
                    "$GNRMC,123519,A,48,N,01131.000,E,,,*00",
                    "$GPGGA,1,2,3*ZZ",
                ]
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
