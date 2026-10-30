# SPDX-License-Identifier: GPL-2.0-only
import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/oneplus13"))
capture = importlib.import_module("camera-capture-dtb")
from stock import Fdt, cells, strings


class CameraCaptureTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        blob = (
            ROOT / "devices/oneplus13/qualified-data/calibrated.dtb"
        ).read_bytes()
        cls.actual, cls.report = capture.derive(blob)
        cls.tree = Fdt(cls.actual)

    def test_phone_route_is_cphy1_csid1_vfe1(self):
        self.assertEqual(self.report["csiphy_index"], 1)
        self.assertEqual(self.report["csiphy"], capture.PHYS[1]["path"])
        self.assertEqual(self.report["csid_index"], 1)
        self.assertEqual(self.report["vfe_index"], 1)
        self.assertEqual(self.report["cphy_trios"], 3)
        self.assertEqual(self.report["link_frequency_hz"], 1_400_000_000)
        self.assertEqual(self.report["settle_count_expected"], 45)

    def test_sensor_endpoint_uses_three_cphy_trios(self):
        endpoint = self.tree.nodes[
            capture.probe.SENSOR + "/port/endpoint"
        ]
        self.assertEqual(cells(endpoint["data-lanes"]), [0, 1, 2])
        self.assertEqual(cells(endpoint["bus-type"]), [1])
        self.assertEqual(
            cells(endpoint["link-frequencies"]),
            [0, 1_400_000_000],
        )
        phy = self.tree.nodes[capture.PHYS[1]["path"]]
        self.assertEqual(
            strings(phy["compatible"]),
            ["oneplus,dodge-ultrawide-csi2-phy-experimental"],
        )

    def test_camss_has_sm8750_resources_and_full_phy_array(self):
        node = self.tree.nodes[capture.CAMSS]
        self.assertEqual(strings(node["compatible"]), ["qcom,sm8750-camss"])
        self.assertEqual(len(cells(node["reg"])), 13 * 4)
        self.assertEqual(len(strings(node["reg-names"])), 13)
        self.assertEqual(len(cells(node["clocks"])), 23 * 2)
        self.assertEqual(len(cells(node["interrupts"])), 10 * 3)
        self.assertEqual(len(strings(node["phy-names"])), 6)
        self.assertEqual(len(cells(node["phys"])), 6 * 2)
        self.assertEqual(
            cells(node["power-domains"]), [0x4000007C, 3,
                                           0x4000007C, 4,
                                           0x4000007C, 5,
                                           0x4000007C, 0]
        )

    def test_default_tree_and_qualification_remain_false(self):
        self.assertFalse(self.report["default_boot_tree_changed"])
        self.assertFalse(self.report["hardware_qualified"])
        self.assertTrue(self.report["capture_pipeline_present"])
        self.assertNotIn(
            "/soc/ftm_camera_settings/camera_0000_38E5",
            self.tree.nodes,
        )

    def test_binary_round_trip_is_stable(self):
        parsed = Fdt(self.actual)
        self.assertEqual(parsed.nodes, self.tree.nodes)
        self.assertEqual(parsed.reservations, self.tree.reservations)


if __name__ == "__main__":
    unittest.main()
