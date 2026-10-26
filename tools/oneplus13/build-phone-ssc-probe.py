#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build an isolated metadata-only SSC probe, never an enabled sensor service."""
import argparse,hashlib,json,os,platform,shutil,struct,subprocess,tarfile,urllib.request
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
ARCHIVE_SHA='716d6bd6b34d2d753060c6b54c9a87e34fae75b724c763bf9ef487efa3621587'
SOURCE_COMMIT='0cf77b93b55752da34dca2dcecc06fca8665184b'
EXTRA='0001-add-metadata-only-discovery-guard.patch'
EXTRA_SHA='50811cc82d6f221abce333731d50ff3d8d0355bb002f7aea850c4d1f30538bb5'

def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def environment():
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR') if k in os.environ}
    env.update(LANG='C.UTF-8',LC_ALL='C.UTF-8');return env
def run(args,log,env=None):
    r=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=240,env=env or environment())
    with log.open('a',encoding='utf-8') as stream:stream.write('\n'+json.dumps([str(x) for x in args])+'\n'+r.stdout+r.stderr)
    if r.returncode:raise RuntimeError('SSC offline build/check failed: '+str(args[0]))
    return r.stdout
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--archive',type=Path);p.add_argument('--meson',default='meson');p.add_argument('--host-check',action='store_true')
    a=p.parse_args();native=platform.machine() in ('aarch64','arm64')
    if not native and not a.host_check:raise ValueError('Native ARM64 required for artifacts')
    out=a.output.resolve()
    if out.exists():raise ValueError('Preserve previous build output')
    out.mkdir(parents=True);log=out/'build.log';log.write_text('PHONE_SSC_METADATA_PROBE_OFFLINE_ONLY\n')
    lock=json.loads((REPO/'packaging/sensors/sources.json').read_text())
    entry=next(x for x in lock['sources'] if x['name']=='libssc')
    if entry['sha256']!=ARCHIVE_SHA or entry['upstream_commit']!=SOURCE_COMMIT or len(entry['patches'])!=2:raise ValueError('Original recipe changed')
    archive=a.archive.resolve() if a.archive else out/entry['archive']
    if not a.archive:
        request=urllib.request.Request(entry['mirror_url'].replace('http:','https:',1),headers={'User-Agent':'OnePlus13-offline-source-build'})
        with urllib.request.urlopen(request,timeout=45) as response,archive.open('xb') as target:shutil.copyfileobj(response,target)
    if sha(archive)!=ARCHIVE_SHA:raise ValueError('Original source hash changed')
    parent=out/'source';parent.mkdir()
    with tarfile.open(archive) as tf:
        names=set()
        for member in tf:
            path=Path(member.name)
            if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0]!='libssc' or member.name in names or not(member.isfile() or member.isdir()):raise ValueError('Unsafe source archive')
            names.add(member.name)
        tf.extractall(parent,filter='data')
    source=parent/'libssc';patches=[]
    for item in entry['patches']:
        path=REPO/'packaging/sensors'/item['file']
        if sha(path)!=item['sha256']:raise ValueError('Original patch changed')
        patches.append(path)
    extra=REPO/'tools/oneplus13/ssc-patches'/EXTRA
    if sha(extra)!=EXTRA_SHA:raise ValueError('Phone overlay changed')
    patches.append(extra)
    for patch in patches:run(['patch','-d',source,'-p1','--batch','--fuzz=0','-i',patch],log)
    counts={}
    for kind,options in [('release',['--buildtype=release']),('sanitized',['--buildtype=debug','-Db_sanitize=address,undefined','-Db_lundef=false'])]:
        build=out/kind
        run([a.meson,'setup',build,source,'--wrap-mode=nofallback',*options],log)
        run([a.meson,'compile','-C',build,'-j','2'],log)
        env=environment();env['ASAN_OPTIONS']='detect_leaks=0:abort_on_error=1';env['UBSAN_OPTIONS']='halt_on_error=1:print_stacktrace=1'
        run([a.meson,'test','-C',build,'--setup','phoneoffline','--suite','phone-probe','--suite','delivery','--print-errorlogs'],log,env)
        tests=[json.loads(line) for line in (build/'meson-logs/testlog-phoneoffline.json').read_text().splitlines() if line.strip()]
        if len(tests)!=3 or not all(x['result']=='OK' for x in tests):raise ValueError('Missing actual guard/encoding results')
        names={x['name'].split(':')[-1] for x in tests}
        if names!={'phone-probe-policy','phone-probe-send-guard','tests-delivery'}:raise ValueError('Wrong tested scope')
        counts[kind]=len(tests)
        answer=run([build/'src/phone-ssc-metadata-probe','--verify-lock'],log,env)
        if 'SSC_PHONE_METADATA_LOCK_VERIFIED_NO_QRTR' not in answer:raise ValueError('Probe policy not linked')
    probe=out/'release/src/phone-ssc-metadata-probe'
    symbols=run(['readelf','-Ws',probe],log)
    imported=[x.split()[-1].split('@')[0] for x in symbols.splitlines() if len(x.split())>=8 and x.split()[6]=='UND']
    if any('ssc_sensor_' in name and ('_open' in name or '_close' in name) for name in imported):raise ValueError('Probe imports measurement APIs')
    if not {'ssc_sensor_new','ssc_phone_lock_metadata_only','ssc_phone_metadata_only_locked'}<=set(imported):raise ValueError('Probe lacks guarded API imports')
    files={}
    if native and not a.host_check:
        entries={'probe/phone-ssc-metadata-probe':probe,'probe/libssc.so.2':out/'release/src/libssc.so.2',
                 'tests/phone-probe-policy':out/'release/tests/phone-probe-policy',
                 'tests/phone-probe-send-guard':out/'release/tests/phone-probe-send-guard'}
        archive_out=out/'phone-ssc-probe-arm64.tar.gz'
        with tarfile.open(archive_out,'x:gz') as tf:
            for name,path in entries.items():
                data=path.read_bytes()
                if data[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',data,18)[0]!=183:raise ValueError('Not AArch64 ELF')
                info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o755;info.mtime=0
                with path.open('rb') as stream:tf.addfile(info,stream)
                files[name]={'bytes':len(data),'sha256':sha(path),'mode':info.mode}
        (out/'phone-ssc-probe-manifest.json').write_text(json.dumps({'scope':'PUBLIC_PHONE_SSC_METADATA_ONLY_PROBE',
           'files':files,'archive_sha256':sha(archive_out),'samples_or_streams_allowed':False,
           'one_way_send_guard':True,'private_inputs_included':False,'hardware_qualified':False},indent=2)+'\n')
    for name in ['COPYING','LICENSE']:
        if (source/name).is_file():shutil.copy2(source/name,out/('LICENSE-'+name))
    shutil.copy2('/usr/share/common-licenses/GPL-3',out/'LICENSE-GPL-3')
    (out/'COPYRIGHT.txt').write_text('Original libssc 0.4.4 retains Dylan Van Assche and original contributor notices.\nPhone-only metadata guard/probe: Codex <codex@openai.com>, GPL-3.0-or-later.\nSource commit '+SOURCE_COMMIT+'; original recipe patches and phone overlay recorded in verification.json.\nNo firmware, calibration, registry, service integration or installer included.\n')
    result={'scope':'PHONE_SSC_METADATA_ONLY_OFFLINE_BUILD','phone_operations':0,'native_arm64':native,
        'host_check_only':a.host_check,'source_commit':SOURCE_COMMIT,'source_archive_sha256':ARCHIVE_SHA,
        'patches':[{'name':x.name,'sha256':sha(x)} for x in patches],
        'test_counts':counts,'one_way_metadata_policy_and_real_send_guard_tests_pass':True,
        'original_delivery_encoding_regression_pass':True,'original_qrtr_service_tests_run':False,
        'no_measurement_api_imported_by_probe':True,'lock_only_cli_pass':True,'leak_testing_claimed':False,
        'private_inputs_included':False,'services_or_installers_included':False,'hardware_eligible':False,
        'artifact_files':files}
    (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
