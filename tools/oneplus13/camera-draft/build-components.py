#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile isolated camera and amplifier components, never phone integration."""
import argparse,hashlib,json,os,platform,subprocess,tarfile,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
PIN='7a81d184e3098624d4342d8f4eff5e23674bcc9f'
REPOSITORY='https://github.com/yzddmr6/linux-sm8750-erhai.git'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source-archive',type=Path)
    parser.add_argument('--cross-compile',choices=('aarch64-linux-gnu-',))
    parser.add_argument('--cphy',action='store_true',
                        help='Compile isolated C-PHY framework candidate without phone tables')
    args=parser.parse_args()
    if platform.machine() not in ('aarch64','arm64') and not args.cross_compile:
        raise ValueError('Native ARM64 or explicit AArch64 cross compiler required')
    out=args.output.resolve()
    if out.exists():raise ValueError('Preserve prior evidence')
    out.mkdir(parents=True);log=out/'compile.log'
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR') if k in os.environ}
    env.update(LANG='C.UTF-8',LC_ALL='C.UTF-8')
    if args.cross_compile:env['CROSS_COMPILE']=args.cross_compile
    def run(command,timeout=240):
        result=subprocess.run([str(x) for x in command],capture_output=True,env=env,timeout=timeout)
        with log.open('ab') as f:f.write(json.dumps([str(x) for x in command]).encode()+b'\n'+result.stdout+result.stderr+b'\n')
        if result.returncode:raise RuntimeError('Offline component step failed; see compile.log')
        return result.stdout.decode('utf-8','replace')
    lock=json.loads((HERE/'sources.json').read_text())
    if lock['kernel_pin']!=PIN or lock['kernel_repository']!=REPOSITORY or len(lock['patches'])!=23:
        raise ValueError('Unreviewed component inputs')
    kernel=out/'linux'
    if args.source_archive:
        if sha(args.source_archive)!=lock['kernel_archive']['sha256']:
            raise ValueError('Kernel source archive mismatch')
        scratch=out/'source-extract';scratch.mkdir()
        with tarfile.open(args.source_archive) as archive:
            archive.extractall(scratch,filter='data')
        roots=list(scratch.iterdir())
        if len(roots)!=1 or not roots[0].is_dir():raise ValueError('Unexpected source archive roots')
        roots[0].rename(kernel);scratch.rmdir()
    else:
        run(['git','init',kernel]);run(['git','-C',kernel,'remote','add','origin',REPOSITORY])
        run(['git','-C',kernel,'fetch','--depth','1','origin',PIN],timeout=240)
        run(['git','-C',kernel,'checkout','--detach','FETCH_HEAD'],timeout=180)
        if run(['git','-C',kernel,'rev-parse','HEAD']).strip()!=PIN:raise ValueError('Kernel pin mismatch')
    if len(lock.get('local_fixes',[]))!=2:raise ValueError('Missing reviewed compiler/error corrections')
    for entry in lock['disabled_cci_resources']:
        if sha(HERE/entry['file'])!=entry['sha256']:raise ValueError('Original resource patch changed')
    for entry in lock['patches']+lock['local_fixes']+lock['resource_rebases']+lock['sensor_patches']+lock['sensor_compat_fixes']:
        name=Path(entry['file'])
        if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe patch name')
        patch=HERE/name
        if sha(patch)!=entry['sha256']:raise ValueError('Public patch hash mismatch')
        run(['patch','-d',kernel,'-p1','--batch','--forward','--fuzz=0','-i',patch])
    cphy_lock=None
    if args.cphy:
        directory=HERE/'cphy';cphy_lock=json.loads((directory/'sources.json').read_text())
        if (cphy_lock['scope']!='ISOLATED_CPHY_FRAMEWORK_ONLY_NO_PHONE_TABLE_OR_ACTIVATION' or
            cphy_lock['phone_register_table_present'] or cphy_lock['hardware_qualified']):
            raise ValueError('Unreviewed C-PHY integration scope')
        def verify_paths(base,inventory):
            for name,digest in inventory.items():
                path=Path(name)
                if path.is_absolute() or '..' in path.parts or sha(base/path)!=digest:
                    raise ValueError('C-PHY source mismatch: '+name)
        verify_paths(kernel,cphy_lock['base_files'])
        verify_paths(directory,{item['file']:item['sha256'] for item in cphy_lock['upstream_messages']})
        verify_paths(directory,{'rebased.patch':cphy_lock['rebase_patch_sha256']})
        run(['patch','-d',kernel,'-p1','--batch','--forward','--fuzz=0','-i',directory/'rebased.patch'])
        verify_paths(kernel,cphy_lock['generated_files'])
    # Only this isolated tree gains disabled CCI/MCLK resources. No firmware,
    # rootfs or normal build output is touched. The amplifier
    # object shares the new build configuration, without Kconfig/DT integration.
    audio=HERE.parent/'audio-draft'
    for name in ('aw88461.c','aw88461-profile.h'):
        (kernel/'sound/soc/codecs'/name).write_bytes((audio/name).read_bytes())
    run(['python3',audio/'check.py','--output',out/'audio-synthetic'])
    checker='check-cphy-errors.py' if args.cphy else 'check-phy-errors.py'
    run(['python3',HERE/checker,'--kernel',kernel,'--output',out/'camera-synthetic'])
    run(['make','-C',kernel,'ARCH=arm64','defconfig'],timeout=120)
    config=kernel/'scripts/config'
    for name in ('MEDIA_SUPPORT','MEDIA_CONTROLLER','VIDEO_DEV','MEDIA_PLATFORM_SUPPORT','V4L_PLATFORM_DRIVERS','PM_OPP'):
        run([config,'--file',kernel/'.config','--enable',name])
    for name in ('VIDEO_QCOM_CAMSS','PHY_QCOM_MIPI_CSI2','I2C_QCOM_CCI','VIDEO_S5KJN5'):
        run([config,'--file',kernel/'.config','--module',name])
    run(['make','-C',kernel,'ARCH=arm64','olddefconfig'],timeout=120)
    cfg=(kernel/'.config').read_text()
    for name in ('VIDEO_QCOM_CAMSS','PHY_QCOM_MIPI_CSI2','I2C_QCOM_CCI','VIDEO_S5KJN5'):
        if f'CONFIG_{name}=m\n' not in cfg:raise ValueError('Required component disabled: '+name)
    targets=['drivers/media/platform/qcom/camss/',
             'drivers/media/i2c/s5kjn5.o',
             'drivers/phy/qualcomm/phy-qcom-mipi-csi2.o',
             'drivers/i2c/busses/i2c-qcom-cci.o','drivers/clk/qcom/camcc-sm8750.o',
             'drivers/clk/qcom/cambistmclkcc-sm8750.o',
             'sound/soc/codecs/aw88461.o','sound/soc/codecs/aw88395/aw88395_lib.o']
    run(['make','-C',kernel,'ARCH=arm64','-j'+str(min(os.cpu_count() or 2,8)),'-k',
         'W=1','KCFLAGS=-Werror',*targets],timeout=600)
    phone_dts=HERE.parents[2]/'devices/oneplus13'
    for path in phone_dts.glob('sm8750-oneplus-dodge*.dts'):
        (kernel/'arch/arm64/boot/dts/qcom'/path.name).write_bytes(path.read_bytes())
    run(['make','-C',kernel,'ARCH=arm64','qcom/sm8750-oneplus-dodge.dtb'],timeout=120)
    spec=importlib.util.spec_from_file_location('camera_stock',HERE.parent/'stock.py')
    stock=importlib.util.module_from_spec(spec);spec.loader.exec_module(stock)
    dtb=kernel/'arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dtb'
    tree=stock.Fdt(dtb.read_bytes())
    cci=[path for path,properties in tree.nodes.items()
         if 'compatible' in properties and 'qcom,sm8750-cci' in tree.text(path,'compatible')]
    if len(cci)!=3 or any(tree.text(path,'status')!=['disabled'] for path in cci):
        raise ValueError('All three staged CCI controllers must remain disabled')
    buses=[path for path in tree.nodes if any(path.startswith(parent+'/i2c-bus@') for parent in cci)]
    if len(buses)!=6:raise ValueError('Expected six disabled-parent CCI I2C hosts')
    expected=['drivers/media/platform/qcom/camss/camss-csid-980.o',
              'drivers/media/platform/qcom/camss/camss-vfe-gen4.o',
              'drivers/media/platform/qcom/camss/camss-tpg-gen1.o',
              'drivers/media/platform/qcom/camss/camss.o',*targets[1:]]
    files={}
    for name in expected:
        path=kernel/name
        data=path.read_bytes()
        if data[:6]!=b'\x7fELF\x02\x01' or int.from_bytes(data[18:20],'little')!=183:
            raise ValueError('Expected AArch64 object: '+name)
        files[name]={'sha256':sha(path),'bytes':len(data)}
    (out/'kernel.config').write_text(cfg)
    proof={'scope':'OFFLINE_CAMERA_AND_AMPLIFIER_OBJECTS_ONLY','phone_operations':0,
       'isolated_cphy_framework':args.cphy,'cphy_provenance':cphy_lock,
       'phone_cphy_register_table_present':False,'cphy_capture_qualified':False,
       'kernel_pin':PIN,'patches':lock['patches'],'local_fixes':lock['local_fixes'],'aarch64_objects':files,
       'disabled_cci_resources':lock['disabled_cci_resources'],'resource_rebases':lock['resource_rebases'],
       'sensor_patches':lock['sensor_patches'],'sensor_compat_fixes':lock['sensor_compat_fixes'],
       'phone_base_dtb_compiled_with_disabled_cci':True,'disabled_cci_controllers':len(cci),
       'cci_i2c_hosts':len(buses),'phone_base_dtb_sha256':sha(dtb),
       'cross_compiler':args.cross_compile,'native_arm64_host':platform.machine() in ('aarch64','arm64'),
       'warning_errors_enabled':True,'phone_dts_or_candidate_changed':False,
       'module_install_or_boot_image_created':False,'firmware_or_private_data_included':False,
       'camera_sensor_driver_and_board_graph_complete':False,
       'speaker_calibration_and_dynamic_protection_complete':False,'hardware_qualified':False}
    (out/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('patches','aarch64_objects')},indent=2))

if __name__=='__main__':main()
