# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the real shell identity function; never invoke modprobe or the phone."""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
BASH = os.environ.get('TEST_BASH') or shutil.which('bash')


def shell_path(path):
    value = Path(path).resolve().as_posix()
    return '/'+value[0].lower()+value[2:] if len(value)>2 and value[1]==':' else value


class NativeGateTests(unittest.TestCase):
    def test_identity_matrix_runs_actual_shell_function(self):
        helper = (REPO/'devices/oneplus13/start-native-display').read_text()
        start = helper.index('check_native_identity() {')
        function = helper[start:helper.index('\n}',start)+2]
        cases = json.loads((REPO/'devices/oneplus13/test-fixtures/native-identity.json').read_text())
        for case in cases:
            with self.subTest(case=case['name']), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                for key in ['model','chassis']:
                    if case[key] is not None:
                        (root/('chassis-type' if key=='chassis' else key)).write_bytes(case[key].encode()+b'\0')
                (root/'compatible').write_bytes(('\0'.join(case['compatible'])+'\0').encode())
                command = function+'\ncheck_native_identity '+shlex.quote(shell_path(root))
                run = subprocess.run([BASH,'--noprofile','--norc','-c',command],capture_output=True,text=True)
                self.assertEqual(run.returncode==0,case['accept'],run.stdout+run.stderr)

    def test_native_desktop_rejected_before_reading_any_inputs(self):
        run = subprocess.run([sys.executable,str(REPO/'tools/oneplus13/package-desktop.py'),
            '--stock','missing','--artifacts','missing','--desktop','missing',
            '--ufdt-tool','missing','--output','missing','--native-xml','missing'],
            capture_output=True,text=True)
        self.assertEqual(run.returncode,2)
        self.assertIn('Native desktop packaging is disabled',run.stderr)
        self.assertNotIn('Traceback',run.stderr)
