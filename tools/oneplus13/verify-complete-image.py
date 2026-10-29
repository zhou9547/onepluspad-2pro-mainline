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
    sample_files=m.get('ssc_sample_files',{})
    if set(sample_files)!={'usr/lib/oneplus13-ssc/phone-ssc-samples-arm64.tar.gz',
        'usr/lib/oneplus13-ssc/phone-ssc-samples-manifest.json','usr/libexec/oneplus13-ram-ssc-samples.py'} or m.get('ssc_samples_auto_started') is not False:
        raise ValueError('Missing separately gated SSC sample probe')
    for name,digest in sample_files.items():
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('Delivered sample input changed')
    runtime_files=m.get('sensor_runtime_files',{})
    required_runtime={'usr/lib/oneplus13-sensors/'+n for n in ('phone-sensor-inputs.tar.gz','phone-sensor-inputs-manifest.json','runtime-bindings.json')}
    required_runtime|={'usr/libexec/oneplus13-'+n for n in ('ram-sensor-attach-only.py','ram-sensor-fileserver.py','ram-sensor-discovery.py','ram-ssc-proxy.py','image-sensors-check.py')}
    required_runtime.add('usr/bin/strace')
    if set(runtime_files)!=required_runtime or m.get('sensor_runtime_host_private_inputs_required') is not False or m.get('sensor_runtime_auto_started') is not False:
        raise ValueError('Missing self-contained sensor runtime')
    for name,digest in runtime_files.items():
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('Delivered sensor runtime changed')
    sensor_desktop_files=m.get('sensor_desktop_files',{})
    required_sensor_desktop={
        'usr/libexec/oneplus13-ram-sensor-desktop.py',
        'etc/udev/rules.d/10-oneplus13-fastrpc.rules',
        'usr/share/dbus-1/system.d/net.hadess.SensorProxy.conf',
        'usr/share/polkit-1/actions/net.hadess.SensorProxy.policy',
        'etc/polkit-1/rules.d/49-oneplus13-sensor-proxy.rules',
        'usr/share/dbus-1/system-services/net.hadess.SensorProxy.service',
        'usr/lib/systemd/system/oneplus13-sensor-setup.service',
        'usr/lib/systemd/system/oneplus13-sensor-fileserver.service',
        'usr/lib/systemd/system/oneplus13-sensor-proxy.service',
        'usr/lib/systemd/system/oneplus13-sensor-stack.target'}
    if (set(sensor_desktop_files)!=required_sensor_desktop or
            m.get('sensor_desktop_stack_manual_start_after_adsp') is not True or
            m.get('sensor_desktop_auto_rotation_enabled') is not True or
            m.get('sensor_desktop_hardware_qualified') is not False):
        raise ValueError('Missing reviewed desktop sensor integration')
    for name,digest in sensor_desktop_files.items():
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('Delivered desktop sensor input changed')
    container_files=m.get('container_files',{})
    if set(container_files)!={'usr/lib/oneplus13-container/kernel.config',
            'usr/libexec/oneplus13-container-kernel.py','usr/libexec/oneplus13-ram-container-check.py','etc/docker/daemon.json'} or m.get('container_daemon_auto_started') is not False:
        raise ValueError('Missing gated container support')
    for name,digest in container_files.items():
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('Delivered container input changed')
    config=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),
                                   'usr/lib/oneplus13-container/kernel.config'],text=True)
    import importlib
    importlib.import_module('container-kernel').check_config(config)
    for name in ['usr/bin/docker','usr/bin/dockerd','usr/sbin/xtables-nft-multi','usr/sbin/xtables-legacy-multi']:
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if blob[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(blob[18:20],'little')!=183:
            raise ValueError('Missing native container binary: '+name)
    audio_files=m.get('experimental_audio_files',{})
    for name in ['usr/bin/aplay','usr/bin/amixer']:
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if blob[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(blob[18:20],'little')!=183:
            raise ValueError('Delivered native ALSA tool missing: '+name)
    if len(audio_files)!=4 or m.get('audio_auto_started') is not False or m.get('audio_hardware_qualified') is not False:
        raise ValueError('Missing gated audio candidate')
    for name,digest in audio_files.items():
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('Delivered audio input changed')
    desktop_audio_files=m.get('desktop_audio_files',{})
    required_desktop_audio={'usr/share/alsa/ucm2/conf.d/sm8750/OnePlus13-Audio-Probe.conf',
        'usr/share/alsa/ucm2/Qualcomm/sm8750/OnePlus13/HiFi.conf',
        'usr/lib/oneplus13-audio/95-oneplus13-desktop-audio.conf',
        'usr/libexec/oneplus13-ram-desktop-audio.py','usr/libexec/oneplus13-ram-desktop-volume-check.py',
        'usr/lib/oneplus13-audio/desktop-bindings.json'}
    if set(desktop_audio_files)!=required_desktop_audio or m.get('desktop_audio_auto_started') is not False:
        raise ValueError('Missing explicitly gated desktop audio files')
    for name,digest in desktop_audio_files.items():
        blob=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(blob).hexdigest()!=digest:raise ValueError('Delivered desktop audio changed')
    timezone=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),'etc/timezone'],text=True)
    if timezone!='Asia/Shanghai\n':raise ValueError('Wrong phone timezone')
    microphone_files=m.get('experimental_microphone_files',{})
    if set(microphone_files)!={'usr/lib/firmware/qcom/sm8750/OnePlus13-Audio-Probe-tplg.bin',
            'usr/libexec/oneplus13-ram-microphone-check.py','usr/libexec/oneplus13-ram-acoustic-check.py'} or m.get('microphone_auto_started') is not False:
        raise ValueError('Missing manually gated alternative microphone runtime')
    for name,digest in microphone_files.items():
        raw=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Microphone runtime changed')
    raw=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),'usr/bin/arecord'])
    if raw[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(raw[18:20],'little')!=183:raise ValueError('Native capture tool missing')
    artifacts=m.get('microphone_probe_artifacts',{})
    if set(artifacts)!={'boot-microphone-ram-experimental.img','sm8750-oneplus13-microphone-probe.dtb',
        'microphone-probe-manifest.json','microphone-dtb-review.json'}:raise ValueError('Incomplete alternative microphone boot')
    for name,digest in artifacts.items():
        if sha256(root/name)!=digest:raise ValueError('Alternative microphone artifact changed')
    probe=json.loads((root/'microphone-probe-manifest.json').read_text())
    for key in ('source_commit','kernel_release','rootfs_sha256','modules_sha256','kernel_sha256','experimental_microphone_files'):
        if probe[key]!=m[key]:raise ValueError('Alternative image component mismatch')
    if probe['default_boot_image_sha256']!=m['boot_image_sha256'] or probe['microphone_hardware_qualified'] is not False:
        raise ValueError('Alternative image changed default speaker identity or acceptance')
    import re
    nonce=probe['session_identity_nonce']
    if not re.fullmatch('[a-f0-9]{24}',nonce) or nonce==m['session_identity_nonce']:
        raise ValueError('Alternative image requires a separate session identity')
    if probe['cmdline']!=m['cmdline'].replace('oneplus13.session='+m['session_identity_nonce'],'oneplus13.session='+nonce)+' oneplus13.audio_probe=1':
        raise ValueError('Alternative image changed qualified boot arguments')
    if sha256(root/'boot-microphone-ram-experimental.img')!=probe['boot_image_sha256'] or sha256(root/'sm8750-oneplus13-microphone-probe.dtb')!=probe['dtb_sha256']:
        raise ValueError('Alternative image manifest hashes disagree')
    from common import boot_sections
    from stock import Fdt
    default_sections=boot_sections((root/'boot-desktop-ram-experimental.img').read_bytes())
    probe_sections=boot_sections((root/'boot-microphone-ram-experimental.img').read_bytes())
    for key in ('kernel','ramdisk'):
        if probe_sections[key]!=default_sections[key]:raise ValueError('Alternative kernel/initramfs changed')
    import importlib
    mic_dtb=importlib.import_module('microphone-dtb')
    expected,_=mic_dtb.derive((Path(__file__).resolve().parents[2]/'devices/oneplus13/qualified-data/calibrated.dtb').read_bytes())
    expected_tree=Fdt(expected);expected_tree.nodes['/chosen']['bootargs']=(probe['cmdline']+'\0').encode()
    if probe_sections['dtb']!=(root/'sm8750-oneplus13-microphone-probe.dtb').read_bytes() or Fdt(probe_sections['dtb']).nodes!=expected_tree.nodes:
        raise ValueError('Alternative microphone DTB mismatch')
    policy=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),
        'etc/modprobe.d/91-oneplus13-unreviewed-peripherals.conf'],text=True)
    if 'install snd_soc_aw88461 /bin/false\n' not in policy:
        raise ValueError('Experimental amplifier must require manual activation')
    camera_runtime=m.get('camera_probe_runtime_files',{})
    if set(camera_runtime)!={'usr/libexec/oneplus13-ram-camera-chip-id.py'} or m.get('camera_probe_auto_started') is not False:
        raise ValueError('Camera runtime must be explicit and default-off')
    for name,digest in camera_runtime.items():
        raw=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Camera runtime source hash changed')
    camera_files=m.get('camera_probe_artifacts',{})
    camera_names={'boot-camera-chip-id-ram-experimental.img',
                  'sm8750-oneplus13-camera-chip-id-probe.dtb',
                  'camera-probe-manifest.json','camera-probe-dtb-review.json'}
    if set(camera_files)!=camera_names:raise ValueError('Missing manual camera probe artifacts')
    for name,digest in camera_files.items():
        if sha256(root/name)!=digest:raise ValueError('Camera artifact changed')
    camera=json.loads((root/'camera-probe-manifest.json').read_text())
    if (camera['scope']!='SEPARATE_MANUAL_CAMERA_CHIP_ID_RAM_BOOT_NEVER_FLASH' or
            camera.get('camera_capture_qualified') is not False or
            camera['default_boot_image_sha256']!=m['boot_image_sha256'] or
            camera['rootfs_sha256']!=m['rootfs_sha256'] or
            camera['source_commit']!=m['source_commit']):
        raise ValueError('Camera alternative identity or qualification changed')
    cam_nonce=camera['session_identity_nonce']
    if not re.fullmatch('[a-f0-9]{24}',cam_nonce) or cam_nonce in (nonce,m['session_identity_nonce']):
        raise ValueError('Camera alternative needs a separate session identity')
    if camera['cmdline']!=m['cmdline'].replace('oneplus13.session='+m['session_identity_nonce'],
            'oneplus13.session='+cam_nonce)+' oneplus13.audio_probe=1 oneplus13.camera_probe=1':
        raise ValueError('Camera alternative boot arguments changed')
    if (sha256(root/'boot-camera-chip-id-ram-experimental.img')!=camera['boot_image_sha256'] or
            sha256(root/'sm8750-oneplus13-camera-chip-id-probe.dtb')!=camera['dtb_sha256']):
        raise ValueError('Camera alternative manifest hashes disagree')
    cam_sections=boot_sections((root/'boot-camera-chip-id-ram-experimental.img').read_bytes())
    for key in ('kernel','ramdisk'):
        if cam_sections[key]!=default_sections[key]:raise ValueError('Camera kernel/initramfs changed')
    camera_dtb=importlib.import_module('camera-probe-dtb')
    cam_expected,_=camera_dtb.derive((Path(__file__).resolve().parents[2]/'devices/oneplus13/qualified-data/calibrated.dtb').read_bytes())
    cam_tree=Fdt(cam_expected);cam_tree.nodes['/chosen']['bootargs']=(camera['cmdline']+'\0').encode()
    if (cam_sections['dtb']!=(root/'sm8750-oneplus13-camera-chip-id-probe.dtb').read_bytes() or
            Fdt(cam_sections['dtb']).nodes!=cam_tree.nodes):
        raise ValueError('Camera alternative DTB changed')
    for module in ('s5kjn5','i2c_qcom_cci'):
        if 'install '+module+' /bin/false\n' not in policy:raise ValueError('Camera modules must remain manual')
    video_files=m.get('video_probe_artifacts',{})
    video_names={'boot-video-ram-experimental.img','sm8750-oneplus13-video-probe.dtb',
                 'video-probe-manifest.json','video-probe-dtb-review.json'}
    if set(video_files)!=video_names or m.get('video_probe_auto_started') is not False:
        raise ValueError('Missing or auto-started manual video probe artifacts')
    for name,digest in video_files.items():
        if sha256(root/name)!=digest:raise ValueError('Video artifact changed')
    video=json.loads((root/'video-probe-manifest.json').read_text())
    if (video['scope']!='SEPARATE_MANUAL_IRIS_VIDEO_RAM_BOOT_NEVER_FLASH' or
            video.get('firmware_authentication_qualified') is not False or
            video.get('hardware_decode_qualified') is not False or
            video['default_boot_image_sha256']!=m['boot_image_sha256'] or
            video['rootfs_sha256']!=m['rootfs_sha256'] or
            video['source_commit']!=m['source_commit']):
        raise ValueError('Video alternative identity or qualification changed')
    video_nonce=video['session_identity_nonce']
    if not re.fullmatch('[a-f0-9]{24}',video_nonce) or video_nonce in (nonce,m['session_identity_nonce'],cam_nonce):
        raise ValueError('Video alternative needs a separate session identity')
    if video['cmdline']!=m['cmdline'].replace('oneplus13.session='+m['session_identity_nonce'],
            'oneplus13.session='+video_nonce)+' oneplus13.audio_probe=1 oneplus13.camera_probe=1 oneplus13.video_probe=1':
        raise ValueError('Video alternative boot arguments changed')
    if (sha256(root/'boot-video-ram-experimental.img')!=video['boot_image_sha256'] or
            sha256(root/'sm8750-oneplus13-video-probe.dtb')!=video['dtb_sha256']):
        raise ValueError('Video alternative manifest hashes disagree')
    video_sections=boot_sections((root/'boot-video-ram-experimental.img').read_bytes())
    for key in ('kernel','ramdisk'):
        if video_sections[key]!=default_sections[key]:raise ValueError('Video kernel/initramfs changed')
    video_dtb=importlib.import_module('video-probe-dtb')
    video_expected,_=video_dtb.derive((Path(__file__).resolve().parents[2]/'devices/oneplus13/qualified-data/calibrated.dtb').read_bytes())
    video_tree=Fdt(video_expected);video_tree.nodes['/chosen']['bootargs']=(video['cmdline']+'\0').encode()
    if (video_sections['dtb']!=(root/'sm8750-oneplus13-video-probe.dtb').read_bytes() or
            Fdt(video_sections['dtb']).nodes!=video_tree.nodes):
        raise ValueError('Video alternative DTB changed')
    if (video['video_firmware']!='usr/lib/firmware/'+video_dtb.FIRMWARE or
            video['video_firmware_sha256']!=video_dtb.FIRMWARE_SHA256 or
            data.get(video_dtb.FIRMWARE)!=video_dtb.FIRMWARE_SHA256):
        raise ValueError('Video alternative must use the exact phone firmware')
    if 'install qcom_iris /bin/false\n' not in policy:
        raise ValueError('Video module must remain manual')
    video_runtime=m.get('video_probe_runtime_files',{})
    video_runtime_names={'usr/libexec/oneplus13-ram-video-check.py','usr/libexec/oneplus13-decode-one-frame',
                         'usr/lib/oneplus13-video/synthetic-avc-bars.json','usr/lib/oneplus13-video/runtime-bindings.json'}
    if set(video_runtime)!=video_runtime_names:raise ValueError('Incomplete manual video runtime')
    for name,digest in video_runtime.items():
        raw=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),name])
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Changed video runtime file')
    video_bindings=json.loads(subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),
        'usr/lib/oneplus13-video/runtime-bindings.json']))
    if video_bindings['kernel_release']!=release or video_bindings['module_policy_sha256']!=hashlib.sha256(policy.encode()).hexdigest():
        raise ValueError('Video runtime kernel/policy binding differs')
    if set(video_bindings['files'])!=video_runtime_names-{'usr/lib/oneplus13-video/runtime-bindings.json'}:
        raise ValueError('Video runtime binding inventory changed')
    for name,digest in video_bindings['files'].items():
        if video_runtime.get(name)!=digest:raise ValueError('Video runtime binding changed')
    for name,digest in video_bindings['module_files'].items():
        raw=subprocess.check_output(['unsquashfs','-cat',str(root/'rootfs.squashfs'),'usr/lib/modules/'+release+'/'+name])
        if hashlib.sha256(raw).hexdigest()!=digest:raise ValueError('Video module binding changed')
    if set(video_bindings['live_nodes'])!={video_dtb.VIDEO,video_dtb.MEMORY}:
        raise ValueError('Video live resource inventory changed')
    for path,properties in video_bindings['live_nodes'].items():
        if {key:bytes.fromhex(value) for key,value in properties.items()}!=video_tree.nodes[path]:
            raise ValueError('Video live resource binding changed')
    static={'scope':'COMPLETE_IMAGE_STATIC_PACKAGE_VERIFICATION' ,'pass':True,'source_commit':m['source_commit'],
            'rootfs_sha256':m['rootfs_sha256'],'boot_image_sha256':m['boot_image_sha256'],
            'firmware_files_verified':len(data),'kernel_module_release_match':True,
            'container_files_verified':len(container_files),'container_daemon_auto_started':False,
            'sensor_runtime_files_verified':len(runtime_files),'sensor_runtime_host_private_inputs_required':False,
            'ssc_probe_files_verified':len(ssc_files),'ssc_probe_auto_started':False,
            'ssc_sample_files_verified':len(sample_files),'ssc_samples_auto_started':False,
            'experimental_audio_files_verified':len(audio_files),'audio_auto_started':False,
            'desktop_audio_files_verified':len(desktop_audio_files),'desktop_audio_auto_started':False,
            'phone_timezone':'Asia/Shanghai',
            'experimental_microphone_files_verified':len(microphone_files),'microphone_auto_started':False,
            'experimental_camera_files_verified':len(camera_files),'camera_auto_started':False,
            'camera_probe_runtime_files_verified':len(camera_runtime),
            'experimental_video_files_verified':len(video_files),'video_auto_started':False,
            'video_probe_runtime_files_verified':len(video_runtime),
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
