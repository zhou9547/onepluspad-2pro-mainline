"""Exercise the production verifier policy used by Actions image completion."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/oneplus13'))
spec = importlib.util.spec_from_file_location('usb_image_verifier', ROOT/'tools/oneplus13/verify-complete-image.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class UsbImagePolicyTests(unittest.TestCase):
    def setUp(self):
        self.base = dict(cmdline='console=tty0 oneplus13.session=base root=overlay',
                         session_identity_nonce='base')
        self.target = dict(cmdline='console=tty0 oneplus13.session=target root=overlay '
            'oneplus13.ir_probe=1 oneplus13.usb_host_probe=1 ' + verifier.USB_LEASE_FLAG,
            session_identity_nonce='target', usb_firmware_lease_available=True,
            usb_firmware_lease_auto_started=False)

    def test_manual_target_policy_accepts_generated_flags(self):
        verifier.verify_targets_boot_arguments(self.base, self.target)

    def test_missing_extra_duplicate_or_reordered_argument_rejected(self):
        original = self.target['cmdline']
        for changed in (original.replace(' '+verifier.USB_LEASE_FLAG, ''),
                        original+' '+verifier.USB_LEASE_FLAG, original+' unexpected=1',
                        original.replace('oneplus13.ir_probe=1 oneplus13.usb_host_probe=1',
                                         'oneplus13.usb_host_probe=1 oneplus13.ir_probe=1')):
            with self.subTest(cmdline=changed), self.assertRaises(ValueError):
                verifier.verify_targets_boot_arguments(self.base, {**self.target, 'cmdline':changed})

    def test_manual_policy_requires_exact_booleans(self):
        for key, values in [('usb_firmware_lease_available', (False, None, 1, 'true')),
                            ('usb_firmware_lease_auto_started', (True, None, 0, 'false'))]:
            for value in values:
                with self.subTest(key=key,value=value), self.assertRaises(ValueError):
                    verifier.verify_targets_boot_arguments(self.base,{**self.target,key:value})

    def test_lease_in_parent_boot_rejected(self):
        with self.assertRaisesRegex(ValueError, 'leaked'):
            verifier.verify_targets_boot_arguments(
                {**self.base,'cmdline':self.base['cmdline']+' '+verifier.USB_LEASE_FLAG}, self.target)


if __name__ == '__main__': unittest.main()
