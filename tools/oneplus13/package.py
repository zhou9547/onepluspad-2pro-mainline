#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Package an explicitly experimental RAM image; never uses Pad stock images."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import tarfile
import urllib.request

from common import make_cpio, sha256

REPO = Path(__file__).resolve().parents[2]


def run(*args):
    return subprocess.check_output(args, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kernel-out', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    cache = REPO / 'out/oneplus13-tools'
    cache.mkdir(parents=True, exist_ok=True)
    inputs = json.loads((REPO / 'kernel/source.json').read_text())['tool_inputs']
    bb = inputs['busybox-arm64']
    deb = cache / bb['archive']
    if not deb.is_file() or sha256(deb) != bb['archive_sha256']:
        url = bb['url'].replace('http://', 'https://', 1)
        with urllib.request.urlopen(url, timeout=120) as stream, deb.open('wb') as target:
            shutil.copyfileobj(stream, target)
    if sha256(deb) != bb['archive_sha256']:
        raise SystemExit('BusyBox archive checksum mismatch')
    subprocess.run(['dpkg-deb', '-x', str(deb), str(cache / 'busybox-root')], check=True)
    busybox = cache / 'busybox-root' / bb['archive_path']
    if sha256(busybox) != bb['sha256']:
        raise SystemExit('BusyBox binary checksum mismatch')
    command = [str(busybox), '--list']
    if platform.machine() not in {'aarch64', 'arm64'}:
        command.insert(0, 'qemu-aarch64')
    applets = run(*command).splitlines()
    required = {'sh', 'mount', 'blockdev', 'reboot', 'poweroff', 'ip', 'httpd',
                'telnetd', 'udhcpd', 'setsid', 'cttyhack', 'dmesg'}
    if not required <= set(applets):
        raise SystemExit(f'Missing BusyBox applets: {required - set(applets)}')
    entries = []
    for name in ['bin', 'sbin', 'dev', 'proc', 'sys', 'run', 'tmp', 'etc']:
        entries.append((name, stat.S_IFDIR | 0o755, b'', 0, 0))
    entries += [('dev/console', stat.S_IFCHR | 0o600, b'', 5, 1),
                ('dev/null', stat.S_IFCHR | 0o666, b'', 1, 3),
                ('bin/busybox', stat.S_IFREG | 0o755, busybox.read_bytes(), 0, 0),
                ('init', stat.S_IFREG | 0o755,
                 (REPO / 'devices/oneplus13/init').read_bytes(), 0, 0)]
    for applet in applets:
        entries.append((f'bin/{applet}', stat.S_IFLNK | 0o777, b'busybox', 0, 0))
    # sbin paths are used by shutdown helpers and interactive diagnostics.
    for applet in ['reboot', 'poweroff']:
        entries.append((f'sbin/{applet}', stat.S_IFLNK | 0o777, b'../bin/busybox', 0, 0))
    (out / 'initramfs.cpio.gz').write_bytes(gzip.compress(make_cpio(entries), mtime=0))
    mk = inputs['mkbootimg.py']
    archive = REPO / mk['bundled_archive']
    if sha256(archive) != mk['archive_sha256']:
        raise SystemExit('mkbootimg archive checksum mismatch')
    with tarfile.open(archive) as source:
        source.extractall(cache / 'mkbootimg', filter='data')
    mkboot = cache / 'mkbootimg/mkbootimg.py'
    if sha256(mkboot) != mk['sha256']:
        raise SystemExit('mkbootimg script checksum mismatch')
    cmdline = 'rdinit=/init panic=15 oneplus13.watchdog=300'
    subprocess.run(['python3', str(mkboot), '--header_version', '2',
                    '--pagesize', '4096', '--base', '0',
                    '--kernel_offset', '0x00008000', '--ramdisk_offset', '0x01000000',
                    '--tags_offset', '0x00000100', '--dtb_offset', '0x01f00000',
                    '--kernel', str(out / 'Image.gz'),
                    '--ramdisk', str(out / 'initramfs.cpio.gz'),
                    '--dtb', str(out / 'sm8750-oneplus-dodge.dtb'),
                    '--cmdline', cmdline,
                    '--output', str(out / 'boot-oneplus13-ram-experimental.img')], check=True)
    source = json.loads((REPO / 'devices/oneplus13/source.json').read_text())
    shutil.copy2(REPO / 'devices/oneplus13/source.json', out / 'source.json')
    shutil.copy2(REPO / 'docs/oneplus13/README.md', out / 'README.md')
    shutil.copy2(REPO / 'COPYING' if (REPO / 'COPYING').exists() else REPO / 'LICENSE',
                 out / 'LICENSE')
    files = {p.name: {'sha256': sha256(p), 'size': p.stat().st_size}
             for p in sorted(out.iterdir()) if p.is_file() and
             p.name not in {'manifest.json', 'SHA256SUMS', 'verification.json', 'qemu.log'}}
    manifest = {
        'status': 'OFFLINE_BUILD_ONLY_NOT_DEVICE_TESTED',
        'device': source['device'], 'kernel_commit': source['kernel']['commit'],
        'integration_commit': run('git', '-C', str(REPO), 'rev-parse', 'HEAD'),
        'kernel_release': (out / 'kernel.release').read_text().strip(),
        'toolchain': run('aarch64-linux-gnu-gcc', '--version').splitlines()[0],
        'cmdline': cmdline,
        'boot_scope': 'Experimental fastboot RAM format; ABL acceptance is unverified. Never flash.',
        'stock_overlay_compatibility': 'NOT_VERIFIED_REQUIRES_PHONE_STOCK_DTBO',
        'hardware_tested': False,
        'phone_inputs_sha256': {
            p.name: sha256(p) for p in sorted((REPO / 'devices/oneplus13').iterdir()) if p.is_file()},
        'files': files}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    checksums = [(sha256(p), p.name) for p in sorted(out.iterdir())
                 if p.is_file() and p.name not in {'SHA256SUMS', 'verification.json', 'qemu.log'}]
    (out / 'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for digest, name in checksums))


if __name__ == '__main__':
    main()
