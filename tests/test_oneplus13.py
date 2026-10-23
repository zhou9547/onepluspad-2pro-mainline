# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
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
from calibrate import boot_index, selected_panel, prepare_sink
spec = importlib.util.spec_from_file_location('phone_stock_collector', TOOLS / 'collect-stock.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class PhoneFormats(unittest.TestCase):
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
