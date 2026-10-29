# SPDX-License-Identifier: GPL-2.0-only
import importlib.util,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('watchdog_recovery',ROOT/'tools/oneplus13/ram-watchdog-recovery.py')
wdt=importlib.util.module_from_spec(spec);spec.loader.exec_module(wdt)


class WatchdogInventory(unittest.TestCase):
    def test_clock_probe_has_no_ping_during_measurement_and_restores_affinity(self):
        class Clock:
            now=0
            def monotonic(self):
                self.now+=0.25
                return self.now
            def sleep(self,seconds):self.now+=seconds
        clock=Clock();events=[];report={}
        with patch.object(wdt.os,'sched_getaffinity',return_value={2,3},create=True), \
             patch.object(wdt.os,'sched_setaffinity',side_effect=lambda pid,cpus:events.append(('affinity',cpus)),create=True), \
             patch.object(wdt.time,'monotonic',side_effect=clock.monotonic), \
             patch.object(wdt.time,'sleep',side_effect=clock.sleep):
            wdt.clock_probe(lambda label:events.append(('sample',label)),report,
                            lambda:events.append(('ping',None)))
        self.assertEqual(events,[('affinity',{2}),('sample','clock-probe-start'),
            ('sample','clock-probe-idle-1'),('sample','clock-probe-busy-2'),
            ('sample','clock-probe-idle-3'),('ping',None),
            ('sample','clock-probe-after-keepalive'),('affinity',{2,3})])
        self.assertEqual([x['mode'] for x in report['clock_intervals']],['idle','busy','idle'])
        self.assertNotIn('countdown_verified',report)
        self.assertNotIn('reset_observed',report)

    def test_clock_probe_restores_affinity_on_status_failure_without_ping(self):
        with patch.object(wdt.os,'sched_getaffinity',return_value={0,1},create=True), \
             patch.object(wdt.os,'sched_setaffinity',create=True) as affinity, \
             patch.object(wdt.time,'sleep') as sleep:
            with self.assertRaisesRegex(ValueError,'status'):
                wdt.clock_probe(lambda label:(_ for _ in ()).throw(ValueError('status')),{},
                                lambda:self.fail('Unexpected ping'))
        self.assertEqual(affinity.call_args_list[-1].args,(0,{0,1}))
        sleep.assert_not_called()

    def test_refuse_foreign_active_nowayout_and_invalid_device_before_open(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            original={'identity':'Gunyah Watchdog','state':'inactive','timeout':'32','nowayout':'0','dev':'241:1'}
            for key,value in original.items():(base/key).write_text(value)
            self.assertEqual(wdt.validate_inventory(base),(241,1))
            for key,value in [('identity','other'),('state','active'),('timeout','60'),
                              ('nowayout','1'),('dev','241:1:2'),('dev','../other')]:
                with self.subTest(key=key,value=value):
                    (base/key).write_text(value)
                    with self.assertRaises(ValueError):wdt.validate_inventory(base)
                    (base/key).write_text(original[key])

    def test_read_only_status_samples_and_reject_bad_hypervisor_values(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder);(base/'device').mkdir();path=base/'device/hypervisor_status'
            self.assertFalse(wdt.status_sample(base,'legacy')['available'])
            with self.assertRaises(ValueError):wdt.status_sample(base,'required',True)
            path.write_text('result=0 enabled=1 expired=0 elapsed_raw=2011\n')
            result=wdt.status_sample(base,'countdown',True)
            self.assertEqual(result['elapsed_raw'],2011)
            self.assertEqual(result['enabled'],1)
            self.assertEqual(result['label'],'countdown')
            self.assertGreater(result['monotonic_seconds'],0)
            for text in ('result=1 enabled=1 expired=0 elapsed_raw=0',
                         'result=0 enabled=2 expired=0 elapsed_raw=0',
                         'result=0 enabled=1 expired=2 elapsed_raw=0',
                         'result=0 enabled=1 expired=0 elapsed_raw=-1',
                         'result=0 enabled=1 expired=0 elapsed_raw=4294967296',
                         'result=0 enabled=1 enabled=0 elapsed_raw=1',
                         'result=0 enabled=1 expired=0 elapsed_raw=1 unknown=0',
                         'result=0 enabled=1 expired=0 elapsed_raw=abc',
                         'x'*257):
                with self.subTest(text=text):
                    path.write_text(text)
                    with self.assertRaises(ValueError):wdt.status_sample(base,'bad',True)


if __name__=='__main__':unittest.main()
