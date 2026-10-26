# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the actual shell thermal gate on saved files; never call main."""
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools/oneplus13/ram-platform-prerequisites.sh'
class ThermalGateTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name)
    def zone(self,index,kind,value=None):
        path=self.root/f'class/thermal/thermal_zone{index}';path.mkdir(parents=True)
        (path/'type').write_text(kind)
        if value is not None:(path/'temp').write_text(str(value))
    def gate(self):
        return subprocess.run(['bash','-c','source "$1"; platform_thermal_gate "$2"','gate',str(SCRIPT),str(self.root)],capture_output=True).returncode
    def test_pending_battery_does_not_replace_cpu_gate(self):
        self.zone(0,'qcom-battmgr-bat');self.zone(1,'cpu-0-4-0-thermal',42000)
        self.assertEqual(self.gate(),0)
    def test_pending_cpu_temperature_refuses_activation(self):
        self.zone(0,'cpu-0-4-0-thermal');self.zone(1,'qcom-battmgr-bat',30000)
        self.assertNotEqual(self.gate(),0)
    def test_no_cpu_sensors_refuses_activation(self):
        self.zone(0,'qcom-battmgr-bat',30000)
        self.assertNotEqual(self.gate(),0)
    def test_hot_cpu_refuses_activation(self):
        self.zone(0,'cpuss-0-0-thermal',70000)
        self.assertNotEqual(self.gate(),0)
    def test_malformed_temperature_refuses_activation(self):
        self.zone(0,'aoss0-thermal','not-a-temperature')
        self.assertNotEqual(self.gate(),0)

if __name__=='__main__':unittest.main()
