#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify a freshly downloaded desktop artifact, without executing its software."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    out = args.directory.resolve()
    for line in (out / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        if Path(name).name != name or name in {'.', '..'}:
            raise SystemExit('Unsafe checksum filename')
        if digest(out / name) != expected:
            raise SystemExit(f'Downloaded artifact checksum mismatch: {name}')
    manifest = json.loads((out / 'manifest.json').read_text())
    if manifest.get('hardware_tested') is not False:
        raise SystemExit('Unexpected hardware support claim')
    for name, expected in manifest['files'].items():
        if Path(name).name != name or name in {'.', '..'}:
            raise SystemExit('Unsafe manifest filename')
        path = out / name
        if path.stat().st_size != expected['size'] or digest(path) != expected['sha256']:
            raise SystemExit(f'Manifest size/hash mismatch: {name}')
    packages = {}
    for line in (out / 'packages.tsv').read_text().splitlines():
        package, version, arch = line.split('\t')
        if arch not in {'arm64', 'all'}:
            raise SystemExit(f'Wrong target package architecture: {package} / {arch}')
        packages[package.split(':')[0]] = version
    # --no-install-recommends requires an explicit complete seed. Checking only
    # NetworkManager misses its WiFi authentication and desktop OBEX services.
    repo=Path(__file__).resolve().parents[2]
    for package in json.loads((repo/'devices/oneplus13/ubuntu.json').read_text())['packages']:
        if package not in packages:
            raise SystemExit(f'Missing required desktop package: {package}')
    image = out / 'rootfs.squashfs'
    read = lambda name: subprocess.check_output(['unsquashfs', '-cat', str(image), name])
    if read('etc/machine-id').strip():
        raise SystemExit('Machine identity was embedded into image')
    root = next(line for line in read('etc/shadow').decode().splitlines() if line.startswith('root:'))
    if not root.split(':')[1].startswith(('!', '*')):
        raise SystemExit('Root account is not locked')
    for name in ['usr/bin/gnome-shell', 'usr/sbin/gdm3', 'usr/sbin/NetworkManager',
                 'usr/sbin/wpa_supplicant','usr/sbin/iw','usr/bin/bluetoothctl',
                 'usr/bin/bluetooth-sendto','usr/libexec/bluetooth/obexd']:
        binary = read(name)
        if binary[:5] != b'\x7fELF\x02' or struct.unpack_from('<H', binary, 18)[0] != 183:
            raise SystemExit(f'Wrong executable architecture: {name}')
    for name,marker in [
        ('usr/share/dbus-1/system-services/fi.w1.wpa_supplicant1.service',b'Name=fi.w1.wpa_supplicant1'),
        ('usr/lib/systemd/system/wpa_supplicant.service',b'BusName=fi.w1.wpa_supplicant1'),
        ('usr/share/dbus-1/services/org.bluez.obex.service',b'Name=org.bluez.obex'),
        ('usr/lib/systemd/user/obex.service',b'BusName=org.bluez.obex')]:
        if marker not in read(name):
            raise SystemExit('Missing or mismatched D-Bus activation contract: '+name)
    if 'VERSION_ID="26.04"' not in read('etc/os-release').decode():
        raise SystemExit('Unexpected Ubuntu release')
    result = {
        'status': 'DOWNLOADED_ROOTFS_OFFLINE_VERIFIED_NOT_DEVICE_TESTED',
        'integration_commit': manifest['integration_commit'],
        'rootfs_sha256': digest(image), 'rootfs_bytes': image.stat().st_size,
        'gnome': (out / 'gnome-version.txt').read_text().strip(),
        'packages': len(packages), 'hardware_tested': False,
        'checks': ['all downloaded SHA256SUMS', 'manifest sizes/hashes', 'all package architectures',
                   'required runtime packages', 'locked root in SquashFS', 'empty machine-id in SquashFS',
                   'actual desktop/WiFi/Bluetooth ARM64 ELF binaries',
                   'supplicant and OBEX D-Bus/systemd activation contracts', 'actual Ubuntu os-release']}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
