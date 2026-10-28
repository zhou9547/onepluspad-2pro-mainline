#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Install and observe the reviewed OnePlus 13 desktop sensor stack in RAM.

The setup phase only writes inside the protected RAM overlay.  The check phase
does not claim sensors: after the desktop starts, GNOME Settings Daemon owns the
accelerometer and Mutter applies the automatic display transform.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path('/')
BINDINGS = Path('/usr/lib/oneplus13-sensors/runtime-bindings.json')
MARKER = Path('/run/oneplus13/sensor-runtime-ready.json')
FILESERVER = 'oneplus13-sensor-fileserver.service'
PROXY = 'oneplus13-sensor-proxy.service'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_tree(root, entries):
    """Verify regular files and the three reviewed absolute data mappings."""
    for name, (content, mode, target) in entries.items():
        path = Path(root) / name
        if target is not None:
            if not path.is_symlink() or str(path.readlink()) != target:
                raise ValueError('Sensor runtime mapping changed')
        elif not path.is_file() or path.is_symlink() or path.stat().st_mode & 0o777 != mode:
            raise ValueError('Sensor runtime mode or file type changed')
        elif sha(path) != hashlib.sha256(content).hexdigest():
            raise ValueError('Sensor runtime bytes changed')


def existing_tree(root, entries):
    return any((Path(root) / name).exists() or (Path(root) / name).is_symlink()
               for name in entries)


def setup(root=ROOT, bindings=BINDINGS, marker=MARKER, chown=os.chown):
    root = Path(root)
    bindings = Path(bindings)
    marker = Path(marker)
    if not root.is_relative_to(ROOT):
        raise ValueError('Sensor setup root is outside the host namespace')
    if not (root / 'run/oneplus13/ram-session').is_file():
        raise ValueError('Protected RAM session required')
    if not any(len(row := line.split()) >= 3 and row[1:3] == ['/', 'overlay']
               for line in (root / 'proc/mounts').read_text().splitlines()):
        raise ValueError('RAM overlay required')
    doc = json.loads(bindings.read_text())
    if doc.get('format') != 'ONEPLUS13_IMAGE_SENSOR_INPUTS_V1':
        raise ValueError('Unreviewed sensor bindings')
    archive = Path(doc['inputs']['archive']['path'])
    manifest_path = Path(doc['inputs']['manifest']['path'])
    for path, expected in ((archive, doc['inputs']['archive']['sha256']),
                           (manifest_path, doc['inputs']['manifest']['sha256'])):
        if path.is_symlink() or sha(path) != expected:
            raise ValueError('Sensor setup input changed')
    manifest = json.loads(manifest_path.read_text())
    fs = load('reviewed_sensor_fileserver',
              root / 'usr/libexec/oneplus13-ram-sensor-fileserver.py')
    entries = fs.archive_entries(archive, manifest)

    if existing_tree(root, entries):
        verify_tree(root, entries)
    else:
        fs.install(root, entries, chown=chown)
        verify_tree(root, entries)
    data = {
        'scope': 'ONEPLUS13_RAM_DESKTOP_SENSOR_RUNTIME_READY',
        'archive_sha256': doc['inputs']['archive']['sha256'],
        'manifest_sha256': doc['inputs']['manifest']['sha256'],
        'native_elf_count': manifest['native_elf_count'],
        'data_files': manifest['text_data_files'],
        'attach_started': False,
        'physical_storage_writes': 0,
    }
    marker.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    marker.write_text(json.dumps(data, sort_keys=True) + '\n')
    marker.chmod(0o644)
    return data


def service_active(run=subprocess.run):
    result = run(['systemctl', 'is-active', '--quiet', FILESERVER, PROXY],
                 capture_output=True, text=True, timeout=6)
    if result.returncode:
        raise ValueError('Desktop sensor services are not active')


def system_orientation(bus):
    import gi
    gi.require_version('GLib', '2.0')
    from gi.repository import GLib
    value = bus.call_sync(
        'net.hadess.SensorProxy', '/net/hadess/SensorProxy',
        'org.freedesktop.DBus.Properties', 'Get',
        GLib.Variant('(ss)', ('net.hadess.SensorProxy',
                              'AccelerometerOrientation')),
        GLib.VariantType.new('(v)'), 0, 2000, None)
    orientation = value.unpack()[0]
    if orientation not in {'undefined', 'normal', 'bottom-up', 'left-up', 'right-up'}:
        raise ValueError('Unexpected SensorProxy orientation')
    return orientation


def display_transforms(bus):
    import gi
    gi.require_version('GLib', '2.0')
    from gi.repository import GLib
    value = bus.call_sync(
        'org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig',
        'org.gnome.Mutter.DisplayConfig', 'GetCurrentState', None,
        GLib.VariantType.new('(ua((ssss)a(siiddada{sv})a{sv})a(iiduba(ssss)a{sv})a{sv})'),
        0, 2000, None).unpack()
    transforms = []
    for monitor in value[1]:
        if len(monitor) < 4 or type(monitor[3]) is not int:
            raise ValueError('Unrecognized Mutter logical-monitor state')
        transforms.append(monitor[3])
    if not transforms or any(value not in (0, 1, 2, 3) for value in transforms):
        raise ValueError('Unrecognized Mutter monitor transform')
    return tuple(transforms)


def collect(seconds, orientation, transforms, clock=time.monotonic, sleep=time.sleep):
    if type(seconds) is not int or seconds != 20:
        raise ValueError('Only the twenty-second desktop orientation window is reviewed')
    orientations = []
    display_states = []
    samples = 0
    until = clock() + seconds
    while clock() < until:
        current_orientation = orientation()
        current_transforms = transforms()
        samples += 1
        if samples > 128:
            raise ValueError('Orientation sample bound exceeded')
        if not orientations or orientations[-1] != current_orientation:
            orientations.append(current_orientation)
        if not display_states or display_states[-1] != list(current_transforms):
            display_states.append(list(current_transforms))
        sleep(min(.25, max(0, until - clock())))
    orientation_set = set(orientations)
    transform_set = {value for state in display_states for value in state}
    passed = (samples >= 20 and len(orientation_set) >= 3
              and len(transform_set) >= 2)
    return {
        'scope': 'AUTOMATIC_DESKTOP_ORIENTATION_OBSERVATION',
        'seconds': seconds,
        'samples': samples,
        'orientation_sequence': orientations,
        'display_transform_sequence': display_states,
        'distinct_orientations': sorted(orientation_set),
        'distinct_display_transforms': sorted(transform_set),
        'automatic_rotation_pass': passed,
        'physical_axes_calibration_accepted': False,
    }


def check(seconds=20, system_bus=None, session_bus=None):
    if not MARKER.is_file():
        raise ValueError('Sensor runtime setup marker missing')
    data = json.loads(MARKER.read_text())
    if data.get('scope') != 'ONEPLUS13_RAM_DESKTOP_SENSOR_RUNTIME_READY':
        raise ValueError('Sensor runtime setup marker changed')
    service_active()
    import gi
    gi.require_version('Gio', '2.0')
    from gi.repository import Gio
    system_bus = system_bus or Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
    session_bus = session_bus or Gio.bus_get_sync(Gio.BusType.SESSION, None)
    result = collect(seconds,
                     lambda: system_orientation(system_bus),
                     lambda: display_transforms(session_bus))
    if not result['automatic_rotation_pass']:
        raise ValueError('Automatic desktop rotation transition incomplete')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('setup', 'check'))
    parser.add_argument('--seconds', type=int, default=20)
    args = parser.parse_args()
    try:
        if args.mode == 'setup':
            if os.geteuid() != 0:
                raise ValueError('Sensor setup requires root')
            result = setup()
        else:
            result = check(args.seconds)
        print('RAM_SENSOR_DESKTOP_RESULT ' + json.dumps(result, sort_keys=True), flush=True)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        print('RAM_SENSOR_DESKTOP_FAILED ' + json.dumps({
            'category': type(exc).__name__,
            'reason': str(exc) if isinstance(exc, ValueError) else 'sensor desktop runtime unavailable',
        }, sort_keys=True), flush=True)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
