#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Bounded isolated SSC guard checks or explicitly selected metadata discovery."""
import argparse,hashlib,json,os,re,stat,struct,subprocess,tarfile
from pathlib import Path

STATE=Path('/run/oneplus13/ssc-metadata')
NAMES={'probe/phone-ssc-metadata-probe','probe/libssc.so.2',
       'tests/phone-probe-policy','tests/phone-probe-send-guard'}
TYPES={'accel','ambient_light','gyro','mag'}

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def entries(archive,manifest):
    if manifest.get('scope')!='PUBLIC_PHONE_SSC_METADATA_ONLY_PROBE' or set(manifest.get('files',{}))!=NAMES:
        raise ValueError('Wrong metadata probe scope')
    if (manifest.get('one_way_send_guard') is not True or manifest.get('samples_or_streams_allowed') is not False
        or manifest.get('private_inputs_included') is not False or manifest.get('hardware_qualified') is not False):
        raise ValueError('Unreviewed probe capability')
    if sha(archive)!=manifest['archive_sha256']:raise ValueError('Probe archive changed')
    result={}
    with tarfile.open(archive) as tf:
        for member in tf:
            if member.name not in NAMES or member.name in result or not member.isfile() or member.mode!=0o755:
                raise ValueError('Unexpected probe member')
            info=manifest['files'][member.name]
            if not 20<=member.size<=2*1024*1024 or member.size!=info['bytes'] or info['mode']!=0o755:
                raise ValueError('Probe member bound/mode mismatch')
            value=tf.extractfile(member).read()
            if (value[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',value,18)[0]!=183
                or hashlib.sha256(value).hexdigest()!=info['sha256']):raise ValueError('Probe ELF mismatch')
            result[member.name]=value
    if set(result)!=NAMES:raise ValueError('Incomplete probe')
    return result

def command(mode,state=STATE):
    if mode not in ('verify','discover'):raise ValueError('Unknown probe mode')
    unit='oneplus13-ssc-metadata-'+mode+'.service'
    properties=['Type=exec','User=65534','Group=65534','NoNewPrivileges=yes','CapabilityBoundingSet=',
       'ProtectSystem=strict','ProtectHome=yes','PrivateTmp=yes','PrivateDevices=yes','DevicePolicy=closed',
       'ProtectKernelTunables=yes','ProtectKernelModules=yes','ProtectControlGroups=yes',
       'RestrictSUIDSGID=yes','LockPersonality=yes','RestrictRealtime=yes',
       'KillMode=control-group','MemoryMax=128M','TasksMax=16','RuntimeMaxSec=20s','TimeoutStopSec=2s',
       'PrivateNetwork='+('yes' if mode=='verify' else 'no'),
       'RestrictAddressFamilies='+('AF_UNIX' if mode=='verify' else 'AF_UNIX AF_QIPCRTR')]
    args=['/usr/bin/systemd-run','--quiet','--wait','--pipe','--collect','--unit='+unit,
          '--setenv=LD_LIBRARY_PATH='+str(state/'probe'),*['--property='+x for x in properties]]
    if mode=='verify':
        args+=['/bin/sh','-eu','-c','"$1" --verify-lock; "$2"; "$3"','--',
               str(state/'probe/phone-ssc-metadata-probe'),str(state/'tests/phone-probe-policy'),
               str(state/'tests/phone-probe-send-guard')]
    else:args+=[str(state/'probe/phone-ssc-metadata-probe')]
    return unit,args

def interpret(mode,output):
    if len(output)>32768:raise ValueError('Oversized probe output')
    if mode=='verify':
        for marker in ('SSC_PHONE_METADATA_LOCK_VERIFIED_NO_QRTR','ok 6 /phone/06-one-way-lock',
                       'PHONE_METADATA_SEND_GUARD_BLOCKED_ALL_UNREVIEWED_REQUESTS_BEFORE_QMI'):
            if output.count(marker)!=1:raise ValueError('Missing native guard result')
        return {'native_guard_checks_passed':3,'qrtr_query_requested':False}
    rows=re.findall(r'^SSC_PHONE_METADATA type=(\w+) available=(yes|no) completed=(yes|no)$',output,re.M)
    if len(rows)!=4 or {r[0] for r in rows}!=TYPES:raise ValueError('Incomplete metadata result inventory')
    final='SSC_PHONE_METADATA_RESULT complete=yes samples_requested=no cleanup_returned=yes'
    if output.count(final)!=1 or any(r[1:]!=('yes','yes') for r in rows):raise ValueError('Discovery or cleanup incomplete')
    return {'metadata_available':sorted(TYPES),'qrtr_query_requested':True,'cleanup_returned':True,
            'sample_data_or_axes_accepted':False,'dsp_release_acknowledgement_claimed':False}

def run_probe(mode,state=STATE,run=subprocess.run):
    unit,args=command(mode,state)
    try:
        result=run(args,capture_output=True,text=True,timeout=26)
    finally:
        try:
            stopped=run(['/usr/bin/systemctl','stop',unit],capture_output=True,text=True,timeout=5)
        finally:
            inactive=run(['/usr/bin/systemctl','is-active',unit],capture_output=True,text=True,timeout=4)
        if stopped.returncode not in (0,5) or inactive.returncode not in (3,4) or inactive.stdout.strip() not in ('inactive','unknown'):
            raise ValueError('SSC metadata unit did not stop cleanly')
    if result.returncode:raise ValueError('SSC metadata process failed')
    facts=interpret(mode,result.stdout+result.stderr)
    return {'scope':'BOUNDED_SSC_METADATA_ONLY','mode':mode,'uid':65534,'unit_inactive':True,
            'measurement_commands_allowed':False,'peripheral_hardware_qualification_implied':False,**facts}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['verify','discover'],required=True)
    for name in ('archive','manifest'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('archive-sha256','manifest-sha256'):p.add_argument('--'+name,required=True)
    a=p.parse_args()
    if os.geteuid()!=0:raise ValueError('Root installs the low-privilege probe')
    if a.manifest.stat().st_size>65536 or a.archive.stat().st_size>4*1024*1024:raise ValueError('Delivery bound exceeded')
    if sha(a.archive)!=a.archive_sha256 or sha(a.manifest)!=a.manifest_sha256:raise ValueError('Delivery hash mismatch')
    files=entries(a.archive,json.loads(a.manifest.read_text()))
    if STATE.exists() or STATE.is_symlink():raise ValueError('Preserve prior probe evidence')
    for parent in STATE.parents:
        if parent==Path('/'):break
        if (parent.is_symlink() or not parent.is_dir() or parent.stat().st_uid!=0
            or parent.stat().st_mode&0o022 or not parent.stat().st_mode&stat.S_IXOTH):
            raise ValueError('Unexpected probe ancestry')
    STATE.mkdir(mode=0o755);STATE.chmod(0o755)
    for name,data in files.items():
        path=STATE/name
        path.parent.mkdir(mode=0o755,exist_ok=True);path.parent.chmod(0o755)
        with path.open('xb') as stream:stream.write(data)
        path.chmod(0o755)
    facts=run_probe(a.mode)
    print('RAM_SSC_METADATA_RESULT '+json.dumps(facts,sort_keys=True),flush=True)

if __name__=='__main__':main()
