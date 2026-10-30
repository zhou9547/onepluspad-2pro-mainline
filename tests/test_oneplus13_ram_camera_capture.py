# SPDX-License-Identifier: GPL-2.0-only
import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/oneplus13"))
capture = importlib.import_module("ram-camera-capture")


TOPOLOGY = """
- entity 1: s5kjn5 1-002d (1 pad, 1 link)
  device node name /dev/v4l-subdev0
  pad0: Source
- entity 2: msm_csiphy1 (2 pads, 2 links)
  device node name /dev/v4l-subdev1
  pad0: Sink
  pad1: Source
- entity 3: msm_csid1 (2 pads, 2 links)
  device node name /dev/v4l-subdev2
  pad0: Sink
  pad1: Source
- entity 4: msm_vfe1_rdi0 (2 pads, 2 links)
  device node name /dev/v4l-subdev3
  pad0: Sink
  pad1: Source
- entity 5: msm_vfe1_video0 (1 pad, 1 link)
  device node name /dev/video7
  pad0: Sink
"""


class CameraCaptureRuntime(unittest.TestCase):
    def test_media_parser_selects_video_node(self):
        entities = capture.parse_media(TOPOLOGY)
        self.assertEqual(set(entities), {
            "s5kjn5 1-002d",
            "msm_csiphy1",
            "msm_csid1",
            "msm_vfe1_rdi0",
            "msm_vfe1_video0",
        })
        self.assertEqual(capture.entity_node(entities, "msm_vfe1_video0"),
                         "/dev/video7")
        self.assertEqual(entities["msm_csiphy1"]["pads"], {0, 1})

    def test_vfe_subdevice_is_not_the_capture_device(self):
        entities = capture.parse_media(TOPOLOGY)
        with self.assertRaises(ValueError):
            capture.entity_node(entities, "msm_vfe1_rdi0")

    def test_raw10_uses_packed_four_pixel_five_byte_layout(self):
        self.assertEqual(capture.MIN_BYTES, 15728640)

    def test_frame_validation_rejects_uniform_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "frame.raw"
            path.write_bytes(b"\0" * capture.MIN_BYTES)
            with self.assertRaises(ValueError):
                capture.validate_frame(path)

    def test_frame_validation_accepts_varied_pixels(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "frame.raw"
            path.write_bytes(bytes(range(256)) * (capture.MIN_BYTES // 256))
            report = capture.validate_frame(path)
            self.assertEqual(report["bytes"], capture.MIN_BYTES)
            self.assertGreaterEqual(report["sampled_unique_values"], 8)

    def test_camera_policy_removes_only_reviewed_dependency_denials(self):
        text = "\n".join(
            (
                "# policy",
                "blacklist mc",
                "install mc /bin/false",
                "blacklist unrelated",
                "install unrelated /bin/false",
            )
        ) + "\n"
        changed = capture.policy_without_camera_denials(text, ["mc"])
        self.assertNotIn("blacklist mc\n", changed)
        self.assertNotIn("install mc /bin/false\n", changed)
        self.assertIn("blacklist unrelated\n", changed)
        self.assertIn("install unrelated /bin/false\n", changed)

    def test_camera_policy_rejects_oversized_or_unsafe_closure(self):
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            capture.policy_without_camera_denials(
                "", ["safe", "../unsafe"]
            )
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            capture.policy_without_camera_denials(
                "", ["module" + str(index) for index in range(65)]
            )


if __name__ == "__main__":
    unittest.main()
