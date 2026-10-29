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


if __name__=='__main__':unittest.main()
