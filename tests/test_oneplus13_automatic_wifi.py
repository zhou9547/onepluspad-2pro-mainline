"""Offline fake-process checks, no device/network operations."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('wifi', Path(__file__).resolve().parents[1]/'tools/oneplus13/automatic-wifi-check.py')
wifi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wifi)


class Fake:
    def __init__(self, fail=None, target=True, state='30 (disconnected)'):
        self.calls = []
        self.ident = None
        self.fail = fail
        self.target = target
        self.password_file = None
        self.state=state

    def __call__(self, args, seconds):
        self.calls.append(args)
        assert 0 < seconds <= 18
        if self.fail and self.fail in args:
            return 124, 'private diagnostics not printed'
        if 'SSID' in args:
            return 0, 'offline-network\n' if self.target else 'other-network\n'
        if 'GENERAL.STATE' in args:
            return 0, self.state+'\n'
        if 'add' in args:
            self.ident = args[args.index('connection.uuid')+1]
        if 'passwd-file' in args:
            self.password_file = Path(args[-1])
            assert self.password_file.stat().st_mode & 0o777 == 0o600
            assert self.password_file.read_text() == '802-11-wireless-security.psk:offline-secret-value\n'
        if 'GENERAL.CON-UUID' in args:
            return 0, self.ident+'\n'
        if 'address' in args:
            return 0, json.dumps([{'addr_info': [{'scope': 'global'}]}])
        if 'route' in args:
            return 0, json.dumps([{'dst': 'default', 'gateway': '192.0.2.1'}])
        return 0, ''


class Checks(unittest.TestCase):
    def call(self, fake):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()) as output:
            result = wifi.check({'ssid': 'offline-network', 'password': 'offline-secret-value'},
                                'wlan-test', execute=fake, runtime=Path(d))
            self.assertNotIn('offline-secret-value', output.getvalue())
            self.assertNotIn('offline-secret-value', repr(fake.calls))
            self.assertFalse(list(Path(d).iterdir()))
        return result

    def test_full_success_requires_target_profile_dhcp_https(self):
        r = self.call(Fake())
        self.assertTrue(all(r[k] for k in ['association_pass', 'dhcp_pass', 'https_pass']))

    def test_nm_timeout_stops_before_scan_auth(self):
        f = Fake(fail='GENERAL.STATE')
        r = self.call(f)
        self.assertEqual(len(f.calls), 2)
        self.assertFalse(r['association_pass'])

    def test_target_absent_never_stages_secret_or_connects(self):
        f = Fake(target=False)
        r = self.call(f)
        self.assertFalse(r['target_seen'])
        self.assertFalse(any('passwd-file' in c for c in f.calls))

    def test_auth_timeout_removes_secret_file_and_stops(self):
        f = Fake(fail='up')
        r = self.call(f)
        self.assertFalse(r['association_pass'])
        self.assertFalse(f.password_file and f.password_file.exists())

    def test_failed_https_not_a_pass(self):
        r = self.call(Fake(fail='curl'))
        self.assertTrue(r['association_pass'] and r['dhcp_pass'])
        self.assertFalse(r['https_pass'])

    def test_missing_supplicant_never_scans_or_authenticates(self):
        f=Fake(fail='busctl')
        result=self.call(f)
        self.assertEqual(len(f.calls),1)
        self.assertFalse(result['association_pass'])

    def test_unavailable_device_does_not_scan(self):
        base=Fake(state='20 (unavailable)')
        result=self.call(base)
        self.assertFalse(result['nm_device_ready'])
        self.assertFalse(any('rescan' in c for c in base.calls))

    def test_subprocess_timeout_is_bounded_and_discards_output(self):
        from unittest.mock import patch
        import subprocess
        with patch.object(wifi.subprocess, 'run', side_effect=subprocess.TimeoutExpired('test', 1, output='private')):
            self.assertEqual(wifi.run(['no-real-command'], 1), (124, ''))


if __name__ == '__main__':
    unittest.main()
