# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
import json
import pathlib
import stat
import struct
import sys
import tempfile
import unittest

TOOLS = pathlib.Path(__file__).resolve().parents[1] / 'tools/oneplus13'
sys.path.insert(0, str(TOOLS))
from common import boot_sections, make_cpio, read_cpio
from verify import check_config, REQUIRED
from stock import Fdt, boot_image, split_dtbs
from calibrate import boot_index, selected_panel, prepare_sink, calibrate_memory, compare_subtree
from panel import command_packets, pps_summary, vendor_pps
from spr import parse_xml as parse_spr, register_plan as spr_plan
from dsc import decode_pps, pack_pps
spec = importlib.util.spec_from_file_location('phone_stock_collector', TOOLS / 'collect-stock.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)
spec = importlib.util.spec_from_file_location('phone_panel_generator', TOOLS / 'generate-panel.py')
panel_generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel_generator)


class PhoneFormats(unittest.TestCase):
    def test_panel_generated_header_matches_public_fixture(self):
        root = TOOLS.parents[1]
        fixture = json.loads((root / 'devices/oneplus13/panel-aa569-120hz.json').read_text())
        header = (root / 'devices/oneplus13/kernel/panel-aa569/aa569-data.h').read_text()
        self.assertEqual(panel_generator.generate(fixture), header)

    def test_panel_generator_rejects_transport_or_payload_changes(self):
        root = TOOLS.parents[1]
        original = (root / 'devices/oneplus13/panel-aa569-120hz.json').read_text()
        for key, value in [('type', 5), ('channel', 1), ('vendor_flags', 128),
                           ('last', 1), ('delay_ms', 999), ('payload', 'ff5aa506')]:
            fixture = json.loads(original)
            fixture['on_packets'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                panel_generator.generate(fixture)

    @staticmethod
    def synthetic_spr():
        # Deliberately synthetic coefficients; never embed the owner's XML.
        fields = {'AdaptiveMode': 'YYGM', 'FilterType': '2DAvg',
                  'FilterCoeffs': ','.join(str(i-8) for i in range(16)),
                  'PhaseInc': '7', 'PhaseRepeat': '3',
                  'ColorPhaseOffsetsRed': '-1,1,0,0,0,0',
                  'ColorPhaseOffsetsGreen': '0,0,0,0,0,0',
                  'ColorPhaseOffsetsBlue': '1,-1,0,0,0,0',
                  'ColorPhaseOffsetsWhite': '0,0,0,0,0,0',
                  'AdaptiveFilterCoeffs': '1,2,3,4,5',
                  'FilterWidth': '0', 'SharpeningStrength': '0', 'Pba': '1,2,3,0,1,2,3'}
        return ('<Calib_Data><SprConfig NumModes="1" DefaultMode="0"><Mode ModeID="0">' +
                ''.join(f'<{k}>{v}</{k}>' for k, v in fields.items()) +
                '</Mode></SprConfig></Calib_Data>').encode()

    def test_spr_enum_pba_and_signed_register_packing(self):
        default, modes = parse_spr(self.synthetic_spr())
        cfg = modes[default]
        self.assertEqual((cfg['cfg7'], cfg['cfg8']), (4, 0))
        self.assertEqual(cfg['cfg18'], [1, 2, 3, 0, 2, 4, 0])
        plan = {op['relative_offset']: op for op in spr_plan(cfg)}
        self.assertEqual(plan[0x24]['values'][0], 0x3f)
        self.assertEqual(plan[0x34]['values'][0], 0x07f907f8)
        self.assertEqual(plan[0x7c]['values'][0], 0x03210210)
        self.assertEqual(plan[4]['values'][0], 0x05379107)
        self.assertEqual(plan[4]['preserve_mask'], 1 << 25)
        self.assertEqual(plan[8]['values'], [1])
        self.assertNotIn(0x54, plan)  # absent in the pinned vendor SPR2 path
        self.assertEqual(plan[0xa0]['values'][-1] >> 16, 4095)
        with self.assertRaises(ValueError):
            spr_plan(cfg, mixers=1)

    def test_spr_rejects_silent_truncation_and_unknown_profiles(self):
        xml = self.synthetic_spr()
        cases = [xml.replace(b'-1,1,0,0,0,0', b'-17,1,0,0,0,0'),
                 xml.replace(b'<PhaseInc>7', b'<PhaseInc>16'),
                 xml.replace(b'<Pba>1,2,3,0,1,2,3', b'<Pba>1,2,3,0,1,2,4'),
                 xml.replace(b'<FilterType>2DAvg', b'<FilterType>Unknown'),
                 xml.replace(b'<FilterWidth>0', b'<FilterWidth>1'),
                 xml.replace(b'<ColorPhaseOffsetsWhite>0,0,0,0,0,0',
                             b'<ColorPhaseOffsetsWhite>0,0,1,0,0,0'),
                 xml.replace(b'NumModes="1"', b'NumModes="2"'),
                 xml.replace(b'DefaultMode="0"', b'DefaultMode="1"'),
                 xml.replace(b'</Mode>', b'<PhaseInc>1</PhaseInc></Mode>'),
                 b'<!DOCTYPE x>'+xml]
        for bad in cases:
            with self.subTest(bad=bad[:100]), self.assertRaises(ValueError):
                parse_spr(bad)

    def test_native_panel_pps_uses_422_group_bpp_not_rgb(self):
        fixture = json.loads((TOOLS.parents[1] / 'devices/oneplus13/panel-aa569-120hz.json').read_text())
        pps = pps_summary(fixture['on_packets'])
        self.assertTrue(pps['native_422'])
        self.assertFalse(pps['convert_rgb'])
        self.assertEqual((pps['width'], pps['height'], pps['chunk_bytes']), (1440, 3168, 720))
        self.assertEqual(pps['encoded_bits_per_pixel_x16'], 256)
        packet = bytes.fromhex('39000040000004ff5aa500')
        self.assertEqual(command_packets(packet)[0]['vendor_flags'], 64)
        for bad in [packet[:6], packet[:-1]]:
            with self.assertRaises(ValueError):
                command_packets(bad)

    def test_dsc_all_fields_roundtrip_and_reject_unsafe_fallbacks(self):
        fixture = json.loads((TOOLS.parents[1] / 'devices/oneplus13/panel-aa569-120hz.json').read_text())
        raw = vendor_pps(fixture['on_packets'])
        cfg = decode_pps(raw)
        self.assertEqual(pack_pps(cfg), raw.ljust(128, b'\0'))
        self.assertEqual(cfg['bits_per_pixel'], 128)
        self.assertEqual((cfg['initial_xmit_delay'], cfg['initial_dec_delay']), (341, 482))
        self.assertEqual((cfg['initial_offset'], cfg['final_offset']), (2048, 3072))
        self.assertEqual(cfg['rc_range_params'][3]['range_bpg_offset'], 62)
        # Flip independent reserved/profile/range fields, not only truncation.
        for offset, value in [(1, 1), (4, raw[4] | 0x10), (5, 1), (12, 0),
                              (16, 0xff), (21, 64), (24, 0xff), (43, 0),
                              (44, 255), (88, 2), (89, 32)]:
            bad = bytearray(raw)
            bad[offset] = value
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                decode_pps(bad)
        for bad in [raw[:-1], raw+b'\0', raw+bytes(33)+b'\1']:
            with self.assertRaises(ValueError):
                decode_pps(bad)

    def test_runtime_memory_never_exposes_stock_protected_holes(self):
        def tree(memory, reservations):
            t = Fdt.__new__(Fdt)
            addressing = {'#address-cells': struct.pack('>I', 2), '#size-cells': struct.pack('>I', 2)}
            t.nodes = {'/': addressing.copy(), '/memory@80000000': {
                'device_type': b'memory\0', 'reg': b''.join(struct.pack('>QQ', *r) for r in memory)},
                '/reserved-memory': addressing.copy()}
            for i, r in enumerate(reservations):
                t.nodes[f'/reserved-memory/test{i}'] = {'reg': struct.pack('>QQ', *r), 'no-map': b''}
            t.reservations = []
            return Fdt(t.to_blob())
        original = tree([(0x80000000, 0x1000)], [(0x80001000, 0x1000)])
        runtime = tree([(0x80000000, 0x10000)], [(0x80001800, 0x1800)])
        report = calibrate_memory(original, runtime)
        self.assertEqual(report['additional_no_map_ranges'], [[0x80002000, 0x1000]])
        self.assertTrue(report['stock_reserved_ranges_all_excluded'])
        original.nodes['/reserved-memory/test0']['reusable'] = b''
        with self.assertRaisesRegex(ValueError, 'reusable'):
            calibrate_memory(original, runtime)
        del original.nodes['/reserved-memory/test0']['reusable']
        runtime.nodes['/memory@80000000']['reg'] *= 2
        with self.assertRaisesRegex(ValueError, 'Overlapping'):
            calibrate_memory(original, runtime)

    def test_stock_control_rejects_extra_control_properties(self):
        actual, control = Fdt.__new__(Fdt), Fdt.__new__(Fdt)
        actual.nodes = {'/panel': {'model': b'synthetic\0'}}
        control.nodes = {'/panel': {'model': b'synthetic\0', 'extra-property': b''}}
        with self.assertRaisesRegex(ValueError, 'extra-property'):
            compare_subtree(actual, control, '/panel')

    def test_stock_boot_v4_geometry_and_truncation(self):
        blob = bytearray(12288)
        blob[:8] = b'ANDROID!'
        struct.pack_into('<II', blob, 8, 3, 4)
        struct.pack_into('<I', blob, 20, 1584)
        struct.pack_into('<I', blob, 40, 4)
        self.assertEqual(boot_image(blob)['sections']['ramdisk'], [8192, 4])
        with self.assertRaises(ValueError):
            boot_image(blob[:8193])

    def test_stock_fdt_roundtrip_bounds_and_overlay_isolation(self):
        tree = Fdt.__new__(Fdt)
        tree.nodes = {'/': {'model': b'synthetic fixture\0'}, '/test': {'reg': struct.pack('>III', 0, 0x80000000, 0x1000)}}
        tree.reservations = [[0x90000000, 4096]]
        blob = tree.to_blob()
        parsed = Fdt(blob)
        self.assertEqual(parsed.nodes, tree.nodes)
        self.assertEqual(parsed.reservations, tree.reservations)
        self.assertEqual(len(split_dtbs(blob + b'\0\0' + blob)), 2)
        with self.assertRaises(ValueError):
            Fdt(blob[:-1])
        bad_overlay = Fdt.__new__(Fdt)
        bad_overlay.nodes = {'/': {}, '/fragment@0': {'target-path': b'/soc\0'}}
        with self.assertRaisesRegex(ValueError, 'Absolute overlay target'):
            prepare_sink(parsed, [], [{'tree': bad_overlay}], parsed)

    def test_calibration_uses_actual_indices_and_strips_panel_serial(self):
        self.assertEqual(boot_index('androidboot.dtb_idx = "2"\n', 'dtb_idx'), 2)
        for text in ['', 'androidboot.dtb_idx = "2"\nandroidboot.dtb_idx = "3"']:
            with self.assertRaises(ValueError):
                boot_index(text, 'dtb_idx')
        path = selected_panel('msm_drm.dsi_display0=qcom,panel_a:PanelSN-SECRET:')
        self.assertEqual(path, '/soc/qcom,mdss_mdp@ae00000/qcom,panel_a')
        self.assertNotIn('SECRET', path)

    def test_rejects_truncated_android_image(self):
        with self.assertRaises(ValueError):
            boot_sections(b'ANDROID!')
        header = bytearray(4096)
        header[:8] = b'ANDROID!'
        struct.pack_into('<9I', header, 8, 100, 0, 100, 0, 0, 0, 0, 4096, 2)
        struct.pack_into('<I', header, 1648, 100)
        with self.assertRaisesRegex(ValueError, 'Truncated'):
            boot_sections(header)

    def test_extracts_android_v2_sections_at_page_boundaries(self):
        data = bytearray(4 * 4096)
        data[:8] = b'ANDROID!'
        struct.pack_into('<9I', data, 8, 3, 0, 4, 0, 0, 0, 0, 4096, 2)
        struct.pack_into('<I', data, 1648, 5)
        data[4096:4099] = b'abc'
        data[8192:8196] = b'defg'
        data[12288:12293] = b'hijkl'
        self.assertEqual(boot_sections(data), {'kernel': b'abc', 'ramdisk': b'defg', 'dtb': b'hijkl'})

    def test_cpio_rejects_paths_and_duplicates(self):
        entry = lambda name: (name, stat.S_IFREG | 0o644, b'x', 0, 0)
        for entries in [[entry('/init')], [entry('../init')], [entry('init'), entry('init')]]:
            with self.assertRaises(ValueError):
                make_cpio(entries)

    def test_cpio_is_deterministic_and_encodes_console_device(self):
        entries = [('dev/console', stat.S_IFCHR | 0o600, b'', 5, 1)]
        archive = make_cpio(entries)
        self.assertEqual(archive, make_cpio(entries))
        fields = [int(archive[6 + i*8:14 + i*8], 16) for i in range(13)]
        self.assertEqual(fields[9:11], [5, 1])
        self.assertEqual(fields[1] & stat.S_IFMT(0o170000), stat.S_IFCHR)

    def test_missing_builtin_dependency_is_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = pathlib.Path(tmp) / '.config'
            config.write_text('\n'.join(f'CONFIG_{name}=y' for name in REQUIRED))
            check_config(config)
            config.write_text(config.read_text().replace('CONFIG_USB_DWC3=y', 'CONFIG_USB_DWC3=m'))
            with self.assertRaisesRegex(ValueError, 'USB_DWC3'):
                check_config(config)
            config.write_text('\n'.join(f'CONFIG_{name}=y' for name in REQUIRED) + '\nCONFIG_ARCH_MEDIATEK=y\n')
            with self.assertRaisesRegex(ValueError, 'Unrelated platform'):
                check_config(config)

    def test_cpio_reader_rejects_truncation_and_missing_trailer(self):
        archive = make_cpio([('init', stat.S_IFREG | 0o755, b'#!/bin/sh\n', 0, 0)])
        self.assertEqual(read_cpio(archive)['init']['data'], b'#!/bin/sh\n')
        for bad in [archive[:10], archive[:115], archive[:-20]]:
            with self.assertRaises(ValueError):
                read_cpio(bad)

    def test_stock_partition_selection_prefers_current_slot(self):
        present = {'dtbo', 'dtbo_a', 'dtbo_b'}
        self.assertEqual(collector.resolve_partition('dtbo', '_b', present.__contains__), 'dtbo_b')
        self.assertEqual(collector.resolve_partition('dtbo', '_a', {'dtbo'}.__contains__), 'dtbo')

    def test_stock_partition_selection_never_falls_back_to_inactive_slot(self):
        for present in [{'boot_a'}, {'boot'}]:
            with self.assertRaises(ValueError):
                collector.resolve_partition('boot', '_b', present.__contains__)


if __name__ == '__main__':
    unittest.main()
