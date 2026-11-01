# SPDX-License-Identifier: GPL-2.0-only
import gzip
import importlib.util
from pathlib import Path
import stat
import sys
import tempfile
import subprocess
import unittest
from unittest.mock import patch

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

    def test_installer_blocks_display_alias_and_ordinary_explicit_loads(self):
        out = TOOLS.parents[1]/'out'
        out.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=out) as temporary:
            root = Path(temporary).resolve()
            (root/'etc').mkdir()
            (root/'etc/os-release').write_text('ID=ubuntu\n')
            # Windows needs privileges for Linux absolute symlinks. Unit files
            # are still written; this test exercises the actual policy writer.
            with patch.object(Path,'symlink_to'):
                installer.install(root)
            policy = (root/'etc/modprobe.d/90-oneplus13-display-manual.conf').read_text()
            for module in ['panel_oneplus_aa569','msm']:
                self.assertIn('blacklist '+module+'\n',policy)
                self.assertIn('install '+module+' /bin/false\n',policy)

    def exercise_runtime_guard(self, already_read_only):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            block = root/'sys/class/block/sda1'
            block.mkdir(parents=True)
            device = root/'dev/sda1'
            device.parent.mkdir()
            device.touch()
            binary = root/'bin'
            binary.mkdir()
            calls = root/'blockdev-calls'
            state = root/'read-only-state'
            state.write_text('1\n' if already_read_only else '0\n')
            fake = binary/'blockdev'
            fake.write_text(
                '#!/bin/sh\n'
                'printf "%s\\n" "$*" >> "$BLOCKDEV_CALLS"\n'
                'if [ "$1" = --getro ]; then IFS= read -r value < "$BLOCKDEV_STATE"; echo "$value"; exit 0; fi\n'
                'if [ "$1" = --setro ]; then echo 1 > "$BLOCKDEV_STATE"; exit 0; fi\n'
                'exit 1\n'
            )
            fake.chmod(0o755)
            script = (TOOLS.parents[1]/'devices/oneplus13/desktop/runtime-guard').read_text()
            script = script.replace('/sys/class/block', str(root/'sys/class/block'))
            script = script.replace('[ -b "/dev/$name" ]', '[ -e "/dev/$name" ]')
            script = script.replace('/dev/', str(root/'dev')+'/')
            script_path = root/'runtime-guard'
            script_path.write_text(script)
            result = subprocess.run(['/bin/sh', str(script_path), '--once'],
                env={'PATH':str(binary), 'BLOCKDEV_CALLS':str(calls),
                     'BLOCKDEV_STATE':str(state)},
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            commands = calls.read_text().splitlines()
            self.assertEqual(commands, ['--getro '+str(device)] +
                ([] if already_read_only else ['--setro '+str(device), '--getro '+str(device)]))

    def test_runtime_guard_does_not_rewrite_read_only_mounted_partition(self):
        self.exercise_runtime_guard(True)

    def test_runtime_guard_sets_read_only_on_new_writable_partition(self):
        self.exercise_runtime_guard(False)
