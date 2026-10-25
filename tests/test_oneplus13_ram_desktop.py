"""Offline RAM-only desktop policy and greeter/session separation checks."""
import configparser
import importlib.util
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('desktop',Path(__file__).resolve().parents[1]/'tools/oneplus13/ram-desktop-check.py')
desktop=importlib.util.module_from_spec(spec);spec.loader.exec_module(desktop)
spec=importlib.util.spec_from_file_location('wifi',Path(__file__).resolve().parents[1]/'tools/oneplus13/automatic-wifi-check.py')
wifi=importlib.util.module_from_spec(spec);spec.loader.exec_module(wifi)


class Desktop(unittest.TestCase):
    def test_software_only_runs_without_wifi_helper_installed(self):
        class FakePath:
            name='wayland-0'
            def __init__(self,*args):pass
            def __truediv__(self,other):return self
            def glob(self,pattern):return [self]
            def iterdir(self):return iter([])
            def read_text(self):return '/usr/lib/erhai/mesa/lib/libEGL_mesa.so.0'
            def exists(self):return True
        with patch.dict('sys.modules',{'pwd':SimpleNamespace(getpwnam=lambda name:SimpleNamespace(pw_uid=1000))}), \
             patch.object(desktop,'Path',FakePath),patch.object(desktop,'user_session',return_value={'Name':'a'}), \
             patch.object(desktop,'process_ids',return_value=['42']),patch.object(desktop,'socket_file',return_value=True), \
             patch.object(desktop,'command',return_value=''),patch.object(desktop.time,'sleep'), \
             patch.object(desktop.importlib.util,'spec_from_file_location',side_effect=AssertionError('WiFi helper must not be imported')), \
             patch.object(desktop,'SAMPLES',[]),patch.object(desktop,'COMPLETED',{}):
            result=desktop.check(check_wifi=False)
        self.assertTrue(result['software_acceptance_pass'])
        self.assertFalse(result['wifi_tested'] or result['combined_pass'])
        self.assertEqual(len(result['samples']),3)

    def test_software_only_never_claims_wifi_or_combined_acceptance(self):
        with patch.object(desktop,'SAMPLES',[{'bound_wifi_https':None}]*3):
            r=desktop.completed_result(False)
        self.assertTrue(r['software_acceptance_pass'])
        self.assertFalse(r['wifi_tested'] or r['wifi_stability_pass'] or r['combined_pass'])

    def test_three_successful_probes_required_for_combined_acceptance(self):
        for probes,passed in [([],False),([True]*2,False),([True]*3,True),([True,False,True],False)]:
            samples=[{'bound_wifi_https':{'passed':p}} for p in probes]
            with patch.object(desktop,'SAMPLES',samples):r=desktop.completed_result(True)
            self.assertEqual(r['combined_pass'],passed)
    def test_config_preserves_other_sections_and_daemon_options(self):
        result=desktop.autologin_config('[daemon]\nWaylandEnable=true\nAutomaticLogin=old\n[security]\nDisallowTCP=true\n')
        c=configparser.ConfigParser();c.read_string(result)
        self.assertEqual(c['security']['DisallowTCP'],'true')
        self.assertEqual(c['daemon']['WaylandEnable'],'true')
        self.assertEqual(c['daemon']['AutomaticLogin'],'a')
        self.assertEqual(c['daemon']['AutomaticLoginEnable'],'True')
        self.assertEqual(c['daemon']['TimedLoginEnable'],'False')
        self.assertEqual(result,desktop.autologin_config(result))

    def test_commented_default_has_exactly_one_daemon_section(self):
        result=desktop.autologin_config('# sample\n[daemon]\n# AutomaticLoginEnable = true\n# AutomaticLogin = somebody\n[debug]\n')
        self.assertEqual(result.count('[daemon]'),1)
        self.assertEqual(result.count('AutomaticLogin='),1)
        self.assertIn('InitialSetupEnable=false',result)

    def test_reject_non_ram_or_missing_session_marker(self):
        for mounts,marker in [('x / ext4 rw 0 0',True),('x / overlay rw 0 0',False),('x /other overlay rw 0 0',True)]:
            with self.assertRaises(ValueError):desktop.ram_only(mounts,marker)
        desktop.ram_only('x / overlay rw 0 0',True)

    def test_accept_only_active_ordinary_gnome_wayland(self):
        p=dict(Name='a',User='1000',Type='wayland',Class='user',Active='yes',State='active',Remote='no',Desktop='ubuntu')
        self.assertTrue(desktop.accepted_session(p,1000))
        for desktop_name in ['', 'ubuntu-wayland', 'gnome', 'ubuntu:GNOME']:
            self.assertTrue(desktop.accepted_session(dict(p,Desktop=desktop_name),1000))
        for key,value in [('Name','gdm'),('User','120'),('Type','x11'),('Class','greeter'),('Active','no'),('State','closing'),('Remote','yes')]:
            with self.subTest(key=key):self.assertFalse(desktop.accepted_session(dict(p,**{key:value}),1000))

    def test_https_probe_keeps_partial_failure_metrics(self):
        def execute(args,seconds):
            self.assertEqual(seconds,9)
            self.assertIn('--interface',args);self.assertIn('--ipv4',args)
            self.assertNotIn('--insecure',args)
            return 28,'tcp_s=0.1\ntls_s=0.3\nhttp_code=000\nssl_verify_result=0\n'
        r=desktop.probe_https(wifi,'wlan-test',execute)
        self.assertFalse(r['passed']);self.assertEqual(r['returncode'],28)
        self.assertEqual(r['metrics']['tls_s'],.3)

    def test_https_requires_success_status_and_valid_certificate(self):
        for rc,http,cert,passed in [(0,200,0,True),(0,200,9,False),(0,204,0,False),(60,0,9,False)]:
            with self.subTest(rc=rc,http=http,cert=cert):
                r=desktop.probe_https(wifi,'wlan-test',lambda args,seconds:(rc,f'http_code={http:03d}\nssl_verify_result={cert}\n'))
                self.assertEqual(r['passed'],passed)


if __name__=='__main__':unittest.main()
