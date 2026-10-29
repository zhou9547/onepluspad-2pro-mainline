# SPDX-License-Identifier: GPL-2.0-only
import importlib.util,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('watchdog_recovery',ROOT/'tools/oneplus13/ram-watchdog-recovery.py')
wdt=importlib.util.module_from_spec(spec);spec.loader.exec_module(wdt)


class WatchdogInventory(unittest.TestCase):
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
