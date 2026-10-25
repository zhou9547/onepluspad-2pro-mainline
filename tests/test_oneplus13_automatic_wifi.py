"""Offline fake-process checks, no device/network operations."""
import contextlib
import importlib.util
import io
import json
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('wifi', Path(__file__).resolve().parents[1]/'tools/oneplus13/automatic-wifi-check.py')
wifi = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wifi)


class Fake:
    def __init__(self, fail=None, target=True, state='30 (disconnected)',fail_status=124):
        self.calls = []
        self.ident = None
        self.fail = fail
        self.target = target
        self.password_file = None
        self.state=state
        self.fail_status=fail_status

    def __call__(self, args, seconds):
        self.calls.append(args)
        assert 0 < seconds <= 18
        if self.fail and self.fail in args:
            return self.fail_status, 'private diagnostics not printed'
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
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()) as output, patch.object(wifi.time, 'sleep'):
            result = wifi.check({'ssid': 'offline-network', 'password': 'offline-secret-value'},
                                'wlan-test', execute=fake, runtime=Path(d))
            self.assertNotIn('offline-secret-value', output.getvalue())
            self.assertNotIn('offline-secret-value', repr(fake.calls))
            self.assertFalse(list(Path(d).iterdir()))
        return result

    def test_full_success_requires_target_profile_dhcp_https(self):
        r = self.call(Fake())
        self.assertTrue(all(r[k] for k in ['association_pass', 'dhcp_pass', 'https_pass']))

    def test_ipv6_first_activation_waits_for_delayed_ipv4_on_same_connection(self):
        base=Fake();observations=0
        def delayed(args,seconds):
            nonlocal observations
            if 'address' in args:
                observations+=1
                if observations<3:return 0,'[]'
            if 'route' in args and observations<3:return 0,'[]'
            return base(args,seconds)
        delayed.calls=base.calls
        r=self.call(delayed)
        self.assertTrue(r['dhcp_pass'] and r['https_pass'])
        self.assertEqual(r['ipv4_observations'],3)
        self.assertEqual(sum('up' in c for c in base.calls),1)

    def test_ipv6_only_never_passes_ipv4_acceptance_and_observation_is_bounded(self):
        base=Fake();observations=0
        def absent(args,seconds):
            nonlocal observations
            if 'address' in args:observations+=1;return 0,'[]'
            if 'route' in args:return 0,'[]'
            return base(args,seconds)
        absent.calls=base.calls
        r=self.call(absent)
        self.assertFalse(r['dhcp_pass'] or r['https_pass'])
        self.assertEqual(observations,8)
        self.assertFalse(any(c[0]=='curl' for c in base.calls))

    def test_ipv4_query_timeout_stops_without_reconnection(self):
        f=Fake(fail='address');r=self.call(f)
        self.assertFalse(r['dhcp_pass'] or r['https_pass'])
        self.assertEqual(r['ipv4_address_rc'],124)
        self.assertEqual(sum('up' in c for c in f.calls),1)

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

    def test_real_missing_executable_returns_code_without_traceback(self):
        self.assertEqual(wifi.run(['/oneplus13-offline-no-such-binary'],1),(127,'executable missing'))

    def test_missing_optional_ping_does_not_abort_https(self):
        f=Fake(fail='ping',fail_status=127)
        r=self.call(f)
        self.assertEqual(r['gateway_rc'],127)
        self.assertEqual(r['gateway_error_class'],'executable_missing')
        self.assertTrue(r['gateway_probe_skipped'])
        self.assertTrue(any(c[0]=='getent' for c in f.calls))
        self.assertTrue(any(c[0]=='curl' for c in f.calls))
        self.assertTrue(r['association_pass'] and r['dhcp_pass'] and r['https_pass'])

    def test_missing_curl_is_reported_as_failure(self):
        r=self.call(Fake(fail='curl',fail_status=127))
        self.assertFalse(r['https_pass'])
        self.assertEqual(r['https_error_class'],'executable_missing')

    def test_missing_optional_dns_probe_still_runs_interface_bound_https(self):
        f=Fake(fail='getent',fail_status=127)
        r=self.call(f)
        self.assertTrue(r['dns_probe_skipped'] and r['https_pass'])
        curl=next(c for c in f.calls if c[0]=='curl')
        self.assertEqual(curl[curl.index('--interface')+1],'wlan-test')
        self.assertEqual(curl[curl.index('--noproxy')+1],'*')
        self.assertIn('https://example.com/',curl)
        self.assertNotIn('--insecure',curl)
        self.assertIn('--ipv4',curl)

    def test_missing_ping_and_https_failure_never_passes(self):
        base=Fake()
        def both(args,seconds):
            if args[0]=='ping':return 127,'private'
            if args[0]=='curl':return 7,'private'
            return base(args,seconds)
        both.calls=base.calls
        r=self.call(both)
        self.assertTrue(r['gateway_probe_skipped'])
        self.assertFalse(r['https_pass'])

    def test_missing_core_tool_preflight_stops_before_network_commands(self):
        for missing in ['nmcli','busctl','ip','curl']:
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as d:
                credentials=Path(d)/'credentials.json'
                credentials.write_text(json.dumps({'ssid':'offline-network','password':'offline-secret-value'}))
                with patch.object(sys, 'argv',
                                  ['automatic-wifi-check.py','--credentials',str(credentials)]), \
                     patch.object(wifi.Path,'read_text', side_effect=['x / overlay rw 0 0',credentials.read_text()]), \
                     patch.object(wifi.Path,'iterdir',return_value=iter([])), \
                     patch.object(wifi.shutil,'which',side_effect=lambda name:None if name==missing else '/usr/bin/'+name), \
                     patch.object(wifi,'check') as check, contextlib.redirect_stdout(io.StringIO()) as output:
                    wifi.main()
                check.assert_not_called()
                result=json.loads(output.getvalue().split('AUTO_WIFI_RESULT ',1)[1])
                self.assertEqual(result['missing_required_commands'],[missing])
                self.assertFalse(result['automatic_acceptance_pass'])
                self.assertFalse(credentials.exists())

    def test_permission_error_is_sanitized(self):
        with patch.object(wifi.subprocess,'run',side_effect=PermissionError('private diagnostics')):
            self.assertEqual(wifi.run(['unused'],1),(126,'executable unavailable'))

    def test_curl_failure_preserves_metrics_and_discards_raw_stderr(self):
        from types import SimpleNamespace
        completed=SimpleNamespace(returncode=28,stdout='dns_s=0.01\ntcp_s=0\n',stderr='private endpoint details')
        with patch.object(wifi.subprocess,'run',return_value=completed):
            self.assertEqual(wifi.run(['curl','--write-out',wifi.HTTPS_WRITE_OUT],9),
                             (28,'dns_s=0.01\ntcp_s=0\n'))

    def test_timing_parser_keeps_only_bounded_numeric_fields(self):
        r=wifi.https_metrics('dns_s=0.01\ntcp_s=0.2\ntls_s=0.4\nfirst_byte_s=0.6\ntotal_s=0.7\nhttp_code=200\nremote_ip=private\n')
        self.assertEqual(r,dict(dns_s=0.01,tcp_s=0.2,tls_s=0.4,first_byte_s=0.6,total_s=0.7,http_code=200))
        self.assertEqual(wifi.https_metrics('dns_s=nan\ntcp_s=-1\ntls_s=inf\ntotal_s=999\nhttp_code=private\n'),{})

    def test_https_timeout_keeps_completed_stage_timings_without_passing(self):
        base=Fake()
        def timeout(args,seconds):
            if args[0]=='curl':
                return 28,'dns_s=0.01\ntcp_s=0.1\ntls_s=0\nfirst_byte_s=0\ntotal_s=4.0\nhttp_code=000\n'
            return base(args,seconds)
        timeout.calls=base.calls
        r=self.call(timeout)
        self.assertFalse(r['https_pass'])
        self.assertEqual(r['https_error_class'],'transfer_timeout')
        self.assertEqual(r['https_metrics']['tcp_s'],0.1)
        self.assertEqual(r['https_metrics']['tls_s'],0)
        self.assertEqual(r['https_address_family'],'IPv4')

    def test_ssl_verification_result_is_numeric_and_bounded(self):
        self.assertEqual(wifi.https_metrics('ssl_verify_result=9\n'),{'ssl_verify_result':9})
        self.assertEqual(wifi.https_metrics('ssl_verify_result=private\n'),{})
        self.assertEqual(wifi.https_metrics('ssl_verify_result=-1\n'),{})

    def test_certificate_error_never_passes(self):
        r=self.call(Fake(fail='curl',fail_status=60))
        self.assertFalse(r['https_pass'])
        self.assertEqual(r['https_error_class'],'certificate_verification_failed')


if __name__ == '__main__':
    unittest.main()
