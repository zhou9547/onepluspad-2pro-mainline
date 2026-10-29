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
- entity 4: msm_vfe1 (2 pads, 1 link)
  device node name /dev/v4l-subdev3
  device node name /dev/video7
  pad0: Sink
  pad1: Source
"""


class CameraCaptureRuntime(unittest.TestCase):
    def test_media_parser_selects_video_node(self):
        entities = capture.parse_media(TOPOLOGY)
        self.assertEqual(set(entities), {
            "s5kjn5 1-002d",
            "msm_csiphy1",
            "msm_csid1",
            "msm_vfe1",
        })
        self.assertEqual(capture.entity_node(entities, "msm_vfe1"),
                         "/dev/video7")
        self.assertEqual(entities["msm_csiphy1"]["pads"], {0, 1})

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


if __name__ == "__main__":
    unittest.main()
