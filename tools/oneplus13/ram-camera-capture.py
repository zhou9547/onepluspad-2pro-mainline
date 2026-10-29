#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Capture one real S5KJN5 C-PHY frame from an isolated RAM boot."""

import argparse
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path


STATE = Path("/run/oneplus13/camera-capture")
FRAME = STATE / "frame-sgbgr10.raw"
WIDTH = 4096
HEIGHT = 3072
MIN_BYTES = WIDTH * HEIGHT * 2


def run(command, timeout=20, check=True):
    result = subprocess.run(
        [str(item) for item in command],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if check and result.returncode:
        raise RuntimeError(
            f"command failed ({result.returncode}): "
            f"{' '.join(map(str, command))}: {result.stderr.strip()}"
        )
    return result


def module_loaded(name):
    return Path("/sys/module", name.replace("-", "_")).is_dir()


def unload(name):
    if module_loaded(name):
        run(["modprobe", "--remove", name], timeout=15, check=False)


def parse_media(output):
    entities = {}
    current = None
    for line in output.splitlines():
        match = re.match(r"^- entity \d+: (.+?)(?: \(\d+ pads?.*)?$", line)
        if match:
            current = match.group(1).strip('"')
            entities[current] = {"nodes": [], "pads": set()}
            continue
        if current is None:
            continue
        match = re.match(r"^\s+device node name (.+)$", line)
        if match:
            entities[current]["nodes"].append(match.group(1).strip())
            continue
        match = re.match(r"^\s+pad(\d+):", line)
        if match:
            entities[current]["pads"].add(int(match.group(1)))
    return entities


def find_media():
    matches = []
    for path in sorted(Path("/dev").glob("media*")):
        result = run(["media-ctl", "--device", path, "--print-topology"])
        entities = parse_media(result.stdout)
        required = {"msm_csiphy1", "msm_csid1", "msm_vfe1"}
        sensor = [
            name for name in entities if name.startswith("s5kjn5 ")
        ]
        if required.issubset(entities) and len(sensor) == 1:
            matches.append((path, entities, sensor[0]))
    if len(matches) != 1:
        raise ValueError(f"Expected one S5KJN5 media graph, found {len(matches)}")
    return matches[0]


def entity_node(entities, name):
    nodes = entities[name]["nodes"]
    videos = [node for node in nodes if node.startswith("/dev/video")]
    if len(videos) != 1:
        raise ValueError(f"Expected one video node for {name}: {nodes}")
    return videos[0]


def set_link(device, source, source_pad, sink, sink_pad):
    run(
        [
            "media-ctl",
            "--device",
            device,
            "--link",
            f'"{source}":{source_pad} -> "{sink}":{sink_pad}[1]',
        ]
    )


def set_format(device, entity, pad):
    run(
        [
            "media-ctl",
            "--device",
            device,
            "--set-v4l2",
            (
                f'"{entity}":{pad}'
                f"[fmt:SGBRG10_1X10/{WIDTH}x{HEIGHT} field:none]"
            ),
        ]
    )


def validate_frame(path):
    size = path.stat().st_size
    if size < MIN_BYTES:
        raise ValueError(f"Short frame: {size} < {MIN_BYTES}")
    data = path.read_bytes()[:MIN_BYTES]
    samples = data[:65536]
    unique = len(set(samples))
    low = min(samples)
    high = max(samples)
    if unique < 8 or high - low < 8:
        raise ValueError(
            f"Implausible camera pixels: unique={unique} range={low}-{high}"
        )
    return {
        "bytes": size,
        "sampled_bytes": len(samples),
        "sampled_unique_values": unique,
        "sampled_min": low,
        "sampled_max": high,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True)
    parser.add_argument("--frame-timeout", type=int, default=25)
    args = parser.parse_args()
    if os.geteuid() != 0 or os.uname().release != args.release:
        raise ValueError("Wrong camera root/kernel")
    if not Path("/run/oneplus13/ram-session").is_file():
        raise ValueError("Protected RAM session required")
    if not re.search(r"^overlay / overlay ", Path("/proc/mounts").read_text(), re.M):
        raise ValueError("RAM overlay required")
    for path in Path("/sys/class/block").iterdir():
        if (
            not path.name.startswith(("ram", "zram", "loop"))
            and (path / "ro").read_text().strip() != "1"
        ):
            raise ValueError("Writable physical storage")
    cmdline = set(Path("/proc/cmdline").read_text().split())
    if "oneplus13.camera_capture=1" not in cmdline:
        raise ValueError("Wrong camera alternative boot")
    for unit in ("oneplus13-ram-guard.service", "oneplus13-ram-deadline.timer"):
        status = run(
            ["systemctl", "show", unit, "-p", "ActiveState", "--value"]
        ).stdout.strip()
        if status != "active":
            raise ValueError(f"Required RAM safety unit is not active: {unit}")

    STATE.mkdir(mode=0o700, exist_ok=False)
    loaded = []
    report = {
        "scope": "REAL_S5KJN5_CPHY_FRAME",
        "width": WIDTH,
        "height": HEIGHT,
        "pixel_format": "V4L2_PIX_FMT_SGBRG10",
        "frame_verified": False,
        "cleanup_pass": False,
    }
    modules = (
        "camcc_sm8750",
        "cambistmclkcc_sm8750",
        "phy_qcom_mipi_csi2",
        "i2c_qcom_cci",
        "s5kjn5",
        "qcom_camss",
    )
    try:
        for module in modules:
            run(["modprobe", "--ignore-install", module], timeout=20)
            loaded.append(module)
        device = None
        until = time.monotonic() + 12
        while time.monotonic() < until:
            try:
                device, entities, sensor = find_media()
                break
            except (OSError, RuntimeError, ValueError):
                time.sleep(0.25)
        if device is None:
            raise ValueError("Linux CAMSS media graph did not appear")
        report.update(
            media_device=str(device),
            sensor_entity=sensor,
            entities=sorted(entities),
        )
        set_link(device, sensor, 0, "msm_csiphy1", 0)
        set_link(device, "msm_csiphy1", 1, "msm_csid1", 0)
        set_link(device, "msm_csid1", 1, "msm_vfe1", 0)
        for entity, pads in (
            (sensor, (0,)),
            ("msm_csiphy1", (0, 1)),
            ("msm_csid1", (0, 1)),
            ("msm_vfe1", (0, 1)),
        ):
            for pad in pads:
                set_format(device, entity, pad)
        video = entity_node(entities, "msm_vfe1")
        run(
            [
                "v4l2-ctl",
                "--device",
                video,
                f"--set-fmt-video=width={WIDTH},height={HEIGHT},pixelformat=GB10",
            ]
        )
        result = run(
            [
                "v4l2-ctl",
                "--device",
                video,
                "--stream-mmap=16",
                "--stream-count=1",
                f"--stream-to={FRAME}",
                f"--stream-poll",
            ],
            timeout=args.frame_timeout,
            check=False,
        )
        report["stream_returncode"] = result.returncode
        report["stream_stdout"] = result.stdout[-2000:]
        report["stream_stderr"] = result.stderr[-4000:]
        if result.returncode:
            raise ValueError("V4L2 capture failed")
        report["pixels"] = validate_frame(FRAME)
        report["frame_verified"] = True
    finally:
        for module in reversed(loaded):
            unload(module)
        report["modules_unloaded"] = not any(
            module_loaded(module) for module in modules
        )
        report["media_graph_removed"] = not any(
            "msm_vfe1"
            in run(
                ["media-ctl", "--device", path, "--print-topology"],
                check=False,
            ).stdout
            for path in Path("/dev").glob("media*")
        )
        report["cleanup_pass"] = (
            report["modules_unloaded"] and report["media_graph_removed"]
        )
        (STATE / "result.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("CAMERA_CAPTURE_RESULT " + json.dumps(report, sort_keys=True))
    if not report["frame_verified"] or not report["cleanup_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
