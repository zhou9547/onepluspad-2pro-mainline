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
from common import boot_sections, make_cpio
from verify import check_config, REQUIRED


class PhoneFormats(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
