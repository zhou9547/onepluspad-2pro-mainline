#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Inspect compiled outputs; QEMU proves userspace only, never phone hardware."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import stat
import tarfile

from common import boot_sections, read_cpio, sha256

REQUIRED = ['ARCH_QCOM', 'ARCH_VEXPRESS', 'BLK_DEV_INITRD', 'RD_GZIP',
            'DEVTMPFS', 'DEVTMPFS_MOUNT', 'TMPFS', 'CONFIGFS_FS', 'USB_GADGET',
            'USB_CONFIGFS', 'USB_CONFIGFS_NCM', 'USB_CONFIGFS_ACM', 'USB_DWC3', 'USB_DWC3_QCOM',
            'PHY_QCOM_M31_EUSB', 'PHY_QCOM_EUSB2_REPEATER', 'PINCTRL_SM8750',
            'SM_GCC_8750', 'SM_TCSRCC_8750', 'REGULATOR_QCOM_RPMH',
            'QCOM_COMMAND_DB', 'QCOM_RPMH', 'QCOM_SMEM', 'QCOM_RPMHPD',
            'INTERCONNECT_QCOM_SM8750', 'SCSI_UFS_QCOM', 'PHY_QCOM_QMP_UFS']


def check_config(path):
    settings = set(path.read_text().splitlines())
    missing = [name for name in REQUIRED if f'CONFIG_{name}=y' not in settings]
    if missing:
        raise ValueError(f'Required early-boot drivers are not built in: {missing}')
    unrelated = ['ARCH_APPLE', 'ARCH_MEDIATEK', 'ARCH_ROCKCHIP', 'ARCH_TEGRA',
                 'ARCH_EXYNOS', 'ARCH_RENESAS', 'ARCH_MESON', 'ARCH_SUNXI']
    enabled = [name for name in unrelated if f'CONFIG_{name}=y' in settings]
    if enabled:
        raise ValueError(f'Unrelated platform families enabled by mistake: {enabled}')


def verify_artifacts(out):
    manifest = json.loads((out / 'manifest.json').read_text())
    if manifest['device'] != 'oneplus,dodge' or manifest['hardware_tested'] is not False:
        raise ValueError('Wrong device or unsupported hardware claim')
    for name, expected in manifest['files'].items():
        if Path(name).name != name or name in {'.', '..'}:
            raise ValueError('Unsafe manifest filename')
        path = out / name
        if path.stat().st_size != expected['size'] or sha256(path) != expected['sha256']:
            raise ValueError(f'Artifact hash/size mismatch: {name}')
    check_config(out / 'kernel.config')
    image = (out / 'Image').read_bytes()
    if len(image) < 64 or image[56:60] != b'ARM\x64':
        raise ValueError('Invalid ARM64 Image magic')
    if gzip.decompress((out / 'Image.gz').read_bytes()) != image:
        raise ValueError('Compressed Image differs from Image')
    sections = boot_sections((out / 'boot-oneplus13-ram-experimental.img').read_bytes())
    for part, filename in [('kernel', 'Image.gz'), ('ramdisk', 'initramfs.cpio.gz'),
                           ('dtb', 'sm8750-oneplus-dodge.dtb')]:
        if sections[part] != (out / filename).read_bytes():
            raise ValueError(f'Boot image section differs: {part}')
    cpio = read_cpio(gzip.decompress(sections['ramdisk']))
    if hashlib.sha256(cpio['init']['data']).hexdigest() != manifest['phone_inputs_sha256']['init']:
        raise ValueError('Packaged init differs from phone source')
    if not cpio['init']['mode'] & stat.S_IXUSR:
        raise ValueError('Packaged init is not executable')
    if hashlib.sha256(cpio['bin/busybox']['data']).hexdigest() != manifest['tools_sha256']['busybox']:
        raise ValueError('Packaged BusyBox differs from pinned binary')
    console = cpio['dev/console']
    if stat.S_IFMT(console['mode']) != stat.S_IFCHR or (console['major'], console['minor']) != (5, 1):
        raise ValueError('Wrong console device in initramfs')
    with tarfile.open(out / 'modules.tar.gz') as archive:
        names = [member.name for member in archive.getmembers()]
        if any(Path(name).is_absolute() or '..' in Path(name).parts for name in names):
            raise ValueError('Unsafe module archive path')
        prefix = 'lib/modules/' + manifest['kernel_release'] + '/'
        if not any(name.removeprefix('./').startswith(prefix) and
                   name.endswith(('.ko', '.ko.zst', '.ko.xz', '.ko.gz')) for name in names):
            raise ValueError('Module archive does not match kernel release')
    dtb = out / 'sm8750-oneplus-dodge.dtb'
    compatible = subprocess.check_output(['fdtget', str(dtb), '/', 'compatible'], text=True)
    if compatible.strip().split() != ['oneplus,dodge', 'qcom,sm8750']:
        raise ValueError('Wrong DTB compatible')
    # Re-decompile with an independent dtc invocation: rejects damaged binary trees.
    subprocess.run(['dtc', '-q', '-I', 'dtb', '-O', 'dts', '-o', '/dev/null', str(dtb)], check=True)
    return {'status': 'OFFLINE_VERIFIED_NOT_DEVICE_TESTED', 'hardware_tested': False,
            'kernel_release': manifest['kernel_release'],
            'boot_sha256': sha256(out / 'boot-oneplus13-ram-experimental.img'),
            'checks': ['artifact sizes and SHA256', 'required built-in dependencies',
                       'ARM64 Image magic', 'Image gzip roundtrip', 'Android v2 section roundtrip',
                       'independent cpio inspection: init, BusyBox, console', 'matching module release archive',
                       'DTB identity and independent decompilation']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--artifacts', type=Path)
    parser.add_argument('--qemu', action='store_true')
    args = parser.parse_args()
    if args.config:
        check_config(args.config)
    if args.artifacts:
        out = args.artifacts.resolve()
        result = verify_artifacts(out)
        if args.qemu:
            command = ['qemu-system-aarch64', '-machine', 'virt', '-cpu', 'cortex-a76',
                       '-m', '1024', '-smp', '2', '-nographic', '-no-reboot',
                       '-kernel', str(out / 'Image'), '-initrd', str(out / 'initramfs.cpio.gz'),
                       '-append', 'console=ttyAMA0 rdinit=/init panic=3 oneplus13.smoke=1']
            proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=90, text=True)
            (out / 'qemu.log').write_text(proc.stdout)
            if proc.returncode or 'ONEPLUS13_QEMU_INIT_OK' not in proc.stdout:
                print(proc.stdout[-10000:])
                raise SystemExit('QEMU initramfs smoke test failed')
            result['checks'].append('QEMU virt boots the exact Image/initramfs and reaches init marker')
            result['qemu_scope'] = 'ARM64 userspace only; not an SM8750 hardware emulator'
        (out / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
        (out / 'SHA256SUMS').write_text(''.join(
            f'{sha256(path)}  {path.name}\n' for path in sorted(out.iterdir())
            if path.is_file() and path.name != 'SHA256SUMS'))
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
