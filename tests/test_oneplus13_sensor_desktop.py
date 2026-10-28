# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the protected RAM sensor setup and desktop orientation gates."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'sensor_desktop', ROOT/'tools/oneplus13/ram-sensor-desktop.py')
desktop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(desktop)


def digest(value):
    return hashlib.sha256(value).hexdigest()


class DesktopSensor(unittest.TestCase):
    def test_transitions_require_sensor_and_mutter_movement(self):
        now = [0.0]
        orientation = lambda: ('bottom-up' if now[0] < 7 else
                               'left-up' if now[0] < 14 else 'right-up')
        transforms = lambda: ((0,) if now[0] < 7 else
                              (3,) if now[0] < 14 else (1,))
        result = desktop.collect(
            20, orientation, transforms,
            clock=lambda: now[0],
            sleep=lambda delay: now.__setitem__(0, now[0] + delay + .1))
        self.assertTrue(result['automatic_rotation_pass'])
        self.assertEqual(result['distinct_orientations'],
                         ['bottom-up', 'left-up', 'right-up'])
        self.assertEqual(result['distinct_display_transforms'], [0, 1, 3])
        self.assertFalse(result['physical_axes_calibration_accepted'])

    def test_static_pose_cannot_pass(self):
        now = [0.0]
        result = desktop.collect(
            20, lambda: 'normal', lambda: (0,),
            clock=lambda: now[0],
            sleep=lambda delay: now.__setitem__(0, now[0] + 1))
        self.assertFalse(result['automatic_rotation_pass'])

    def test_only_twenty_second_window_is_reviewed(self):
        for seconds in (True, 0, 19, 21, 120):
            with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                desktop.collect(seconds, lambda: 'normal', lambda: (0,))

    def test_setup_installs_only_inside_protected_ram_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'run/oneplus13').mkdir(parents=True)
            (root/'run/oneplus13/ram-session').write_text('RAM\n')
            (root/'proc').mkdir()
            (root/'proc/mounts').write_text('tmpfs / overlay rw 0 0\n')
            archive = root/'runtime.tar.gz'; archive.write_bytes(b'archive')
            manifest_bytes = b'{"native_elf_count": 10, "text_data_files": 922}\n'
            manifest_path = root/'manifest.json'; manifest_path.write_bytes(manifest_bytes)
            bindings = root/'bindings.json'
            bindings.write_text(json.dumps({
                'format': 'ONEPLUS13_IMAGE_SENSOR_INPUTS_V1',
                'inputs': {
                    'archive': {'path': str(archive), 'sha256': digest(b'archive')},
                    'manifest': {'path': str(manifest_path), 'sha256': digest(manifest_bytes)},
                },
            }))
            entries = {
                'usr/lib/test': (b'ELF', 0o755, None),
                'var/lib/test': (b'data', 0o640, None),
                'usr/share/mapped': (None, 0o777, '/var/lib/test'),
            }

            class FakeFileserver:
                @staticmethod
                def archive_entries(path, manifest):
                    self.assertEqual(path, archive)
                    return entries

                @staticmethod
                def install(target, files, chown):
                    for name, (content, mode, link) in files.items():
                        path = target/name
                        path.parent.mkdir(parents=True, exist_ok=True)
                        if link is not None:
                            path.symlink_to(link)
                        else:
                            path.write_bytes(content)
                            path.chmod(mode)

            marker = root/'run/oneplus13/sensor-runtime-ready.json'
            with patch.object(desktop, 'load', return_value=FakeFileserver):
                result = desktop.setup(root, bindings, marker, chown=lambda *args: None)
            self.assertEqual(result['scope'], 'ONEPLUS13_RAM_DESKTOP_SENSOR_RUNTIME_READY')
            self.assertFalse(result['attach_started'])
            self.assertEqual((root/'var/lib/test').read_bytes(), b'data')
            self.assertEqual(str((root/'usr/share/mapped').readlink()), '/var/lib/test')

    def test_service_configuration_stays_manual_and_restricted(self):
        service = ROOT/'devices/oneplus13/sensors'
        fileserver = (service/'oneplus13-sensor-fileserver.service').read_text()
        proxy = (service/'oneplus13-sensor-proxy.service').read_text()
        udev = (service/'10-oneplus13-fastrpc.rules').read_text()
        bringup = (ROOT/'devices/oneplus13/desktop/qualified-bringup').read_text()
        self.assertIn('User=65534', fileserver)
        self.assertIn('DevicePolicy=closed', fileserver)
        self.assertIn('/dev/fastrpc-adsp-secure rw', fileserver)
        self.assertIn('User=nobody', proxy)
        self.assertNotIn('WantedBy=', fileserver+proxy)
        self.assertIn('ENV{IIO_SENSOR_PROXY_TYPE}="ssc-accel ssc-compass ssc-gyro"', udev)
        self.assertIn('modprobe --ignore-install fastrpc', bringup)
        self.assertIn('orientation-lock false', bringup)


if __name__ == '__main__':
    unittest.main()
