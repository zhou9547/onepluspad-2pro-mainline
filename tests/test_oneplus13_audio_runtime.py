# SPDX-License-Identifier: GPL-2.0-only
import importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/oneplus13/ram-audio-check.py'
s=importlib.util.spec_from_file_location('ram_audio',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

class AudioRuntime(unittest.TestCase):
    def test_dependency_order_and_missing_or_cyclic_inventory(self):
        text='kernel/a.ko: kernel/b.ko kernel/c.ko\nkernel/b.ko: kernel/c.ko\nkernel/c.ko:\n'
        self.assertEqual(m.module_order(text,['a']),['c','b','a'])
        for bad in [text.replace('kernel/c.ko:\n',''),text.replace('kernel/c.ko:\n','kernel/c.ko: kernel/a.ko\n'),
                    text.replace('kernel/b.ko','../b.ko')]:
            with self.assertRaises(ValueError):m.module_order(bad,['a'])

    def test_live_amp_state_requires_zero_volume_and_maximum_attenuation(self):
        row='id=2308 channel=0 volume=0 powered=1 faulted=0 sysst=0311 sysctrl=2000 attenuation=1023\n'
        self.assertTrue(m.active_state(m.amp_state(row)))
        self.assertTrue(m.active_state(m.amp_state(row.replace('sysst=0311','sysst=0211'))))
        for old,new in [('id=2308','id=2309'),('volume=0','volume=1'),
                        ('faulted=0','faulted=1'),('attenuation=1023','attenuation=1000')]:
            with self.assertRaises(ValueError):m.amp_state(row.replace(old,new))
        for old,new in [('powered=1','powered=0'),('sysst=0311','sysst=0000'),
                        ('sysst=0311','sysst=4311'),('sysctrl=2000','sysctrl=2003')]:
            self.assertFalse(m.active_state(m.amp_state(row.replace(old,new))))

if __name__=='__main__':unittest.main()
