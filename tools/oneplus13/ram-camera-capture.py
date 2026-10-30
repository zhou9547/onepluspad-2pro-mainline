#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Capture one real S5KJN5 C-PHY frame from an isolated RAM boot."""

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import time
from pathlib import Path


STATE = Path("/run/oneplus13/camera-capture")
FRAME = STATE / "frame-sgbgr10.raw"
POLICY = Path(
    "/etc/modprobe.d/91-oneplus13-unreviewed-peripherals.conf"
)
AUDIO_HELPER = Path("/usr/libexec/oneplus13-ram-audio-check.py")
WIDTH = 4096
HEIGHT = 3072
# CAMSS vfe_formats_rdi_845 exports SGBRG10P for SGBRG10_1X10.
# Four 10-bit pixels occupy five bytes; this is not unpacked GB10.
MIN_BYTES = WIDTH * HEIGHT * 5 // 4
VFE_ENTITY = "msm_vfe1_rdi0"
VIDEO_ENTITY = "msm_vfe1_video0"
PROGRESS = STATE / "progress.json"


def progress(stage, **facts):
    """Leave a bounded checkpoint that an independent host sender can collect."""
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    value = {"stage": stage, "utc": time.time(), **facts}
    temporary = PROGRESS.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, sort_keys=True) + "\n")
    temporary.replace(PROGRESS)


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


def policy_without_camera_denials(text, module_names):
    """Remove only deny pairs for the reviewed camera dependency closure."""
    if len(module_names) > 64 or any(
        not re.fullmatch(r"[A-Za-z0-9_+-]+", name) for name in module_names
    ):
        raise ValueError("Unsafe camera module dependency closure")
    denied = {
        line
        for name in module_names
        for line in (
            "blacklist " + name,
            "install " + name + " /bin/false",
        )
    }
    return "\n".join(
        line for line in text.splitlines() if line not in denied
    ) + "\n"


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
    observed = {}
    for path in sorted(Path("/dev").glob("media*")):
        result = run(["media-ctl", "--device", path, "--print-topology"])
        entities = parse_media(result.stdout)
        observed[str(path)] = sorted(entities)
        required = {"msm_csiphy1", "msm_csid1", VFE_ENTITY, VIDEO_ENTITY}
        sensor = [
            name for name in entities if name.startswith("s5kjn5 ")
        ]
        if required.issubset(entities) and len(sensor) == 1:
            matches.append((path, entities, sensor[0]))
    if len(matches) != 1:
        raise ValueError(f"Expected one S5KJN5 media graph, found {len(matches)}; observed={observed}")
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
        "pixel_format": "V4L2_PIX_FMT_SGBRG10P",
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
    module_root = Path("/usr/lib/modules") / args.release
    spec = importlib.util.spec_from_file_location(
        "camera_module_order", AUDIO_HELPER
    )
    audio = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audio)
    ordered = audio.module_order(
        (module_root / "modules.dep").read_text(), list(modules)
    )
    original_policy = POLICY.read_bytes()
    POLICY.write_text(
        policy_without_camera_denials(
            original_policy.decode(), ordered
        ),
        encoding="utf-8",
    )
    report["module_closure"] = ordered
    report["policy_sha256_before"] = hashlib.sha256(
        original_policy
    ).hexdigest()
    try:
        for module in ordered:
            progress("module-load", module=module)
            if module_loaded(module):
                continue
            run(["modprobe", "--ignore-install", module], timeout=20)
            loaded.append(module)
        progress("media-discovery")
        device = None
        until = time.monotonic() + 12
        while time.monotonic() < until:
            try:
                device, entities, sensor = find_media()
                break
            except (OSError, RuntimeError, ValueError):
                report["media_inventory"] = {
                    str(path): run(["media-ctl", "--device", path, "--print-topology"], check=False).stdout[-32768:]
                    for path in Path("/dev").glob("media*")
                }
                time.sleep(0.25)
        if device is None:
            raise ValueError("Linux CAMSS media graph did not appear")
        report.update(
            media_device=str(device),
            sensor_entity=sensor,
            entities=sorted(entities),
        )
        progress("media-discovered", media_device=str(device),
                 entities=sorted(entities))
        set_link(device, sensor, 0, "msm_csiphy1", 0)
        set_link(device, "msm_csiphy1", 1, "msm_csid1", 0)
        set_link(device, "msm_csid1", 1, VFE_ENTITY, 0)
        progress("links-enabled")
        for entity, pads in (
            (sensor, (0,)),
            ("msm_csiphy1", (0, 1)),
            ("msm_csid1", (0, 1)),
            (VFE_ENTITY, (0, 1)),
        ):
            for pad in pads:
                progress("format", entity=entity, pad=pad)
                set_format(device, entity, pad)
        video = entity_node(entities, VIDEO_ENTITY)
        run(
            [
                "v4l2-ctl",
                "--device",
                video,
                f"--set-fmt-video=width={WIDTH},height={HEIGHT},pixelformat=pGAA",
            ]
        )
        selected = run(["v4l2-ctl", "--device", video, "--get-fmt-video"]).stdout
        report["negotiated_format"] = selected
        if (not re.search(r"Width/Height\s*:\s*4096/3072", selected)
                or not re.search(r"Pixel Format\s*:\s*'pGAA'", selected)):
            raise ValueError("Capture format was coerced away from reviewed packed RAW10")
        progress("stream-start", video=video)
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
        progress("stream-finished", returncode=result.returncode)
        if result.returncode:
            raise ValueError("V4L2 capture failed")
        report["pixels"] = validate_frame(FRAME)
        report["frame_verified"] = True
    finally:
        progress("cleanup")
        for module in reversed(loaded):
            unload(module)
        POLICY.write_bytes(original_policy)
        os.chmod(POLICY, 0o644)
        report["policy_sha256_after"] = hashlib.sha256(
            POLICY.read_bytes()
        ).hexdigest()
        report["policy_restored"] = (
            report["policy_sha256_after"] == report["policy_sha256_before"]
        )
        report["modules_unloaded"] = not any(
            module_loaded(module) for module in loaded
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
            report["policy_restored"]
            and report["modules_unloaded"]
            and report["media_graph_removed"]
        )
        (STATE / "result.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        progress("finished", cleanup_pass=report["cleanup_pass"],
                 frame_verified=report["frame_verified"])
        print("CAMERA_CAPTURE_RESULT " + json.dumps(report, sort_keys=True))
    if not report["frame_verified"] or not report["cleanup_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
