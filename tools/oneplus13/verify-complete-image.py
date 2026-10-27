#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Run the exact complete RAM image under QEMU; no physical device operations."""
import argparse,json,subprocess,time
from pathlib import Path
from common import sha256

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kernel',type=Path,required=True);p.add_argument('--image',type=Path,required=True)
    p.add_argument('--static-only',action='store_true',help='Verify packaging without repeating a runtime boot')
    a=p.parse_args();root=a.image.resolve();kernel=a.kernel.resolve()
    m=json.loads((root/'manifest.json').read_text())
    for name,key in [('rootfs.squashfs','rootfs_sha256'),('boot-desktop-ram-experimental.img','boot_image_sha256')]:
        if sha256(root/name)!=m[key]:raise ValueError('Complete artifact changed')
    if sha256(kernel/'Image.gz')!=m['kernel_sha256']:raise ValueError('Wrong kernel')
    # Inspect the actual delivered SquashFS, rather than just staging inputs.
    release=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),'usr/lib/oneplus13-desktop/kernel-release'],text=True).strip()
    if release!=m['kernel_release']:raise ValueError('Delivered kernel/module release mismatch')
    data=json.loads(subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),'usr/lib/oneplus13-desktop/private-firmware.json']))
    import hashlib
    for name,digest in data.items():
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),'usr/lib/firmware/'+name])
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('Delivered firmware changed: '+name)
    ssc_files=m.get('ssc_probe_files',{})
    required_ssc={'usr/lib/oneplus13-ssc/phone-ssc-probe-arm64.tar.gz',
                  'usr/lib/oneplus13-ssc/phone-ssc-probe-manifest.json',
                  'usr/lib/oneplus13-ssc/verification.json',
                  'usr/libexec/oneplus13-ram-ssc-metadata.py'}
    if set(ssc_files)!=required_ssc or m.get('ssc_probe_auto_started') is not False:
        raise ValueError('Missing isolated SSC metadata probe')
    for name,digest in ssc_files.items():
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('Delivered SSC input changed')
    static={'scope':'COMPLETE_IMAGE_STATIC_PACKAGE_VERIFICATION','pass':True,'source_commit':m['source_commit'],
            'rootfs_sha256':m['rootfs_sha256'],'boot_image_sha256':m['boot_image_sha256'],
            'firmware_files_verified':len(data),'kernel_module_release_match':True,
            'ssc_probe_files_verified':len(ssc_files),'ssc_probe_auto_started':False,
            'qemu_executed':not a.static_only,'hardware_tested':False,'phone_operations':0}
    (root/'complete-verification.json').write_text(json.dumps(static,indent=2)+'\n')
    if a.static_only:
        (root/'SHA256SUMS').write_text(''.join(f'{sha256(x)}  {x.name}\n' for x in sorted(root.iterdir()) if x.is_file() and x.name!='SHA256SUMS'))
        print(json.dumps(static,indent=2));return
    cmd=['qemu-system-aarch64','-machine','virt','-cpu','cortex-a76','-m','6144','-smp','2','-nographic','-no-reboot','-nic','none',
         '-kernel',str(kernel/'Image'),'-initrd',str(root/'initramfs-desktop.cpio.gz'),
         '-drive','file='+str(root/'rootfs.squashfs')+',format=raw,if=none,readonly=on,id=rootfs',
         '-device','virtio-blk-device,drive=rootfs','-append','console=ttyAMA0 '+m['cmdline']+' oneplus13.desktop.qemu=1']
    start=time.monotonic()
    with (root/'qemu-complete.log').open('wb') as log:
        try:rc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=320).returncode
        except subprocess.TimeoutExpired:rc=124
    text=(root/'qemu-complete.log').read_text(errors='replace')
    # PRIVATE is a historical observer marker for the real calibration handoff,
    # as opposed to the synthetic public-root fixture. This data is now published.
    markers=['ONEPLUS13_DISPLAY_AUTOLOAD_BLOCKED','ONEPLUS13_NATIVE_RUNTIME_GUARDS_OFFLINE_OK',
             'ONEPLUS13_NATIVE_PREFLIGHT_OFFLINE_OK','ONEPLUS13_PRIVATE_NATIVE_HANDOFF_OK',
             'ONEPLUS13_DESKTOP_HANDOFF_OK','ONEPLUS13_QEMU_DEADLINE_FIRED','reboot: Restarting system']
    passed=rc==0 and all(v in text for v in markers) and all(text.index(x)<text.index(y) for x,y in zip(markers,markers[1:]))
    proof={'scope':'COMPLETE_IMAGE_QEMU_HANDOFF_AND_DEADLINE_NOT_HARDWARE_EMULATION','pass':passed,'returncode':rc,
           'source_commit':m['source_commit'],'rootfs_sha256':m['rootfs_sha256'],'boot_image_sha256':m['boot_image_sha256'],
           'kernel_image_sha256':sha256(kernel/'Image'),'elapsed_seconds':round(time.monotonic()-start,1),
           'markers':{v:v in text for v in markers},'phone_operations':0,'hardware_tested':False}
    (root/'qemu-complete-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    if not passed:raise SystemExit('Exact complete-rootfs QEMU handoff/deadline failed; log preserved')
    (root/'SHA256SUMS').write_text(''.join(f'{sha256(x)}  {x.name}\n' for x in sorted(root.iterdir()) if x.is_file() and x.name!='SHA256SUMS'))
    print(json.dumps(proof,indent=2))

if __name__=='__main__':main()
