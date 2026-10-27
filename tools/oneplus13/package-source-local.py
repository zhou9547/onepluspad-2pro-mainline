#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Package a complete RAM image from fresh builds and verified hardware data.

--qualified-data uses the owner-authorized, scrubbed repository dataset in CI.
--private-inputs preserves local-only packaging for unreviewed owner datasets.
Neither mode contacts a phone or consumes an old kernel/rootfs/script overlay.
"""
import argparse,gzip,importlib,json,os,secrets,shutil,struct,subprocess,sys,tarfile,tempfile
from pathlib import Path
from common import boot_sections,read_cpio,sha256
from native import build_initramfs
from desktop import derive
from stock import Fdt

REPO=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['kernel','desktop','rootfs','output']:p.add_argument('--'+n,required=True,type=Path)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--private-inputs',type=Path)
    group.add_argument('--qualified-data',type=Path)
    p.add_argument('--runtime-checks',choices=['qemu','static'],default='qemu',help='static is the owner-approved default for unchanged qualified runtime inputs in CI')
    a=p.parse_args();kernel=a.kernel.resolve();desktop=a.desktop.resolve();rootfs=a.rootfs.resolve();private=(a.qualified_data or a.private_inputs).resolve();out=a.output.resolve()
    public=a.qualified_data is not None
    if os.geteuid()!=0:raise ValueError('Root required for filesystem packing')
    if out.exists() or (not public and out.is_relative_to(REPO)):raise ValueError('Fresh output required; unreviewed private output must stay outside checkout')
    manifest_name='manifest.json' if public else 'manifest.private.json'
    pin=json.loads((private/manifest_name).read_text())
    expected='ONEPLUS13_QUALIFIED_DATA_V1' if public else 'ONEPLUS13_PRIVATE_DATA_V1'
    if pin['format']!=expected:raise ValueError('Wrong data manifest format')
    if public:
        if private!=(REPO/'devices/oneplus13/qualified-data').resolve():raise ValueError('CI accepts only the reviewed repository dataset')
        from verify_qualified_data import verify
        verify(private)
    for name,item in pin['files'].items():
        if Path(name).is_absolute() or '..' in Path(name).parts or (private/name).is_symlink():raise ValueError('Unsafe private data path')
        if sha256(private/name)!=item['sha256'] or (private/name).stat().st_size!=item['bytes']:raise ValueError('Changed private input')
    km=json.loads((kernel/'manifest.json').read_text());dm=json.loads((desktop/'manifest.json').read_text());rm=json.loads((rootfs/'manifest.json').read_text())
    if len({km['integration_commit'],dm['integration_commit'],rm['integration_commit']})!=1:raise ValueError('Public components must share one source commit')
    if a.runtime_checks=='static' and not public:raise ValueError('Static-only packaging is limited to the reviewed repository dataset')
    if a.runtime_checks=='qemu' and not all(dm.get(k) is True for k in ['qemu_handoff_verified','qemu_deadline_expiry_verified','qemu_native_preflight_runtime_guards_verified']):raise ValueError('Fresh complete-rootfs QEMU handoff/recovery required')
    for name in ['Image','Image.gz','initramfs.cpio.gz','modules.tar.gz','sm8750-oneplus-dodge-native.dtb']:
        if sha256(kernel/name)!=km['files'][name]['sha256']:raise ValueError('Kernel artifact changed')
    if sha256(rootfs/'rootfs.squashfs')!=rm['rootfs_sha256'] or sha256(rootfs/'rootfs.squashfs')!=dm['rootfs_sha256']:raise ValueError('QEMU rootfs differs')
    if sha256(kernel/'sm8750-oneplus-dodge-native.dtb')!=pin['compatible_public_native_dtb_sha256']:raise ValueError('Private calibration must be re-reviewed for this new DTB')
    if km['kernel_release']!=rm['kernel_release']:raise ValueError('Kernel/rootfs module mismatch')
    release=km['kernel_release'];out.mkdir(parents=True)
    # Ubuntu contains case-distinct paths (for example Perl Sys and sys).
    # Never unpack a Linux rootfs onto a case-insensitive Windows/DrvFS tree.
    staging=tempfile.TemporaryDirectory(prefix='oneplus13-private-rootfs-',dir='/var/tmp')
    stage=Path(staging.name)/'rootfs'
    subprocess.run(['unsquashfs','-no-progress','-processors','2','-d',str(stage),str(rootfs/'rootfs.squashfs')],check=True)
    for name,item in pin['files'].items():
        if not name.startswith('firmware/'):continue
        dest=stage/'usr/lib/firmware'/name.removeprefix('firmware/')
        if not dest.resolve().is_relative_to(stage):raise ValueError('Firmware target escapes private staging')
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(private/name,dest);dest.chmod(0o644)
    firmware_hashes={name.removeprefix('firmware/'):item['sha256'] for name,item in pin['files'].items() if name.startswith('firmware/')}
    (stage/'usr/lib/oneplus13-desktop/private-firmware.json').write_text(json.dumps(firmware_hashes,indent=2)+'\n')
    bindings={'kernel_release':release,'firmware_sha256':firmware_hashes}
    for key,name in {'CPUCP_MODULE_SHA256':'mailbox/qcom-cpucp-mbox.ko','SOCINFO_MODULE_SHA256':'soc/qcom/socinfo.ko',
        'CEC_MODULE_SHA256':'media/cec/core/cec.ko','UBWC_MODULE_SHA256':'soc/qcom/ubwc_config.ko'}.items():
        bindings[key]=sha256(stage/'usr/lib/modules'/release/'kernel/drivers'/name)
    bindings['MODULE_POLICY_SHA256']=sha256(stage/'etc/modprobe.d/91-oneplus13-unreviewed-peripherals.conf')
    (stage/'usr/lib/oneplus13-desktop/runtime-bindings.private.json').write_text(json.dumps(bindings,indent=2)+'\n')
    dest=stage/'usr/libexec/oneplus13-qualified-bringup'
    shutil.copyfile(REPO/'devices/oneplus13/desktop/qualified-bringup',dest);dest.chmod(0o755)
    # These scripts are repository source, installed in the image rather than
    # supplied by old host overlays during the hardware test.
    for name in ['automatic-wifi-check.py','wifi-radio-report.py','wifi-band-cache.py','ram-wifi-quiescent.py','ram-kernel-health.py','ram-clock-bridge.py','ram-desktop-check.py','ram-platform-prerequisites.sh','ram-display-prerequisites.py']:
        dest=stage/'usr/libexec'/('oneplus13-'+name)
        shutil.copyfile(REPO/'tools/oneplus13'/name,dest);dest.chmod(0o755)
    # A source-bound probe is available for an explicitly reviewed metadata
    # test. It is never auto-started and contains no registry or measurement API.
    ssc=REPO/'out/phone-ssc'
    evidence=json.loads((ssc/'verification.json').read_text())
    ssc_manifest=ssc/'phone-ssc-probe-manifest.json'
    ssc_archive=ssc/'phone-ssc-probe-arm64.tar.gz'
    metadata=json.loads(ssc_manifest.read_text())
    if (evidence.get('integration_commit')!=km['integration_commit']
        or metadata.get('integration_commit')!=km['integration_commit']
        or evidence.get('native_arm64') is not True or evidence.get('host_check_only') is not False
        or evidence.get('typed_sensor_properties_regression_pass') is not True
        or evidence.get('test_counts')!={'release':4,'sanitized':4}):
        raise ValueError('SSC probe must pass native checks at this source commit')
    importlib.import_module('ram-ssc-metadata').entries(ssc_archive,metadata)
    ssc_root=stage/'usr/lib/oneplus13-ssc';ssc_root.mkdir()
    ssc_hashes={}
    for path in [ssc_archive,ssc_manifest,ssc/'verification.json']:
        dest=ssc_root/path.name;shutil.copyfile(path,dest);dest.chmod(0o644)
        ssc_hashes[str(dest.relative_to(stage))]=sha256(dest)
    dest=stage/'usr/libexec/oneplus13-ram-ssc-metadata.py'
    shutil.copyfile(REPO/'tools/oneplus13/ram-ssc-metadata.py',dest);dest.chmod(0o755)
    ssc_hashes[str(dest.relative_to(stage))]=sha256(dest)
    image_rootfs=out/'rootfs.squashfs'
    subprocess.run(['mksquashfs',str(stage),str(image_rootfs),'-noappend','-comp','zstd','-processors','2','-mkfs-time','0','-all-time','0','-no-progress'],check=True)
    staging.cleanup()
    native_helper=(REPO/'devices/oneplus13/start-native-display').read_bytes()
    canonical=(REPO/'devices/oneplus13/native-desktop.py').read_bytes()
    if not native_helper.startswith(b'#!/usr/bin/python3\n') or native_helper.replace(b'# kernel release: @KERNEL_RELEASE@\n',b'')!=canonical:
        raise ValueError('Complete image requires the full qualified Python display helper, not a diagnostic stub')
    packed,_=build_initramfs((kernel/'initramfs.cpio.gz').read_bytes(),(kernel/'modules.tar.gz').read_bytes(),release,None,
        native_helper,encoded_profile=(private/'display-profile.bin').read_bytes())
    packed,derive_report=derive(packed)
    from common import make_cpio
    files=read_cpio(gzip.decompress(packed))
    init=files['init']['data'];old=b'  sleep 900 &\n'
    if init.count(old)!=1:raise ValueError('Unrecognized pre-handoff watchdog')
    files['init']['data']=init.replace(old,b'  sleep 600 &\n')
    packed=gzip.compress(make_cpio([(n,e['mode'],e['data'],e['major'],e['minor']) for n,e in sorted(files.items())]),mtime=0)
    (out/'initramfs-desktop.cpio.gz').write_bytes(packed)
    nonce=secrets.token_hex(12)
    cmdline='rdinit=/init panic=15 oneplus13.desktop=1 oneplus13.rootfs.sha256='+sha256(image_rootfs)+' oneplus13.rootfs.bytes='+str(image_rootfs.stat().st_size)+' oneplus13.session='+nonce
    tree=Fdt((private/'calibrated.dtb').read_bytes());tree.nodes['/chosen']['bootargs']=(cmdline+'\0').encode()
    dtb=out/'sm8750-oneplus-dodge-abl.dtb';dtb.write_bytes(tree.to_blob())
    geometry=json.loads((private/'boot-geometry.json').read_text())
    tool=json.loads((REPO/'kernel/source.json').read_text())['tool_inputs']['mkbootimg.py']
    archive=REPO/tool['bundled_archive']
    if sha256(archive)!=tool['archive_sha256']:raise ValueError('Boot packer archive mismatch')
    image=out/'boot-desktop-ram-experimental.img'
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(archive) as tf:tf.extractall(tmp,filter='data')
        mk=Path(tmp)/'mkbootimg.py'
        if sha256(mk)!=tool['sha256']:raise ValueError('Boot packer script mismatch')
        subprocess.run([sys.executable,str(mk),'--header_version','2','--pagesize','4096','--base','0',
            '--kernel_offset',str(geometry['kernel_addr']),'--ramdisk_offset',str(geometry['ramdisk_addr']),
            '--tags_offset',str(geometry['tags_addr']),'--dtb_offset',str(geometry['dtb_addr']),
            '--kernel',str(kernel/'Image.gz'),'--ramdisk',str(out/'initramfs-desktop.cpio.gz'),'--dtb',str(dtb),
            '--cmdline',cmdline,'--output',str(image)],check=True)
    if boot_sections(image.read_bytes())!={'kernel':(kernel/'Image.gz').read_bytes(),'ramdisk':packed,'dtb':dtb.read_bytes()}:raise ValueError('Independent boot section readback mismatch')
    result={'scope':'QUALIFIED_FRESH_SOURCE_COMPLETE_RAM_IMAGE_NEVER_FLASH' if public else 'PRIVATE_FRESH_SOURCE_COMPLETE_RAM_IMAGE_NEVER_FLASH','source_commit':km['integration_commit'],
        'kernel_release':release,'cmdline':cmdline,'session_identity_nonce':nonce,
        'boot_image_sha256':sha256(image),'boot_image_bytes':image.stat().st_size,
        'rootfs_sha256':sha256(image_rootfs),'rootfs_bytes':image_rootfs.stat().st_size,
        'firmware_files':len(firmware_hashes),'hardware_data_manifest_sha256':sha256(private/manifest_name),
        'qualified_repository_data':public,'private_owner_inputs_required':not public,
        'runtime_checks_requested':a.runtime_checks,'prerequisite_qemu_handoff_pass':dm.get('qemu_handoff_verified',False),
        'public_rootfs_sha256':rm['rootfs_sha256'],'modules_sha256':sha256(kernel/'modules.tar.gz'),
        'kernel_sha256':sha256(kernel/'Image.gz'),'profile_from_existing_qualified_data':True,
        'old_kernel_or_rootfs_used':False,'old_runtime_package_overlay_used':False,
        'full_qualified_python_display_helper':True,
        'initial_watchdog_seconds':600,'post_handoff_deadline_seconds':300,
        'initial_watchdog_survives_switch_root':False,'phone_operations':0,'partition_writes':0,
        'hardware_tested':False,'ssc_probe_files':ssc_hashes,'ssc_probe_auto_started':False,
        'ssc_sensor_property_types_corrected':True}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['scope','source_commit','kernel_release','boot_image_sha256','rootfs_sha256','firmware_files','old_kernel_or_rootfs_used']},indent=2))

if __name__=='__main__':main()
