#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""QEMU-only handoff of exact SquashFS with separately pinned matching modules."""
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import tarfile
import threading
from common import make_cpio,read_cpio,sha256
from desktop import derive

REPO=Path(__file__).resolve().parents[2]
EXPECTED_KERNEL_COMMIT='1f5c1128d42a62244bef9974e58cfe07adf29f7d'
EXPECTED_ROOTFS='f9140e5c98d70bca6a04b8934dc9b1937bbf28b1eb0218411eaa0a9939a6cced'
EXPECTED_RELEASE='7.2.0-oneplus13-g7a81d184e309-c963dc1c909ec-p4f8ae6f76730'

def main():
    p=argparse.ArgumentParser();p.add_argument('--kernel',type=Path,required=True)
    p.add_argument('--rootfs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();kernel=a.kernel.resolve();rootfs=a.rootfs.resolve();out=a.output.resolve()
    manifest=json.loads((kernel/'manifest.json').read_text())
    assert manifest['integration_commit']==EXPECTED_KERNEL_COMMIT
    assert manifest['kernel_release']==EXPECTED_RELEASE
    for name in ['Image','initramfs.cpio.gz','modules.tar.gz']:
        assert sha256(kernel/name)==manifest['files'][name]['sha256'],name
    assert sha256(rootfs)==EXPECTED_ROOTFS and rootfs.stat().st_size==426221568
    with tarfile.open(kernel/'modules.tar.gz') as archive:
        assert all(not x.name.startswith('/') and '..' not in Path(x.name).parts for x in archive)
    packed,_=derive((kernel/'initramfs.cpio.gz').read_bytes())
    files=read_cpio(gzip.decompress(packed))
    # The generic userspace artifact deliberately has no kernel-release pin.
    # Supply the separately verified matching kernel in the emulator's RAM
    # overlay before prepare's normal release check, never by editing SquashFS.
    prepare=files['bin/oneplus13-ram-prepare']['data']
    release_check=b'[ "$(cat /newroot/usr/lib/oneplus13-desktop/kernel-release)" = "$(uname -r)" ]\n'
    assert prepare.count(release_check)==1
    bind=(b'[ "$qemu" = 1 ]\n'+
          b'tr \'\\000\' \'\\n\' < /sys/firmware/devicetree/base/compatible | grep -qx linux,dummy-virt\n'+
          b'[ "$(uname -r)" = '+EXPECTED_RELEASE.encode()+b' ]\n'+
          b'[ ! -e /newroot/usr/lib/oneplus13-desktop/kernel-release ]\n'+
          b'printf \'%s\\n\' '+EXPECTED_RELEASE.encode()+b' > /newroot/usr/lib/oneplus13-desktop/kernel-release\n')
    files['bin/oneplus13-ram-prepare']['data']=prepare.replace(release_check,bind+release_check)
    helper=files['bin/oneplus13-qemu-install']['data']
    anchor=b'[ "${1:-}" = /newroot ]\n'
    assert helper.count(anchor)==1
    install=(b'mkdir -p /run/qemu-modules /newroot/usr/lib/modules\n'+
             b'/bin/busybox tar xzf /qemu-matching-modules.tar.gz -C /run/qemu-modules\n'+
             b'cp -a /run/qemu-modules/lib/modules/. /newroot/usr/lib/modules/\n')
    files['bin/oneplus13-qemu-install']['data']=helper.replace(anchor,anchor+install)
    files['qemu-matching-modules.tar.gz']={'mode':stat.S_IFREG|0o600,'major':0,'minor':0,
                                           'data':(kernel/'modules.tar.gz').read_bytes()}
    out.mkdir(parents=True,exist_ok=True);ramdisk=out/'initramfs-qemu-only.cpio.gz'
    ramdisk.write_bytes(gzip.compress(make_cpio([(n,v['mode'],v['data'],v['major'],v['minor'])
                                                for n,v in sorted(files.items())]),mtime=0))
    spec=importlib.util.spec_from_file_location('server',REPO/'tools/oneplus13/serve-rootfs.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    stats={'bytes':0,'parts':[]}
    server=module.ThreadingHTTPServer(('127.0.0.1',8000),module.handler(rootfs,stats));server.daemon_threads=True
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    cmdline=('console=ttyAMA0 rdinit=/init panic=15 oneplus13.desktop=1 '
             'oneplus13.desktop.qemu=1 oneplus13.desktop.qemu-http=1 '
             f'oneplus13.rootfs.sha256={EXPECTED_ROOTFS} oneplus13.rootfs.bytes={rootfs.stat().st_size}')
    command=['qemu-system-aarch64','-machine','virt','-cpu','cortex-a76','-m','6144','-smp','2',
             '-nographic','-no-reboot','-nic','none','-kernel',str(kernel/'Image'),'-initrd',str(ramdisk),
             '-drive',f'file={rootfs},format=raw,if=none,readonly=on,id=rootfs',
             '-device','virtio-blk-device,drive=rootfs','-append',cmdline,
             '-netdev','user,id=rootfsnet,net=172.16.13.0/24,host=172.16.13.2',
             '-device','virtio-net-device,netdev=rootfsnet,mac=02:13:00:00:00:01']
    try:
        result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=360)
        log=result.stdout;rc=result.returncode
    except subprocess.TimeoutExpired as exc:
        log=exc.stdout or b'';log=log.decode(errors='replace') if isinstance(log,bytes) else log;rc=124
    finally:
        server.shutdown();server.server_close();thread.join()
    (out/'qemu.log').write_text(log)
    markers=['ONEPLUS13_DISPLAY_AUTOLOAD_BLOCKED','ONEPLUS13_NATIVE_RUNTIME_GUARDS_OFFLINE_OK',
             'ONEPLUS13_NATIVE_PREFLIGHT_OFFLINE_OK','ONEPLUS13_NATIVE_HANDOFF_OFFLINE_OK',
             'ONEPLUS13_DESKTOP_HANDOFF_OK','ONEPLUS13_QEMU_DEADLINE_FIRED','reboot: Restarting system']
    passed=rc==0 and all(x in log for x in markers)
    if passed:passed=all(log.index(x)<log.index(y) for x,y in zip(markers,markers[1:]))
    count=(rootfs.stat().st_size+module.CHUNK-1)//module.CHUNK
    passed=passed and stats['bytes']==rootfs.stat().st_size and stats['parts']==list(range(count))
    report={'scope':'QEMU_EXACT_ROOTFS_HANDOFF_ONLY','phone_operations':0,'hardware_tested':False,
            'rootfs_sha256':EXPECTED_ROOTFS,'rootfs_bytes':rootfs.stat().st_size,
            'kernel_integration_commit':EXPECTED_KERNEL_COMMIT,'kernel_release':EXPECTED_RELEASE,
            'kernel_image_sha256':sha256(kernel/'Image'),'modules_sha256':sha256(kernel/'modules.tar.gz'),
            'qemu_only_module_delivery':True,'rootfs_bytes_unchanged':sha256(rootfs)==EXPECTED_ROOTFS,
            'returncode':rc,'required_markers':{x:x in log for x in markers},
            'http_bytes':stats['bytes'],'http_parts':stats['parts'],'handoff_and_deadline_pass':passed,
            'physical_display_input_radio_or_audio_tested':False}
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
    if not passed:print(log[-9000:]);raise SystemExit(1)

if __name__=='__main__':main()
