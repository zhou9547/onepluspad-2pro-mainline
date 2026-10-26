#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile isolated camera and amplifier components, never phone integration."""
import argparse,hashlib,json,os,platform,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
PIN='7a81d184e3098624d4342d8f4eff5e23674bcc9f'
REPOSITORY='https://github.com/yzddmr6/linux-sm8750-erhai.git'

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if platform.machine() not in ('aarch64','arm64'):raise ValueError('Native ARM64 only')
    out=args.output.resolve()
    if out.exists():raise ValueError('Preserve prior evidence')
    out.mkdir(parents=True);log=out/'compile.log'
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR') if k in os.environ}
    env.update(LANG='C.UTF-8',LC_ALL='C.UTF-8')
    def run(command,timeout=240):
        result=subprocess.run([str(x) for x in command],capture_output=True,env=env,timeout=timeout)
        with log.open('ab') as f:f.write(json.dumps([str(x) for x in command]).encode()+b'\n'+result.stdout+result.stderr+b'\n')
        if result.returncode:raise RuntimeError('Offline component step failed; see compile.log')
        return result.stdout.decode('utf-8','replace')
    lock=json.loads((HERE/'sources.json').read_text())
    if lock['kernel_pin']!=PIN or lock['kernel_repository']!=REPOSITORY or len(lock['patches'])!=23:
        raise ValueError('Unreviewed component inputs')
    kernel=out/'linux'
    run(['git','init',kernel]);run(['git','-C',kernel,'remote','add','origin',REPOSITORY])
    run(['git','-C',kernel,'fetch','--depth','1','origin',PIN],timeout=240)
    run(['git','-C',kernel,'checkout','--detach','FETCH_HEAD'],timeout=180)
    if run(['git','-C',kernel,'rev-parse','HEAD']).strip()!=PIN:raise ValueError('Kernel pin mismatch')
    for entry in lock['patches']:
        name=Path(entry['file'])
        if name.is_absolute() or '..' in name.parts:raise ValueError('Unsafe patch name')
        patch=HERE/name
        if sha(patch)!=entry['sha256']:raise ValueError('Public patch hash mismatch')
        run(['patch','-d',kernel,'-p1','--batch','--forward','--fuzz=0','-i',patch])
    # No DTS, firmware, rootfs or normal build output is touched. The amplifier
    # object shares the new build configuration, without Kconfig/DT integration.
    audio=HERE.parent/'audio-draft'
    for name in ('aw88461.c','aw88461-profile.h'):
        (kernel/'sound/soc/codecs'/name).write_bytes((audio/name).read_bytes())
    run(['python3',audio/'check.py','--output',out/'audio-synthetic'])
    run(['make','-C',kernel,'ARCH=arm64','defconfig'],timeout=120)
    config=kernel/'scripts/config'
    for name in ('MEDIA_SUPPORT','MEDIA_CONTROLLER','VIDEO_DEV','MEDIA_PLATFORM_SUPPORT','V4L_PLATFORM_DRIVERS','PM_OPP'):
        run([config,'--file',kernel/'.config','--enable',name])
    for name in ('VIDEO_QCOM_CAMSS','PHY_QCOM_MIPI_CSI2','I2C_QCOM_CCI'):
        run([config,'--file',kernel/'.config','--module',name])
    run(['make','-C',kernel,'ARCH=arm64','olddefconfig'],timeout=120)
    cfg=(kernel/'.config').read_text()
    for name in ('VIDEO_QCOM_CAMSS','PHY_QCOM_MIPI_CSI2','I2C_QCOM_CCI'):
        if f'CONFIG_{name}=m\n' not in cfg:raise ValueError('Required component disabled: '+name)
    targets=['drivers/media/platform/qcom/camss/',
             'drivers/phy/qualcomm/phy-qcom-mipi-csi2.o',
             'drivers/i2c/busses/i2c-qcom-cci.o','drivers/clk/qcom/camcc-sm8750.o',
             'sound/soc/codecs/aw88461.o','sound/soc/codecs/aw88395/aw88395_lib.o']
    run(['make','-C',kernel,'ARCH=arm64','-j'+str(min(os.cpu_count() or 2,8)),
         'W=1','KCFLAGS=-Werror',*targets],timeout=600)
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
       'kernel_pin':PIN,'patches':lock['patches'],'aarch64_objects':files,
       'warning_errors_enabled':True,'phone_dts_or_candidate_changed':False,
       'module_install_or_boot_image_created':False,'firmware_or_private_data_included':False,
       'camera_sensor_driver_and_board_graph_complete':False,
       'speaker_calibration_and_dynamic_protection_complete':False,'hardware_qualified':False}
    (out/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k not in ('patches','aarch64_objects')},indent=2))

if __name__=='__main__':main()
