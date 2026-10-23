# SPDX-License-Identifier: GPL-2.0-only
import gzip
import importlib.util
from pathlib import Path
import stat
import sys
import unittest

TOOLS = Path(__file__).resolve().parents[1]/'tools/oneplus13'
sys.path.insert(0, str(TOOLS))
from common import make_cpio, read_cpio
from desktop import derive
spec = importlib.util.spec_from_file_location('install_desktop', TOOLS/'install-desktop.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class DesktopTests(unittest.TestCase):
    def fixture(self):
        init = (TOOLS.parents[1]/'devices/oneplus13/init').read_bytes().replace(b'\r\n', b'\n')
        return gzip.compress(make_cpio([
            ('bin', stat.S_IFDIR|0o755, b'', 0, 0),
            ('init', stat.S_IFREG|0o755, init, 0, 0),
            ('dev/console', stat.S_IFCHR|0o600, b'', 5, 1),
        ]))

    def test_preserves_device_nodes_and_unrelated_entries(self):
        original = self.fixture()
        packed, report = derive(original)
        old, new = read_cpio(gzip.decompress(original)), read_cpio(gzip.decompress(packed))
        self.assertEqual(new['dev/console'], old['dev/console'])
        self.assertEqual(new['bin'], old['bin'])
        self.assertEqual(report['original_entries_preserved_except_explicit_init'], 2)
        self.assertIn(b'watchdog_pid=$!', new['init']['data'])
        self.assertIn(b'sleep 300', old['init']['data'])
        self.assertNotIn(b'sleep 300', new['init']['data'])

    def test_changed_diagnostic_init_rejected(self):
        entries = read_cpio(gzip.decompress(self.fixture()))
        entries['init']['data'] += b'\necho unexpected\n'
        packed = gzip.compress(make_cpio([(n, p['mode'], p['data'], p['major'], p['minor'])
                                         for n, p in entries.items()]))
        with self.assertRaises(ValueError):
            derive(packed)

    def test_cannot_install_support_into_host_root(self):
        with self.assertRaises(ValueError):
            installer.install(Path('/').resolve())
