#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Install opt-in RAM desktop support into the freshly built phone rootfs."""
import argparse
from pathlib import Path
import json
import tarfile
from common import sha256

REPO = Path(__file__).resolve().parents[2]
CONDITION = ('ConditionKernelCommandLine=oneplus13.desktop=1\n'
             'ConditionPathExists=/run/oneplus13/ram-session\n')


def install(root, kernel=None):
    if not root.is_relative_to((REPO/'out').resolve()) or not (root/'etc/os-release').is_file():
        raise ValueError('Expected a fresh phone rootfs staging tree under repository out/')

    def write(name, data, mode=0o644):
        path = root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, newline='\n')
        path.chmod(mode)

    def unit(name, body, target):
        write('usr/lib/systemd/system/'+name, '[Unit]\n'+CONDITION+body)
        link = root/('etc/systemd/system/'+target+'.wants/'+name)
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to('/usr/lib/systemd/system/'+name)

    for name in ['runtime-guard', 'runtime-usb', 'runtime-evidence', 'runtime-serial']:
        write('usr/libexec/oneplus13-'+name,
              (REPO/'devices/oneplus13/desktop'/name).read_text(), 0o755)
    write('usr/lib/oneplus13-desktop/version', '1\n')
    if kernel:
        manifest = json.loads((kernel/'manifest.json').read_text())
        if (manifest['integration_commit'] != 'c2e659aaa062647a206c67edcc421f0fa9931f7a' or
                manifest['device'] != 'oneplus,dodge' or manifest['hardware_tested'] is not False):
            raise ValueError('Desktop requires the pinned verified phone kernel artifact')
        archive = kernel/'modules.tar.gz'
        if sha256(archive) != manifest['files']['modules.tar.gz']['sha256']:
            raise ValueError('Kernel module archive hash mismatch')
        with tarfile.open(archive) as source:
            for member in source.getmembers():
                name = member.name.removeprefix('./')
                if name not in {'.', 'lib', 'lib/modules', 'lib/modules/'+manifest['kernel_release']} and not name.startswith('lib/modules/'+manifest['kernel_release']+'/'):
                    raise ValueError('Unexpected module member')
            source.extractall(root, filter='data')
        write('usr/lib/oneplus13-desktop/kernel-release', manifest['kernel_release']+'\n')
    write('etc/NetworkManager/conf.d/80-oneplus13-ram-usb.conf',
          '[keyfile]\nunmanaged-devices=mac:02:13:00:00:00:01\n')
    write('usr/lib/udev/rules.d/10-oneplus13-ram-storage.rules',
          'ACTION=="add", SUBSYSTEM=="block", KERNEL!="loop*|ram*|zram*", '
          'TEST=="/run/oneplus13/ram-session", ENV{UDISKS_IGNORE}="1", '
          'RUN+="/usr/sbin/blockdev --setro %N"\n')
    unit('oneplus13-ram-guard.service',
         'Description=Protect physical storage during the RAM desktop\n'
         'DefaultDependencies=no\nBefore=sysinit.target systemd-udevd.service systemd-udev-trigger.service\n'
         'IgnoreOnIsolate=yes\nFailureAction=reboot-force\n[Service]\nType=simple\n'
         'ExecStartPre=/usr/libexec/oneplus13-runtime-guard --once\n'
         'ExecStart=/usr/libexec/oneplus13-runtime-guard\n', 'sysinit.target')
    unit('oneplus13-ram-deadline.timer',
         'Description=Bound the complete RAM desktop boot\nDefaultDependencies=no\n'
         'Before=sysinit.target\nIgnoreOnIsolate=yes\n[Timer]\nOnBootSec=900s\n'
         'AccuracySec=1s\nUnit=oneplus13-ram-deadline.service\n', 'sysinit.target')
    write('usr/lib/systemd/system/oneplus13-ram-deadline.service',
          '[Unit]\n'+CONDITION+'Description=End the RAM session\nDefaultDependencies=no\n'
          '[Service]\nType=oneshot\nExecStart=/usr/bin/busybox reboot -f -n\n')
    unit('oneplus13-ram-evidence.service',
         'Description=RAM desktop liveness evidence\nAfter=local-fs.target\n'
         '[Service]\nExecStart=/usr/libexec/oneplus13-runtime-evidence\n', 'multi-user.target')
    unit('oneplus13-ram-usb.service',
         'Description=Retain the phone RAM USB network\nAfter=NetworkManager.service\n'
         'ConditionPathExists=/sys/kernel/config/usb_gadget/oneplus13/UDC\n'
         '[Service]\nType=oneshot\nRemainAfterExit=yes\n'
         'ExecStart=/usr/libexec/oneplus13-runtime-usb\n', 'multi-user.target')
    for name, command in {
        'dhcp': '/usr/bin/busybox udhcpd -f /run/oneplus13/udhcpd.conf',
        'http': '/usr/bin/busybox httpd -f -p 172.16.13.1:8080 -h /run/evidence',
        'shell': '/usr/bin/busybox telnetd -F -b 172.16.13.1:23 -l /bin/sh',
        'serial': '/usr/libexec/oneplus13-runtime-serial',
    }.items():
        unit('oneplus13-ram-'+name+'.service',
             'Description=Explicit RAM USB development '+name+'\n'
             'Requires=oneplus13-ram-usb.service\nAfter=oneplus13-ram-usb.service\n'
             'ConditionPathExists=/sys/kernel/config/usb_gadget/oneplus13/UDC\n'
             '[Service]\nExecStart='+command+'\n', 'multi-user.target')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--kernel', type=Path)
    a = p.parse_args()
    install(a.root.resolve(), a.kernel.resolve() if a.kernel else None)
