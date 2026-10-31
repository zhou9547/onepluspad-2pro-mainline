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
TPG_FRAME = STATE / "frame-tpg-sgbgr10.raw"
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
DEBUG_CPHY_MODULE = Path("/run/oneplus13/core/phy-qcom-mipi-csi2.ko")
DEBUG_CAMSS_MODULE = Path("/run/oneplus13/core/qcom-camss.ko")
DEBUG_SENSOR_MODULE = Path("/run/oneplus13/core/s5kjn5.ko")


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


def entity_subdev_node(entities, name):
    nodes = entities[name]["nodes"]
    subdevs = [
        node for node in nodes if node.startswith("/dev/v4l-subdev")
    ]
    if len(subdevs) != 1:
        raise ValueError(
            f"Expected one V4L2 subdevice node for {name}: {nodes}"
        )
    return subdevs[0]


def module_diagnostics(module_names):
    rows = {}
    for name in module_names:
        root = Path("/sys/module") / name.replace("-", "_")
        drivers = []
        for path in sorted((root / "drivers").glob("*")):
            drivers.append(path.name)
        rows[name] = {
            "loaded": root.is_dir(),
            "drivers": drivers[:16],
        }
    buses = {}
    for bus in ("i2c", "platform", "spi"):
        base = Path("/sys/bus") / bus / "drivers"
        buses[bus] = sorted(
            path.name for path in base.glob("*")
            if any(token in path.name.lower() for token in (
                "camss", "csiphy", "mipi", "cci", "s5k", "ir-dodge"
            ))
        )[:32] if base.is_dir() else []
    return {"modules": rows, "matching_drivers": buses}


def camss_probe_trace():
    """Capture return values while retrying CAMSS probe after module load."""
    trace = Path("/sys/kernel/debug/tracing")
    events = trace / "kprobe_events"
    driver = Path("/sys/bus/platform/drivers/qcom-camss")
    device = Path("/sys/bus/platform/devices/ad27000.isp")
    if not events.is_file() or not (driver / "bind").is_file() or not device.is_dir():
        return {"available": False}
    names = (
        "camss_probe", "camss_icc_get", "camss_configure_pd",
        "camss_init_subdevices", "dma_set_mask_and_coherent",
        "camss_parse_ports", "camss_register_entities",
        "camss_link_entities",
    )
    reserved = {"oneplus13_" + name for name in names}
    if any(
        line.split()[0].split(":", 1)[-1].split("/")[-1] in reserved
        for line in events.read_text().splitlines() if line.split()
    ):
        return {"available": True, "cleanup_pass": False,
                "error": "CAMSS trace probes already exist"}
    created = []
    report = {"available": True, "created": created}
    try:
        for name in names:
            event = "oneplus13_" + name
            with events.open("a") as stream:
                stream.write(f"r:{event} {name} ret=$retval\n")
            created.append(event)
            (trace / "events/kprobes" / event / "enable").write_text("1\n")
        (trace / "trace").write_text("")
        (trace / "tracing_on").write_text("1\n")
        if not Path("/sys/bus/platform/devices/ad27000.isp/driver").exists():
            (driver / "bind").write_text(device.name + "\n")
        time.sleep(2)
        (trace / "tracing_on").write_text("0\n")
        output = (trace / "trace").read_text()
        report.update({
            "driver_bound": Path(
                "/sys/bus/platform/devices/ad27000.isp/driver"
            ).exists(),
            "trace": [line for line in output.splitlines()
                      if "oneplus13_" in line][-128:],
        })
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)
    finally:
        errors = remove_stream_probes(trace, events, created)
        report["cleanup_pass"] = not errors
        if errors:
            report["cleanup_errors"] = errors
    return report


def restore_function_trace(state):
    """Attempt every restoration even when an earlier write fails."""
    errors = []
    for path, value in (
        (state["trace"] / "tracing_on", "0\n"),
        (state["tracer"], state["previous"] + "\n"),
        (state["selector"], ""),
    ):
        try:
            path.write_text(value)
        except OSError as error:
            errors.append(str(error))
    return errors


def stream_trace_start():
    trace = Path("/sys/kernel/debug/tracing")
    events = trace / "kprobe_events"
    if not events.is_file():
        available = trace / "available_filter_functions"
        selector = trace / "set_ftrace_filter"
        tracer = trace / "current_tracer"
        if not (available.is_file() and selector.is_file() and tracer.is_file()):
            return None
        names = {
            "s5kjn5_enable_streams", "csid_isr", "vfe_isr",
            "vfe_buf_done", "dodge_cphy_irq",
        }
        functions = [
            line.split()[0]
            for line in available.read_text().splitlines()
            if line.split() and line.split()[0] in names
        ]
        if not functions:
            return None
        previous = tracer.read_text().strip()
        selected = [line for line in selector.read_text().splitlines()
                    if line.strip() and not line.startswith("#")]
        if previous != "nop" or selected:
            return {"state": None, "report": {"available": True,
                    "mode": "function", "cleanup_pass": False,
                    "error": "Function tracer is already owned"}}
        state = {"mode": "function", "trace": trace, "tracer": tracer,
                 "selector": selector, "previous": previous}
        try:
            selector.write_text("\n".join(functions) + "\n")
            (trace / "trace").write_text("")
            tracer.write_text("function\n")
            (trace / "tracing_on").write_text("1\n")
        except OSError as error:
            errors = restore_function_trace(state)
            return {
                "state": None,
                "report": {
                    "available": True,
                    "mode": "function",
                    "error": type(error).__name__ + ": " + str(error),
                    "cleanup_pass": not errors,
                    "cleanup_errors": errors,
                },
            }
        return {
            "state": {
                "mode": "function",
                "trace": trace,
                "tracer": tracer,
                "selector": selector,
                "previous": previous,
            },
            "report": {
                "available": True,
                "mode": "function",
                "functions": functions,
            },
        }
    original = events.read_text()
    entries = (
        ("stream_enter", "s5kjn5_enable_streams", "p"),
        ("stream_exit", "s5kjn5_enable_streams", "r"),
        ("csid_irq", "csid_isr", "p"),
        ("vfe_irq", "vfe_isr", "p"),
        ("vfe_buf_done", "vfe_buf_done", "p"),
        ("cphy_irq", "dodge_cphy_irq", "p"),
    )
    # kprobe_events creates disabled events. Enable each event explicitly;
    # tracing_on alone does not produce a single probe sample.
    reserved = {"oneplus13_" + suffix for suffix, _, _ in entries}
    if any(
        line.split()[0].split(":", 1)[-1].split("/")[-1] in reserved
        for line in original.splitlines() if line.split()
    ):
        return {
            "state": None,
            "report": {"available": True, "mode": "kprobe",
                       "error": "Camera trace probes already exist"},
        }
    created = []
    try:
        for suffix, symbol, kind in entries:
            name = "oneplus13_" + suffix
            line = f"{kind}:{name} {symbol}"
            if kind == "r":
                line += " ret=$retval"
            line += "\n"
            try:
                with events.open("a") as stream:
                    stream.write(line)
            except OSError:
                continue
            created.append(name)
            (trace / "events/kprobes" / name / "enable").write_text("1\n")
        if not created:
            raise OSError("No camera trace probe could be created")
        (trace / "trace").write_text("")
        (trace / "tracing_on").write_text("1\n")
    except OSError as error:
        cleanup_errors = remove_stream_probes(trace, events, created)
        return {
            "state": None,
            "report": {
                "available": True,
                "error": type(error).__name__ + ": " + str(error),
                "created": created,
                "cleanup_errors": cleanup_errors,
                "cleanup_pass": not cleanup_errors,
            },
        }
    return {
        "state": {
            "mode": "kprobe",
            "trace": trace,
            "events": events,
            "created": created,
        },
        "report": {
            "available": True,
            "mode": "kprobe",
            "created": created,
        },
    }


def remove_stream_probes(trace, events, created):
    """Remove only this capture's events, retaining unrelated kprobes."""
    errors = []
    try:
        (trace / "tracing_on").write_text("0\n")
    except OSError as error:
        errors.append(str(error))
    for name in reversed(created):
        try:
            (trace / "events/kprobes" / name / "enable").write_text("0\n")
        except OSError as error:
            errors.append(str(error))
        try:
            with events.open("a") as stream:
                stream.write("-:kprobes/" + name + "\n")
        except OSError as error:
            errors.append(str(error))
    return errors


def stream_trace_stop(started):
    if not started:
        return {"available": False}
    state = started["state"]
    report = dict(started["report"])
    if not state:
        return report
    trace = state["trace"]
    if state["mode"] == "function":
        try:
            (trace / "tracing_on").write_text("0\n")
            lines = [
                line for line in (trace / "trace").read_text().splitlines()
                if re.search(r"\s(" + "|".join(re.escape(name) for name in report["functions"]) + r")\s*$", line)
            ]
            counts = {}
            for line in lines:
                match = re.search(r"\s([^\s]+)\s*$", line)
                if match:
                    counts[match.group(1)] = counts.get(match.group(1), 0) + 1
            report["counts"] = counts
            report["lines"] = lines[-128:]
        except OSError as error:
            report["error"] = type(error).__name__ + ": " + str(error)
        finally:
            errors = restore_function_trace(state)
            report["cleanup_pass"] = not errors
            if errors:
                report["cleanup_errors"] = errors
        return report
    try:
        (trace / "tracing_on").write_text("0\n")
        lines = [
            line for line in (trace / "trace").read_text().splitlines()
            if "oneplus13_" in line
        ]
        counts = {}
        for line in lines:
            match = re.search(r": oneplus13_([^:]+):", line)
            if match:
                counts[match.group(1)] = counts.get(match.group(1), 0) + 1
        report["counts"] = counts
        report["lines"] = lines[-128:]
    except OSError as error:
        report["error"] = type(error).__name__ + ": " + str(error)
    finally:
        errors = remove_stream_probes(trace, state["events"], state["created"])
        report["cleanup_pass"] = not errors
        if errors:
            report["cleanup_errors"] = errors
    return report


def set_link(device, source, source_pad, sink, sink_pad, enabled=True):
    run(
        [
            "media-ctl",
            "--device",
            device,
            "--link",
            (
                f'"{source}":{source_pad} -> "{sink}":{sink_pad}'
                f'[{1 if enabled else 0}]'
            ),
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


def accept_sensor_frame(report, path, primary_attempt):
    """A validated RDI sensor frame can qualify after the primary RDI fails."""
    fallback = any(item.get("frame_verified") is True
                   for item in report.get("rdi_fallbacks", []))
    if not fallback and (primary_attempt["returncode"]
                         or "VIDIOC_STREAMON returned" in primary_attempt["stderr"]):
        raise ValueError("V4L2 capture failed")
    # TPG output is kept in a separate file and never qualifies this path.
    report["pixels"] = validate_frame(path)
    report["frame_verified"] = True


def cleanup_capture(loaded, original_policy):
    report = {}
    cleanup_errors = []
    for module in reversed(loaded):
        try:
            unload(module)
        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
            cleanup_errors.append("module:" + module + ":" + type(error).__name__)
    try:
        POLICY.write_bytes(original_policy)
        os.chmod(POLICY, 0o644)
    except OSError as error:
        cleanup_errors.append("policy:" + type(error).__name__)
    try:
        report["policy_sha256_after"] = hashlib.sha256(POLICY.read_bytes()).hexdigest()
        report["policy_restored"] = POLICY.read_bytes() == original_policy
    except OSError as error:
        report["policy_restored"] = False
        cleanup_errors.append("policy-readback:" + type(error).__name__)
    report["modules_unloaded"] = not any(
        module_loaded(module) for module in loaded
    )
    try:
        report["media_graph_removed"] = not any(
            "msm_vfe1" in run(
                ["media-ctl", "--device", path, "--print-topology"],
                check=False,
            ).stdout for path in Path("/dev").glob("media*")
        )
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        report["media_graph_removed"] = False
        cleanup_errors.append("media:" + type(error).__name__)
    report["cleanup_errors"] = cleanup_errors
    report["cleanup_pass"] = (
        not cleanup_errors
        and report["policy_restored"]
        and report["modules_unloaded"]
        and report["media_graph_removed"]
    )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", required=True)
    parser.add_argument("--frame-timeout", type=int, default=25)
    parser.add_argument(
        "--sensor-test-pattern",
        type=int,
        default=-1,
        help="Optionally select a sensor test pattern before streaming",
    )
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
            if (
                module == "phy_qcom_mipi_csi2"
                and DEBUG_CPHY_MODULE.is_file()
            ):
                run(
                    ["insmod", str(DEBUG_CPHY_MODULE)],
                    timeout=20,
                )
            elif module == "qcom_camss" and DEBUG_CAMSS_MODULE.is_file():
                run(
                    ["insmod", str(DEBUG_CAMSS_MODULE)],
                    timeout=20,
                )
            elif module == "s5kjn5" and DEBUG_SENSOR_MODULE.is_file():
                run(
                    ["insmod", str(DEBUG_SENSOR_MODULE)],
                    timeout=20,
                )
            else:
                run(["modprobe", "--ignore-install", module], timeout=20)
            loaded.append(module)
        report["module_diagnostics"] = module_diagnostics(ordered)
        report["module_dmesg"] = run(
            ["dmesg"], timeout=8, check=False
        ).stdout[-24000:]
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
            report["camss_probe_trace"] = camss_probe_trace()
            report["module_dmesg_after_retry"] = run(
                ["dmesg"], timeout=8, check=False
            ).stdout[-16000:]
            report["failure_media_inventory"] = {
                str(path): run(
                    ["media-ctl", "--device", path, "--print-topology"],
                    check=False,
                ).stdout[-32768:]
                for path in Path("/dev").glob("media*")
            }
            raise ValueError("Linux CAMSS media graph did not appear")
        report.update(
            media_device=str(device),
            sensor_entity=sensor,
            entities=sorted(entities),
            topology=run(
                ["media-ctl", "--device", device, "--print-topology"],
                check=False,
            ).stdout[-32768:],
        )
        progress("media-discovered", media_device=str(device),
                 entities=sorted(entities))
        set_link(device, "msm_csiphy1", 1, "msm_csid1", 0)
        set_link(device, "msm_csid1", 1, VFE_ENTITY, 0)
        progress("links-enabled")
        for entity, pads in (
            ("msm_csiphy1", (0, 1)),
            ("msm_csid1", (0, 1)),
            (VFE_ENTITY, (0, 1)),
        ):
            for pad in pads:
                progress("format", entity=entity, pad=pad)
                set_format(device, entity, pad)
        report["post_format_topology"] = run(
            ["media-ctl", "--device", device, "--print-topology"],
            check=False,
        ).stdout[-32768:]
        time.sleep(0.25)
        sensor_video = entity_subdev_node(entities, sensor)
        report["sensor_controls"] = run(
            ["v4l2-ctl", "--device", sensor_video, "--list-ctrls"],
            check=False,
        ).stdout[-8000:]
        if args.sensor_test_pattern >= 0:
            pattern = run(
                [
                    "v4l2-ctl",
                    "--device",
                    sensor_video,
                    f"--set-ctrl=test_pattern={args.sensor_test_pattern}",
                ],
                check=False,
            )
            report["sensor_test_pattern"] = {
                "returncode": pattern.returncode,
                "stdout": pattern.stdout[-2000:],
                "stderr": pattern.stderr[-2000:],
            }
            report["sensor_controls_after_test_pattern"] = run(
                ["v4l2-ctl", "--device", sensor_video, "--list-ctrls"],
                check=False,
            ).stdout[-8000:]
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
        stream_trace = stream_trace_start()
        if stream_trace and stream_trace["report"].get("cleanup_pass") is False:
            report["stream_trace"] = stream_trace_stop(stream_trace)
            raise RuntimeError("Camera trace ownership or setup cleanup is unproven")
        progress("stream-start", video=video)
        try:
            attempts = []
            for attempt in range(3):
                if attempt:
                    time.sleep(0.75)
                command = [
                    "v4l2-ctl",
                    "--device",
                    video,
                    "--stream-mmap=16",
                    "--stream-count=1",
                    f"--stream-to={FRAME}",
                    "--stream-poll",
                ]
                before_irq = Path("/proc/interrupts").read_text()
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                time.sleep(2)
                during_irq = Path("/proc/interrupts").read_text()
                try:
                    stdout, stderr = process.communicate(
                        timeout=args.frame_timeout
                    )
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    stderr += "\nv4l2-ctl process timeout\n"
                attempts.append({
                    "attempt": attempt + 1,
                    "returncode": process.returncode,
                    "stdout": stdout[-2000:],
                    "stderr": stderr[-4000:],
                    "frame_bytes": FRAME.stat().st_size
                    if FRAME.exists() else 0,
                    "interrupts_before": [
                        line for line in before_irq.splitlines()
                        if (
                            re.match(r"^\s*(426|436|478|603):", line)
                            or re.search(
                                r"camss|csid|csiphy|vfe|mipi|cphy|adab000",
                                line,
                                re.I,
                            )
                        )
                    ],
                    "interrupts_during": [
                        line for line in during_irq.splitlines()
                        if (
                            re.match(r"^\s*(426|436|478|603):", line)
                            or re.search(
                                r"camss|csid|csiphy|vfe|mipi|cphy|adab000",
                                line,
                                re.I,
                            )
                        )
                    ],
                    "interrupts_all_during": during_irq[-16000:],
                })
                if (
                    process.returncode == 0
                    and "VIDIOC_STREAMON returned" not in stderr
                    and FRAME.is_file()
                    and FRAME.stat().st_size >= MIN_BYTES
                ):
                    break
        finally:
            report["stream_trace"] = stream_trace_stop(stream_trace)
        report["stream_attempts"] = attempts
        report["stream_returncode"] = attempts[-1]["returncode"]
        report["stream_stdout"] = attempts[-1]["stdout"]
        report["stream_stderr"] = attempts[-1]["stderr"]
        report["post_stream_dmesg"] = run(
            ["dmesg"], timeout=8, check=False
        ).stdout[-16000:]
        sensor_frame_ready = (
            FRAME.is_file() and FRAME.stat().st_size >= MIN_BYTES
        )
        if not sensor_frame_ready:
            variants = []
            report["rdi_fallbacks"] = variants
            for pad, vfe_entity, video_entity in (
                (2, "msm_vfe1_rdi1", "msm_vfe1_video1"),
                (3, "msm_vfe1_rdi2", "msm_vfe1_video2"),
            ):
                variant_frame = STATE / f"frame-rdi{pad - 1}.raw"
                variant = {
                    "rdi_index": pad - 1,
                    "frame": str(variant_frame),
                    "attempts": [],
                }
                variants.append(variant)
                try:
                    set_link(
                        device, "msm_csid1", 1, VFE_ENTITY, 0,
                        enabled=False,
                    )
                    if pad > 2:
                        set_link(
                            device, "msm_csid1", pad - 1,
                            f"msm_vfe1_rdi{pad - 2}", 0,
                            enabled=False,
                        )
                    set_link(
                        device, "msm_csid1", pad, vfe_entity, 0,
                        enabled=True,
                    )
                    set_format(device, "msm_csid1", pad)
                    set_format(device, vfe_entity, 0)
                    set_format(device, vfe_entity, 1)
                    variant_video = entity_node(entities, video_entity)
                    run(
                        [
                            "v4l2-ctl",
                            "--device",
                            variant_video,
                            (
                                f"--set-fmt-video=width={WIDTH},"
                                f"height={HEIGHT},pixelformat=pGAA"
                            ),
                        ]
                    )
                    for attempt in range(2):
                        if attempt:
                            time.sleep(0.75)
                        variant_result = run(
                            [
                                "v4l2-ctl",
                                "--device",
                                variant_video,
                                "--stream-mmap=16",
                                "--stream-count=1",
                                f"--stream-to={variant_frame}",
                                "--stream-poll",
                            ],
                            timeout=args.frame_timeout,
                            check=False,
                        )
                        variant["attempts"].append({
                            "attempt": attempt + 1,
                            "returncode": variant_result.returncode,
                            "stdout": variant_result.stdout[-2000:],
                            "stderr": variant_result.stderr[-4000:],
                            "frame_bytes": variant_frame.stat().st_size
                            if variant_frame.exists() else 0,
                        })
                        if (
                            variant_result.returncode == 0
                            and "VIDIOC_STREAMON returned"
                            not in variant_result.stderr
                            and variant_frame.is_file()
                            and variant_frame.stat().st_size >= MIN_BYTES
                        ):
                            break
                    if (
                        variant_frame.is_file()
                        and variant_frame.stat().st_size >= MIN_BYTES
                    ):
                        variant["pixels"] = validate_frame(variant_frame)
                        variant["frame_verified"] = True
                        FRAME.write_bytes(variant_frame.read_bytes())
                        sensor_frame_ready = True
                        break
                except Exception as error:
                    variant["error"] = (
                        type(error).__name__ + ": " + str(error)
                    )
        if not sensor_frame_ready:
            tpg_report = {"attempts": []}
            report["tpg_fallback"] = tpg_report
            try:
                if "rdi_fallbacks" in report:
                    try:
                        set_link(
                            device, "msm_csid1", 3,
                            "msm_vfe1_rdi2", 0, enabled=False,
                        )
                    except RuntimeError:
                        pass
                set_link(
                    device, "msm_csiphy1", 1, "msm_csid1", 0,
                    enabled=False,
                )
                set_link(
                    device, "msm_tpg1", 0, "msm_csid1", 0,
                    enabled=True,
                )
                set_link(
                    device, "msm_csid1", 1, VFE_ENTITY, 0,
                    enabled=True,
                )
                set_format(device, "msm_tpg1", 0)
                tpg_video = entity_subdev_node(entities, "msm_tpg1")
                tpg_control = run(
                    [
                        "v4l2-ctl",
                        "--device",
                        tpg_video,
                        "--set-ctrl=test_pattern=5",
                    ],
                    check=False,
                )
                tpg_report["control"] = {
                    "returncode": tpg_control.returncode,
                    "stdout": tpg_control.stdout[-2000:],
                    "stderr": tpg_control.stderr[-2000:],
                }
                run(
                    [
                        "v4l2-ctl",
                        "--device",
                        video,
                        (
                            f"--set-fmt-video=width={WIDTH},"
                            f"height={HEIGHT},pixelformat=pGAA"
                        ),
                    ]
                )
                for attempt in range(2):
                    if attempt:
                        time.sleep(0.75)
                    tpg_result = run(
                        [
                            "v4l2-ctl",
                            "--device",
                            video,
                            "--stream-mmap=16",
                            "--stream-count=1",
                            f"--stream-to={TPG_FRAME}",
                            "--stream-poll",
                        ],
                        timeout=args.frame_timeout,
                        check=False,
                    )
                    tpg_report["attempts"].append({
                        "attempt": attempt + 1,
                        "returncode": tpg_result.returncode,
                        "stdout": tpg_result.stdout[-2000:],
                        "stderr": tpg_result.stderr[-4000:],
                        "frame_bytes": TPG_FRAME.stat().st_size
                        if TPG_FRAME.exists() else 0,
                    })
                    if (
                        tpg_result.returncode == 0
                        and "VIDIOC_STREAMON returned" not in tpg_result.stderr
                        and TPG_FRAME.is_file()
                        and TPG_FRAME.stat().st_size >= MIN_BYTES
                    ):
                        break
                if (
                    TPG_FRAME.is_file()
                    and TPG_FRAME.stat().st_size >= MIN_BYTES
                ):
                    tpg_report["pixels"] = validate_frame(TPG_FRAME)
                    tpg_report["frame_verified"] = True
            except Exception as error:
                tpg_report["error"] = type(error).__name__ + ": " + str(error)
        progress("stream-finished", returncode=attempts[-1]["returncode"])
        accept_sensor_frame(report, FRAME, attempts[-1])
    finally:
        progress("cleanup")
        report.update(cleanup_capture(loaded, original_policy))
        report["cleanup_pass"] &= (
            report.get("stream_trace", {}).get("cleanup_pass", True)
            and report.get("camss_probe_trace", {}).get("cleanup_pass", True)
        )
        (STATE / "result.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        progress("finished", cleanup_pass=report["cleanup_pass"],
                 frame_verified=report["frame_verified"])
        print("CAMERA_CAPTURE_RESULT " + json.dumps(report, sort_keys=True))
        print(
            "CAMERA_CAPTURE_SUMMARY "
            + json.dumps(
                {
                    "cleanup_pass": report["cleanup_pass"],
                    "frame_verified": report["frame_verified"],
                    "sensor_test_pattern": report.get("sensor_test_pattern"),
                    "sensor_controls_after_test_pattern": report.get(
                        "sensor_controls_after_test_pattern"
                    ),
                    "stream_attempts": report.get("stream_attempts"),
                    "rdi_fallbacks": report.get("rdi_fallbacks"),
                    "tpg_fallback": report.get("tpg_fallback"),
                    "post_stream_dmesg": [
                        line
                        for line in report.get(
                            "post_stream_dmesg", ""
                        ).splitlines()
                        if re.search(
                            r"camss|csiphy|csid|vfe|s5kjn5|phy|"
                            r"timeout|failed|error|warning",
                            line,
                            re.I,
                        )
                    ][-80:],
                },
                sort_keys=True,
            )
        )
    if not report["frame_verified"] or not report["cleanup_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
