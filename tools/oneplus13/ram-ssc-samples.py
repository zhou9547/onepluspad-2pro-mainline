#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Explicit bounded three-vector samples; no autostart or IIO service."""
import hashlib,importlib.util,json,math,os,re,struct,subprocess,tarfile
from pathlib import Path

STATE=Path('/run/oneplus13/ssc-samples')
TYPES={'accel','gyro','mag'}
LIBRARIES={'libprotobuf-c.so.1','libqmi-glib.so.5','libqrtr-glib.so.0','libmbim-glib.so.4'}
NAMES={'probe/phone-ssc-sample-probe','tests/phone-sample-tests'}|{'probe/'+x for x in LIBRARIES}
metadata_path=Path(__file__).with_name('ram-ssc-metadata.py')
if not metadata_path.exists():metadata_path=Path(__file__).with_name('oneplus13-ram-ssc-metadata.py')
spec=importlib.util.spec_from_file_location('metadata_guard',metadata_path)
if not spec or not spec.loader:raise ValueError('Missing original SSC guard')
metadata=importlib.util.module_from_spec(spec);spec.loader.exec_module(metadata)

def entries(archive,manifest):
    expected={'rate_hz':5,'collection_ms':3000,'maximum_uids':3,'one_way_send_guard':True,
              'metadata_executable_can_upgrade':False,'private_inputs_included':False,'hardware_qualified':False}
    if manifest.get('scope')!='PUBLIC_PHONE_SSC_BOUNDED_THREE_VECTOR_PROBE' or any(manifest.get(k)!=v for k,v in expected.items()):
        raise ValueError('Unreviewed sample capability')
    if set(manifest.get('files',{}))!=NAMES or set(manifest.get('runtime_libraries',{}))!=LIBRARIES:
        raise ValueError('Unreviewed sample archive inventory')
    if metadata.sha(archive)!=manifest['archive_sha256']:raise ValueError('Sample archive changed')
    result={};total=0
    with tarfile.open(archive) as tf:
        for member in tf:
            if member.name not in NAMES or member.name in result or not member.isfile() or member.mode!=0o755:
                raise ValueError('Unreviewed sample member')
            info=manifest['files'][member.name];total+=member.size
            if not 20<=member.size<=8*1024*1024 or total>16*1024*1024 or member.size!=info['bytes'] or info['mode']!=0o755:
                raise ValueError('Sample member bound/mode changed')
            data=tf.extractfile(member).read()
            if data[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',data,18)[0]!=183 or hashlib.sha256(data).hexdigest()!=info['sha256']:
                raise ValueError('Sample AArch64 ELF changed')
            result[member.name]=data
    if set(result)!=NAMES:raise ValueError('Incomplete sample archive')
    return result

def install(files,state=STATE):return metadata.install(files,state)

def command(mode,state=STATE):
    if mode not in ('verify','sample'):raise ValueError('Unreviewed sample mode')
    unit,args=metadata.command('verify' if mode=='verify' else 'discover',state)
    old_unit=unit;unit='oneplus13-ssc-samples-'+mode+'.service'
    args=[x.replace('--unit='+old_unit,'--unit='+unit) for x in args]
    args=args[:args.index('/bin/sh')] if mode=='verify' else args[:-1]
    # Absence means unbatched. Explicit zero is rejected by libssc's parser
    # and, under GLib test semantics, turns that warning into a child failure.
    args+=['--setenv=SSC_SUSPEND_MODE=nowakeup']
    args+=[str(state/('tests/phone-sample-tests' if mode=='verify' else 'probe/phone-ssc-sample-probe'))]
    return unit,args

def interpret(output):
    if len(output)>32768:raise ValueError('Oversized sample output')
    rows=re.findall(r'^SSC_PHONE_SAMPLE type=(accel|gyro|mag) enabled=([01]) disabled=([01]) count=(\d+) invalid=(\d+) norm_min=([0-9.e+-]+) norm_max=([0-9.e+-]+)$',output,re.M)
    if len(rows)!=3 or {r[0] for r in rows}!=TYPES:raise ValueError('Incomplete sample inventory')
    result={}
    for name,en,off,count,bad,minimum,maximum in rows:
        low,high=float(minimum),float(maximum)
        if en!='1' or off!='1' or not 3<=int(count)<=64 or int(bad)!=0 or not all(math.isfinite(x) for x in (low,high)) or not 0<=low<=high<=2000000:
            raise ValueError('Sensor samples or disable acknowledgement failed')
        result[name]={'samples':int(count),'finite_vectors':True,'norm_min':low,'norm_max':high,'disable_acknowledged':True}
    if output.count('SSC_PHONE_SAMPLE_RESULT complete=yes rate_hz=5 collection_ms=3000 cleanup_returned=yes')!=1:
        raise ValueError('Missing sample completion/cleanup')
    return {'samples':result,'rate_hz':5,'collection_ms':3000,'cleanup_returned':True,
            'physical_axes_or_calibration_accepted':False,'continuous_service_accepted':False}

def run_probe(mode,state=STATE,run=subprocess.run):
    unit,args=command(mode,state);result=None
    try:
        result=run(args,capture_output=True,text=True,timeout=20)
    finally:
        try:stopped=run(['/usr/bin/systemctl','stop',unit],capture_output=True,text=True,timeout=3)
        finally:inactive=run(['/usr/bin/systemctl','is-active',unit],capture_output=True,text=True,timeout=2)
        if stopped.returncode not in (0,5) or inactive.returncode not in (3,4) or inactive.stdout.strip() not in ('inactive','unknown','failed'):
            raise ValueError('Sample unit failed to stop')
    if result.returncode:
        private=metadata.save_private_failure(state,result)
        raise ValueError('Sample process failed: '+json.dumps({'exit':result.returncode,'private_output':private}))
    if mode=='verify':
        if not all(x in result.stdout for x in ['ok 1 /phone-samples/actual-send-policy','ok 2 /phone-samples/metadata-cannot-upgrade','ok 3 /phone-samples/real-protobuf-vector-decoder']):
            raise ValueError('Missing actual native sample guard checks')
        facts={'native_guard_checks_passed':3,'qrtr_query_requested':False}
    else:facts=interpret(result.stdout)
    return {'scope':'BOUNDED_THREE_VECTOR_SAMPLES','mode':mode,'unit_inactive':True,
            'measurement_commands_allowed':mode=='sample',**facts}
