#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One explicit generic CEC-core prerequisite, without a hardware CEC adapter.

The caller binds the exact kernel module and policy hashes before this load.
After registration, ordinary CEC dependency requests become a no-op. Every
other peripheral denial remains byte-identical in the RAM overlay.
No display module, adapter, message, unload or retry is requested here.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path

def command(args):
    return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT,timeout=8).strip()

def no_adapter(root):
    if any((root/'dev').glob('cec[0-9]*')):
        raise ValueError('Hardware CEC adapter unexpectedly exists')
    bus=root/'sys/bus/cec/devices'
    if bus.exists() and any(bus.iterdir()):
        raise ValueError('CEC bus unexpectedly contains an adapter')

POLICY='etc/modprobe.d/91-oneplus13-unreviewed-peripherals.conf'

def validate(root,release,digest,policy_sha,run=command):
    root=Path(root)
    if not re.fullmatch(r'[A-Za-z0-9._+-]{1,160}',release) or not all(re.fullmatch(r'[0-9a-f]{64}',value) for value in [digest,policy_sha]):
        raise ValueError('Invalid bound module identity')
    if not (root/'run/oneplus13/ram-session').is_file():
        raise ValueError('RAM marker missing')
    if not any(len(parts:=line.split())>=3 and parts[1:3]==['/','overlay']
               for line in (root/'proc/mounts').read_text().splitlines()):
        raise ValueError('RAM overlay missing')
    blocks=[p for p in (root/'sys/class/block').iterdir() if not p.name.startswith(('ram','zram','loop'))]
    if not blocks or any((p/'ro').read_text().strip()!='1' for p in blocks):
        raise ValueError('Physical block protection missing')
    for unit in ['oneplus13-ram-guard.service','oneplus13-ram-deadline.timer']:
        if run(['/usr/bin/systemctl','is-active',unit])!='active':
            raise ValueError('RAM recovery service inactive')
    module=root/('usr/lib/modules/'+release+'/kernel/drivers/media/cec/core/cec.ko')
    if module.is_symlink() or module.stat().st_size>1024*1024:
        raise ValueError('Unexpected CEC module file')
    if hashlib.sha256(module.read_bytes()).hexdigest()!=digest:
        raise ValueError('Bound CEC module hash mismatch')
    if not run(['/usr/sbin/modinfo','-k',release,'-F','vermagic','cec']).startswith(release+' '):
        raise ValueError('CEC module release mismatch')
    if 'install cec /bin/false' not in [line.strip() for line in run(['/usr/sbin/modprobe','-c']).splitlines()]:
        raise ValueError('Ordinary CEC load denial missing')
    policy=root/POLICY
    if policy.is_symlink() or hashlib.sha256(policy.read_bytes()).hexdigest()!=policy_sha:
        raise ValueError('Exact original peripheral policy required')
    if policy.read_bytes().count(b'install cec /bin/false\n')!=1:
        raise ValueError('Single exact CEC install rule required')
    if (root/'sys/module/cec').exists():
        raise ValueError('CEC was already loaded before explicit prerequisite')
    no_adapter(root)

def prepare(root,release,digest,policy_sha,run=command):
    root=Path(root)
    if run is command and (root!=Path('/') or os.uname().release!=release):
        raise ValueError('Real loading requires current RAM root and release')
    validate(root,release,digest,policy_sha,run)
    marker=root/'run/oneplus13/cec-core-load-attempted'
    # Retain this marker even when kmod fails. Never retry an attempted load.
    with marker.open('x'):pass
    run(['/usr/sbin/modprobe','--ignore-install','cec'])
    if not (root/'sys/module/cec').is_dir():
        raise ValueError('Generic CEC core did not register')
    no_adapter(root)
    # kmod executes install rules even for an already loaded dependency.
    # Permit only a no-op after the exact generic core is visibly registered.
    policy=root/POLICY;original=policy.read_bytes()
    updated=original.replace(b'install cec /bin/false\n',b'install cec /bin/true\n',1)
    policy.write_bytes(updated)
    if 'install cec /bin/true' not in [line.strip() for line in run(['/usr/sbin/modprobe','-c']).splitlines()]:
        raise ValueError('Registered CEC dependency no-op not effective')
    return {'scope':'EXPLICIT_GENERIC_CEC_CORE_ONLY','cec_module_sha256':digest,
        'ordinary_cec_requests_noop_after_registration':True,'other_peripheral_denials_unchanged':True,
        'original_policy_sha256':policy_sha,'runtime_policy_sha256':hashlib.sha256(updated).hexdigest(),'hardware_cec_adapters':0,
        'display_loaded':False,'cec_message_or_adapter_control_requested':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--release',required=True);p.add_argument('--sha256',required=True)
    p.add_argument('--policy-sha256',required=True);a=p.parse_args()
    try:
        if os.geteuid()!=0:raise ValueError('Root required')
        result=prepare(Path('/'),a.release,a.sha256,a.policy_sha256)
        print('RAM_DISPLAY_PREREQUISITE_RESULT '+json.dumps(result,sort_keys=True))
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        print('RAM_DISPLAY_PREREQUISITE_FAILED '+type(error).__name__)
        return 1
    return 0
if __name__=='__main__':raise SystemExit(main())
