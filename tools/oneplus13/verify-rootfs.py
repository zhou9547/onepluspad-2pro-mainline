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
    # Require Ubuntu's full desktop metapackage alongside the device additions.
    repo=Path(__file__).resolve().parents[2]
    package_seed=json.loads((repo/'devices/oneplus13/ubuntu.json').read_text())['packages']
    for package in package_seed:
        if package not in packages:
            raise SystemExit(f'Missing required desktop package: {package}')
    for package in ['ubuntu-desktop','ubuntu-desktop-minimal','gnome-initial-setup']:
        if package not in packages:
            raise SystemExit(f'Missing standard Ubuntu desktop package: {package}')
    image = out / 'rootfs.squashfs'
    read = lambda name: subprocess.check_output(['unsquashfs', '-cat', str(image), name])
    if read('etc/machine-id').strip():
        raise SystemExit('Machine identity was embedded into image')
    root = next(line for line in read('etc/shadow').decode().splitlines() if line.startswith('root:'))
    if not root.split(':')[1].startswith(('!', '*')):
        raise SystemExit('Root account is not locked')
    passwd = read('etc/passwd').decode().splitlines()
    if any(1000 <= int(line.split(':')[2]) < 60000 for line in passwd if line):
        raise SystemExit('A regular user was precreated in the rootfs')
    initial_setup=read('usr/libexec/gnome-initial-setup')
    if initial_setup[:5] != b'\x7fELF\x02' or struct.unpack_from('<H', initial_setup, 18)[0] != 183:
        raise SystemExit('GNOME first-user setup binary missing or wrong architecture')
    gdm_config=read('etc/gdm3/custom.conf').decode()
    if '[daemon]' not in gdm_config or 'InitialSetupEnable=true' not in gdm_config:
        raise SystemExit('GDM first-user setup is not explicitly enabled')
    environment=read('etc/environment').decode().splitlines()
    if any(line.startswith(('GTK_IM_MODULE=','QT_IM_MODULE=','XMODIFIERS=')) for line in environment):
        raise SystemExit('A global IM override bypasses the native Wayland input path')
    mobile=read('usr/share/glib-2.0/schemas/90-oneplus13-mobile.gschema.override').decode()
    if '[org.gnome.desktop.a11y.applications]\nscreen-keyboard-enabled=true\n' not in mobile:
        raise SystemExit('Mobile first-user screen keyboard default missing')
    if '[org.gnome.desktop.interface]\ntoolkit-accessibility=true\n' not in mobile:
        raise SystemExit('Mobile accessibility bridge default missing')
    for name in ['gnome-initial-setup', 'gnome-initial-setup-first-login',
                 'gnome-initial-setup-upgrade-login']:
        if 'Environment=GIS_SMALL_SCREEN=1' not in read(
                'usr/lib/systemd/user/'+name+'.service.d/60-oneplus13-small-screen.conf').decode():
            raise SystemExit('Initial Setup small-screen layout missing')
    if 'x-scheme-handler/https=org.gnome.Epiphany.desktop' not in read('etc/xdg/mimeapps.list').decode():
        raise SystemExit('Usable browser default missing')
    for name in ['usr/bin/gnome-shell', 'usr/sbin/gdm3', 'usr/sbin/NetworkManager',
                 'usr/sbin/wpa_supplicant','usr/sbin/iw','usr/bin/bluetoothctl',
                 'usr/bin/bluetooth-sendto','usr/libexec/bluetooth/obexd',
                 'usr/bin/epiphany','usr/bin/gnome-software']:
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
                   'full Ubuntu Desktop metapackages and required runtime packages',
                   'locked root, no precreated desktop user, enabled GDM first-user setup, and empty machine-id',
                   'actual desktop/WiFi/Bluetooth ARM64 ELF binaries',
                   'supplicant and OBEX D-Bus/systemd activation contracts', 'actual Ubuntu os-release']}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
