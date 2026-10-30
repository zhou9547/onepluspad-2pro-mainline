#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch


PATH = Path(__file__).resolve().parents[1] / "tools/oneplus13/ram-gnss-check.py"
SPEC = importlib.util.spec_from_file_location("ram_gnss", PATH)
GNSS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GNSS)


def sentence(payload):
    checksum = 0
    for char in payload:
        checksum ^= ord(char)
    return "$" + payload + f"*{checksum:02X}"


class GnssNmeaTests(unittest.TestCase):
    def test_rmc_and_gga_fix_are_parsed(self):
        fixes = GNSS.parse_fix(
            [
                sentence("GNRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W"),
                sentence("GNGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,"),
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

    def test_bad_checksum_and_out_of_range_coordinates_are_not_fixes(self):
        self.assertEqual(GNSS.parse_fix([
            "$GNRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A",
            sentence("GNGGA,123519,9961.0,N,01131.0,E,1,08,0.9,1,M,1,M,,"),
            sentence("GNGGA,123519,4807.0,N,01131.0,E,1"),
            sentence("GNGGA,123519,NaN,N,01131.0,E,1,08,0.9,1,M,1,M,,"),
        ]), [])

    def test_loc_actions_separate_and_stop_reuses_client(self):
        child = Mock(returncode=0)
        child.communicate.return_value = (sentence("GNGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,"), "")
        child.poll.return_value = 0
        with patch.object(GNSS, "run", side_effect=[
            {"returncode": 0, "stdout": "CID: '7'"},
            {"returncode": 0, "stdout": "nmea types"},
            {"returncode": 0, "stdout": "engine lock"},
            {"returncode": 0, "stdout": "started"},
            {"returncode": 0, "stdout": "stopped"},
        ]) as run, patch.object(GNSS.subprocess, "Popen", return_value=child) as popen:
            result = GNSS.collect_session("qmicli", "qrtr://0", 30)
        self.assertTrue(result["fix_acquired"])
        self.assertTrue(result["cleanup_complete"])
        self.assertEqual(
            [call.args[0][-2:] for call in run.call_args_list[:3]],
            [
                ["--loc-noop", "--client-no-release-cid"],
                ["--loc-set-nmea-types=gga|rmc", "--client-no-release-cid"],
                ["--loc-set-engine-lock=none", "--client-no-release-cid"],
            ],
        )
        self.assertIn("--client-cid=7", popen.call_args.args[0])
        self.assertIn("--client-cid=7", run.call_args_list[-1].args[0])
        self.assertIn("--loc-stop", run.call_args_list[-1].args[0])
        self.assertTrue(
            all("--device-open-proxy" in call.args[0] for call in run.call_args_list)
        )
        self.assertIn("--device-open-proxy", popen.call_args.args[0])

    def test_failed_start_cannot_qualify_engine_or_start_follower(self):
        responses = [
            {"returncode": 0, "stdout": "CID: '7'"},
            {"returncode": 0},
            {"returncode": 0},
            {"returncode": 1},
            {"returncode": 1},
            {"returncode": 1},
            {"returncode": 0},
        ]
        with patch.object(GNSS, "run", side_effect=responses), patch.object(
            GNSS.time, "sleep"
        ), patch.object(GNSS.subprocess, "Popen") as popen:
            result = GNSS.collect_session("qmicli", "qrtr://0", 30)
        self.assertFalse(result["engine_control_qualified"])
        self.assertFalse(result["fix_acquired"])
        self.assertEqual(len(result["start_attempts"]), 3)
        self.assertTrue(result["cleanup_complete"])
        popen.assert_not_called()

    def test_failed_client_setup_skips_start_and_follower(self):
        with patch.object(
            GNSS, "run", return_value={"returncode": 1, "stdout": ""}
        ), patch.object(GNSS.subprocess, "Popen") as popen:
            result = GNSS.collect_session("qmicli", "qrtr://0", 30)
        self.assertFalse(result["engine_control_qualified"])
        self.assertEqual(result["start_attempts"], [])
        popen.assert_not_called()

    def test_loc_service_probe_retries_until_node_answers(self):
        responses = [
            {"returncode": 1, "stderr": "service not ready"},
            {"returncode": 1, "stderr": "service not ready"},
            {"returncode": 0, "stdout": "mode"},
        ]
        with patch.object(GNSS, "run", side_effect=responses), patch.object(
            GNSS.time, "sleep"
        ):
            selected, probes = GNSS.probe_devices(
                "qmicli", ["qrtr://0"], 5
            )
        self.assertEqual(selected, "qrtr://0")
        self.assertEqual(len(probes), 3)


if __name__ == "__main__":
    unittest.main()
