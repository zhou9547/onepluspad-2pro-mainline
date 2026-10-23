#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Calibrate an experimental packaging DTB from PRIVATE local stock evidence.

Offline only. No ADB, fastboot, stock uploads, partition writes or flash command.
Uses Android libufdt for a positive stock control before touching the candidate.
The output remains PRIVATE and is not a hardware bootability certificate.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile

from stock import Fdt, boot_image, bounded, cells, dtbo_entries, split_dtbs, strings


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


def boot_index(text, name):
    matches = re.findall(r'^androidboot\.' + re.escape(name) + r'\s*=\s*"([0-9]+)"\s*$', text, re.M)
    if len(matches) != 1:
        raise ValueError(f'Missing or ambiguous actual {name}; refusing a reference-device index')
    return int(matches[0])


class Ufdt:
    def __init__(self, path):
        self.lib = ctypes.CDLL(str(path.resolve()))
        self.lib.ufdt_apply_overlay.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                                                 ctypes.c_void_p, ctypes.c_size_t]
        self.lib.ufdt_apply_overlay.restype = ctypes.c_void_p
        self.lib.dto_free.argtypes = [ctypes.c_void_p]
        self.lib.dto_free.restype = None

    def apply(self, base, overlay):
        base_buffer = ctypes.create_string_buffer(base)
        overlay_buffer = ctypes.create_string_buffer(overlay)
        result = self.lib.ufdt_apply_overlay(base_buffer, len(base), overlay_buffer, len(overlay))
        if not result:
            raise ValueError('libufdt rejected overlay application')
        try:
            header = ctypes.string_at(result, 40)
            size = struct.unpack('>I', header[4:8])[0]
            if size < 40 or size > 64 * 1024 * 1024:
                raise ValueError('libufdt returned unreasonable FDT length')
            blob = ctypes.string_at(result, size)
            Fdt(blob)
            return blob
        finally:
            self.lib.dto_free(result)


class UfdtTool:
    def __init__(self, path):
        self.path = path.resolve()

    def apply(self, base, overlay):
        with tempfile.TemporaryDirectory(prefix='oneplus13-ufdt-') as temp:
            root = Path(temp)
            (root / 'base.dtb').write_bytes(base)
            (root / 'overlay.dtbo').write_bytes(overlay)
            subprocess.run([str(self.path), str(root / 'base.dtb'),
                            str(root / 'overlay.dtbo'), str(root / 'merged.dtb')],
                           check=True, timeout=30, capture_output=True)
            blob = (root / 'merged.dtb').read_bytes()
            Fdt(blob)
            return blob


def selected_panel(cmdline):
    # Capture only the DT node name; never retain PanelSN or factory identifiers.
    result = re.findall(r'(?:^|\s)msm_drm\.dsi_display0=(qcom,[a-zA-Z0-9_,.-]+):', cmdline)
    if len(result) != 1:
        raise ValueError('Missing or ambiguous active panel selection')
    return '/soc/qcom,mdss_mdp@ae00000/' + result[0]


def compare_subtree(actual, control, root):
    paths = [p for p in actual.nodes if p == root or p.startswith(root + '/')]
    if not paths:
        raise ValueError('Expected stock control subtree is absent')
    failures = []
    for path in paths:
        for key, value in actual.nodes[path].items():
            if control.nodes.get(path, {}).get(key) != value:
                failures.append(path + ':' + key)
    for path in control.nodes:
        if (path == root or path.startswith(root + '/')) and path not in actual.nodes:
            failures.append(path + ':unexpected-control-node')
    if failures:
        raise ValueError('Stock positive control mismatch: ' + ', '.join(failures[:5]))
    return {'nodes': len(paths), 'properties': sum(len(actual.nodes[p]) for p in paths)}


def prepare_sink(mainline, bases, entries, identity):
    container, sink, phandle = '/oneplus13-abl', '/oneplus13-abl/overlay-sink', 0x40000000
    if container in mainline.nodes or phandle in mainline.phandles:
        raise ValueError('Packaging sink conflicts with input')
    union = set()
    for tree in bases:
        union.update(tree.nodes.get('/__symbols__', {}))
    for entry in entries:
        tree = entry['tree']
        union.update(tree.nodes.get('/__fixups__', {}))
        for path, props in tree.nodes.items():
            if path.count('/') == 1 and path.startswith('/fragment@'):
                if 'target-path' in props:
                    raise ValueError('Absolute overlay target cannot be isolated in the packaging sink')
                if 'target' not in props:
                    raise ValueError('Missing overlay fragment target')
    for key in ('qcom,msm-id', 'qcom,board-id'):
        if key not in identity.nodes['/']:
            raise ValueError('Missing selected stock base identity: ' + key)
        mainline.nodes['/'][key] = identity.nodes['/'][key]
    mainline.nodes[container] = {'status': b'disabled\0'}
    mainline.nodes[sink] = {'phandle': struct.pack('>I', phandle),
                            'linux,phandle': struct.pack('>I', phandle)}
    symbols = mainline.nodes.setdefault('/__symbols__', {})
    # Stock names must all resolve to the inert sink, never real mainline devices.
    for name in union:
        symbols[name] = sink.encode() + b'\0'
    return mainline.to_blob(), len(union)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stock', required=True, type=Path)
    ufdt_args = parser.add_mutually_exclusive_group(required=True)
    ufdt_args.add_argument('--libufdt', type=Path)
    ufdt_args.add_argument('--ufdt-tool', type=Path, help='Host ufdt-apply executable, including 32-bit Windows')
    parser.add_argument('--mainline-dtb', type=Path)
    parser.add_argument('--output', required=True, type=Path, help='New PRIVATE directory outside Git')
    args = parser.parse_args()
    import importlib.util
    spec = importlib.util.spec_from_file_location('collector', Path(__file__).with_name('collect-stock.py'))
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    out = collector.private_destination(args.output)
    out.mkdir(parents=True, exist_ok=True)
    runtime = Fdt((args.stock / 'runtime.dtb').read_bytes())
    config = (args.stock / 'bootconfig.txt').read_text()
    base_index, overlay_index = boot_index(config, 'dtb_idx'), boot_index(config, 'dtbo_idx')
    image = (args.stock / 'vendor_boot.img').read_bytes()
    geometry = boot_image(image)
    off, size = geometry['sections']['dtb']
    bases = split_dtbs(bounded(image, off, size))
    entries = dtbo_entries((args.stock / 'dtbo.img').read_bytes())
    if base_index >= len(bases) or overlay_index >= len(entries):
        raise ValueError('Actual boot index is outside stock table')
    ufdt = Ufdt(args.libufdt) if args.libufdt else UfdtTool(args.ufdt_tool)
    merged = ufdt.apply(bases[base_index].blob, entries[overlay_index]['tree'].blob)
    control = Fdt(merged)
    panel = selected_panel((args.stock / 'cmdline.txt').read_text())
    checks = {panel: compare_subtree(runtime, control, panel)}
    touch = [p for p, props in runtime.nodes.items()
             if props.get('compatible') == b'synaptics,tcm-spi-hbp\0' and props.get('status') == b'okay\0']
    if len(touch) != 1:
        raise ValueError('Missing or ambiguous active touch controller')
    checks[touch[0]] = compare_subtree(runtime, control, touch[0])
    # DTBO root properties are selection metadata, not fragment contents.
    # libufdt merges fragments only. This bootloader exposes the selected
    # overlay's identity at runtime; verify that independently, byte-for-byte.
    identity_checks = {}
    for key in ('qcom,msm-id', 'qcom,board-id'):
        expected = entries[overlay_index]['tree'].nodes['/'].get(key)
        if expected is None:
            expected = control.nodes['/'].get(key)
        if runtime.nodes['/'].get(key) != expected:
            raise ValueError('Stock root identity mismatch: ' + key)
        identity_checks[key] = 'runtime matches selected DTBO root metadata'
    soc_pairs = cells(entries[overlay_index]['tree'].nodes['/']['qcom,msm-id'])
    selected_soc = cells(bases[base_index].nodes['/']['qcom,msm-id'])
    if len(selected_soc) != 2 or tuple(selected_soc) not in list(zip(soc_pairs[::2], soc_pairs[1::2])):
        raise ValueError('Selected stock base SoC is absent from selected overlay identity')
    (out / 'stock-positive-control.dtb').write_bytes(merged)
    report = {'status': 'OFFLINE_STOCK_CONTROL_ONLY', 'hardware_tested': False,
              'base_index': base_index, 'overlay_index': overlay_index,
              'base_count': len(bases), 'overlay_count': len(entries),
              'base_sha256': digest(bases[base_index].blob),
              'overlay_sha256': digest(entries[overlay_index]['tree'].blob),
              'runtime_sha256': digest(runtime.blob), 'stock_control': checks,
              'identity_checks': identity_checks,
              'panel': panel, 'touch': touch[0]}
    if args.mainline_dtb:
        original = Fdt(args.mainline_dtb.read_bytes())
        candidate, count = prepare_sink(original, bases, entries, bases[base_index])
        # ALL stock table entries must merge, and no operational node may change.
        final = Fdt(candidate)
        protected = {p: props for p, props in final.nodes.items()
                     if not p.startswith('/oneplus13-abl/') and p != '/__symbols__'}
        merged_hashes = []
        for entry in entries:
            test = Fdt(ufdt.apply(candidate, entry['tree'].blob))
            for path, props in protected.items():
                if test.nodes.get(path) != props:
                    raise ValueError('Overlay escaped disabled sink into ' + path)
            escaped = set(test.nodes) - set(final.nodes)
            if any(not p.startswith('/oneplus13-abl/overlay-sink/') for p in escaped):
                raise ValueError('Overlay created operational nodes outside disabled sink')
            merged_hashes.append(digest(test.blob))
        (out / 'sm8750-oneplus-dodge-abl.dtb').write_bytes(candidate)
        report['candidate'] = {'sha256': digest(candidate), 'symbols': count,
                               'all_overlay_merged_sha256': merged_hashes,
                               'sink': '/oneplus13-abl/overlay-sink', 'requires_hardware_validation': True}
    (out / 'calibration.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Offline stock positive control passed; no device boot or flash was attempted.')


if __name__ == '__main__':
    main()
