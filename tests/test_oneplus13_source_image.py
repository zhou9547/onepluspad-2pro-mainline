import hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class SourceImageTests(unittest.TestCase):
    def test_run88_functional_inputs_are_restored(self):
        lock=json.loads((ROOT/'devices/oneplus13/functional-source-lock.json').read_text())
        for name,sha in lock['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha)
        touch=(ROOT/'devices/oneplus13/kernel/synaptics-dodge/dodge-s3910-spi.c').read_text()
        self.assertNotIn('message.actual_length != len',touch)
        for name in ['0012-sm8750-adsp-pas.patch','0013-qseecom-allowlist.patch']:
            self.assertTrue((ROOT/'devices/oneplus13/kernel-patches'/name).is_file())

    def test_pipeline_cannot_download_historical_actions_images(self):
        workflow=(ROOT/'.github/workflows/oneplus13-source-image.yml').read_text()
        self.assertNotIn('run-id:',workflow)
        self.assertNotIn('github-token:',workflow)
        for value in ['source-kernel-${{ github.sha }}','source-gnome-${{ github.sha }}','source-mesa-${{ github.sha }}']:
            self.assertIn(value,workflow)
        self.assertIn('needs: [kernel, rootfs, mesa]',workflow)

    def test_native_entry_is_full_qualified_python_implementation(self):
        helper=(ROOT/'devices/oneplus13/start-native-display').read_text()
        runtime=(ROOT/'devices/oneplus13/native-desktop.py').read_text()
        self.assertTrue(helper.startswith('#!/usr/bin/python3\n'))
        self.assertEqual(helper.count('@KERNEL_RELEASE@'),1)
        self.assertEqual(helper.replace('# kernel release: @KERNEL_RELEASE@\n',''),runtime)
        self.assertIn('ONEPLUS13_NATIVE_PREFLIGHT_OK_NOT_ACTIVATED',helper)
        self.assertIn("['/usr/sbin/modprobe','--ignore-install',module]",helper)

if __name__=='__main__':unittest.main()
