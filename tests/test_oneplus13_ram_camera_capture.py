# SPDX-License-Identifier: GPL-2.0-only
import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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
    def test_kprobe_trace_start_stop_keeps_mode_and_returns_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp)
            (trace / "kprobe_events").write_text("")
            (trace / "tracing_on").write_text("0\n")
            (trace / "trace").write_text("")
            for suffix in ("stream_enter", "stream_exit", "csid_irq",
                           "vfe_irq", "vfe_buf_done", "cphy_irq"):
                event = trace / "events/kprobes" / ("oneplus13_" + suffix)
                event.mkdir(parents=True)
                (event / "enable").write_text("0\n")
            with mock.patch.object(capture, "Path", return_value=trace):
                started = capture.stream_trace_start()
            for name in started["state"]["created"]:
                self.assertEqual(
                    (trace / "events/kprobes" / name / "enable").read_text(), "1\n"
                )
            (trace / "trace").write_text(
                "worker-1 [000] 1.0: oneplus13_stream_enter: (sensor)\n"
                "worker-1 [000] 1.1: oneplus13_stream_exit: (sensor) ret=-110\n"
            )
            report = capture.stream_trace_stop(started)
            self.assertEqual(report["mode"], "kprobe")
            self.assertEqual(report["counts"], {"stream_enter": 1, "stream_exit": 1})
            self.assertEqual((trace / "tracing_on").read_text(), "0\n")
            self.assertTrue(report["cleanup_pass"])
            for name in started["state"]["created"]:
                self.assertEqual(
                    (trace / "events/kprobes" / name / "enable").read_text(), "0\n"
                )
                self.assertIn("-:kprobes/" + name + "\n",
                              (trace / "kprobe_events").read_text())

    def test_existing_camera_probe_is_not_taken_over(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp)
            original = "p:kprobes/oneplus13_stream_enter sensor\n"
            (trace / "kprobe_events").write_text(original)
            with mock.patch.object(capture, "Path", return_value=trace):
                started = capture.stream_trace_start()
            self.assertIsNone(started["state"])
            self.assertIn("already exist", started["report"]["error"])
            self.assertEqual((trace / "kprobe_events").read_text(), original)

    def test_probe_creation_appends_and_partial_enable_failure_is_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp)
            original = "p:other_group/unrelated another_symbol\n"
            (trace / "kprobe_events").write_text(original)
            (trace / "tracing_on").write_text("0\n")
            with mock.patch.object(capture, "Path", return_value=trace):
                started = capture.stream_trace_start()
            self.assertIsNone(started["state"])
            report = capture.stream_trace_stop(started)
            self.assertIn("FileNotFoundError", report["error"])
            self.assertEqual(report["created"], ["oneplus13_stream_enter"])
            self.assertTrue((trace / "kprobe_events").read_text().startswith(original))
            self.assertIn("-:kprobes/oneplus13_stream_enter\n",
                          (trace / "kprobe_events").read_text())
            self.assertNotIn("-:other_group/unrelated",
                             (trace / "kprobe_events").read_text())

    def test_probe_cleanup_keeps_trying_after_disable_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp)
            events = trace / "kprobe_events"
            events.write_text("")
            errors = capture.remove_stream_probes(trace, events, ["oneplus13_stream_enter"])
            self.assertTrue(errors)
            self.assertEqual(events.read_text(), "-:kprobes/oneplus13_stream_enter\n")

    def test_trace_read_error_still_disables_and_deletes_probes(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp)
            event = trace / "events/kprobes/oneplus13_stream_enter/enable"
            event.parent.mkdir(parents=True)
            event.write_text("1\n")
            events = trace / "kprobe_events"
            events.write_text("")
            state = {"mode": "kprobe", "trace": trace, "events": events,
                     "created": ["oneplus13_stream_enter"]}
            report = capture.stream_trace_stop(
                {"state": state, "report": {"mode": "kprobe"}}
            )
            self.assertIn("FileNotFoundError", report["error"])
            self.assertTrue(report["cleanup_pass"])
            self.assertEqual(event.read_text(), "0\n")

    def test_function_trace_fallback_still_collects_and_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = Path(tmp)
            for name, text in {"available_filter_functions": "csid_isr\nother\n",
                               "set_ftrace_filter": "", "current_tracer": "nop\n",
                               "trace": "", "tracing_on": "0\n"}.items():
                (trace / name).write_text(text)
            with mock.patch.object(capture, "Path", return_value=trace):
                started = capture.stream_trace_start()
            (trace / "trace").write_text("worker-1 [000] 1.0: csid_isr\n")
            report = capture.stream_trace_stop(started)
            self.assertEqual(report["counts"], {"csid_isr": 1})
            self.assertEqual((trace / "current_tracer").read_text(), "nop\n")
            self.assertEqual((trace / "tracing_on").read_text(), "0\n")

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
        self.assertEqual(
            capture.entity_subdev_node(entities, "s5kjn5 1-002d"),
            "/dev/v4l-subdev0",
        )

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
