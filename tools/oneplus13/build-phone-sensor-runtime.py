#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Native build of the original rpcd/proxy with the corrected phone libssc.

Development candidate. No registry, calibration or automatic service included.
Consumes only the guarded SSC build from this exact integration source commit.
"""
import argparse,hashlib,io,json,os,platform,shlex,shutil,struct,subprocess,tarfile,urllib.request
from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
PREFIX='/usr/lib/erhai/sensors'

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,log,env=None):
    p=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=240,env=env)
    with log.open('a') as f:f.write('\n'+json.dumps([str(x) for x in args])+'\n'+p.stdout+p.stderr)
    if p.returncode:raise ValueError('Native sensor runtime step failed: '+str(args[0]))
    return p.stdout.strip()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ssc-build',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--meson',default='meson');a=p.parse_args()
    if platform.machine() not in ('aarch64','arm64'):raise ValueError('Native AArch64 required')
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False);log=out/'runtime-build.log'
    ssc=a.ssc_build.resolve();proof=json.loads((ssc/'verification.json').read_text())
    commit=run(['git','-C',REPO,'rev-parse','HEAD'],log)
    if proof['integration_commit']!=commit or not proof['native_arm64'] or proof['host_check_only']:
        raise ValueError('SSC runtime must come from the same native source build')
    lock=json.loads((REPO/'packaging/sensors/sources.json').read_text())
    sources={x['name']:x for x in lock['sources']}
    sdk=out/'sdk';ssc_build=out/'runtime-libssc-build'
    run([a.meson,'setup',ssc_build,ssc/'source/libssc','--buildtype=release','--wrap-mode=nofallback',
         '--prefix='+PREFIX,'--libdir=lib','--bindir=bin','--libexecdir=libexec',
         '-Dc_link_args=-Wl,-rpath,'+PREFIX+'/lib'],log)
    run([a.meson,'compile','-C',ssc_build,'-j','2'],log)
    run([a.meson,'install','-C',ssc_build,'--no-rebuild','--destdir',sdk],log)
    pc=list(sdk.rglob('libssc.pc'))
    if len(pc)!=1:raise ValueError('Missing single libssc SDK pkg-config file')
    # This SDK is private to the build. Installed runtime RUNPATH remains the
    # original public prefix, not a build-host or owner filesystem location.
    text=pc[0].read_text();assert 'prefix='+PREFIX+'\n' in text
    pc[0].write_text(text.replace('prefix='+PREFIX+'\n','prefix='+str(sdk/PREFIX.lstrip('/'))+'\n',1))
    built={};pins=[]
    for name in ('hexagonrpc','iio-sensor-proxy'):
        entry=sources[name];archive=out/entry['archive']
        url=entry.get('mirror_url',entry['url']).replace('http:','https:',1)
        with urllib.request.urlopen(url,timeout=45) as response,archive.open('xb') as f:shutil.copyfileobj(response,f)
        if sha(archive)!=entry['sha256']:raise ValueError('Original source archive changed')
        tree=out/(name+'-source');tree.mkdir()
        with tarfile.open(archive) as tf:
            for member in tf:
                path=Path(member.name)
                if path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe source path')
            tf.extractall(tree,filter='data')
        src=tree/entry['directory']
        for license_name in ('COPYING','LICENSE'):
            if (src/license_name).is_file():shutil.copy2(src/license_name,out/('LICENSE-'+name+'-'+license_name))
        for patch in entry['patches']:
            path=REPO/'packaging/sensors'/patch['file']
            if sha(path)!=patch['sha256']:raise ValueError('Original runtime patch changed')
            run(['patch','-d',src,'-p1','--batch','--fuzz=0','-i',path],log)
        build=out/(name+'-build')
        env={**os.environ,'PKG_CONFIG_PATH':str(pc[0].parent)}
        args=[a.meson,'setup',build,src,'--buildtype=release','--wrap-mode=nofallback',
              '--prefix='+PREFIX,'--libdir=lib','--bindir=bin','--libexecdir=libexec',
              '-Dc_link_args=-Wl,-rpath,'+PREFIX+'/lib']
        if name=='iio-sensor-proxy':args+=['-Dssc-support=enabled','-Dudevrulesdir='+PREFIX+'/unused/udev','-Dsystemdsystemunitdir='+PREFIX+'/unused/systemd']
        run(args,log,env);run([a.meson,'compile','-C',build,'-j','2'],log,env)
        if name=='hexagonrpc':run([a.meson,'test','-C',build,'--print-errorlogs'],log,env)
        stage=out/(name+'-stage')
        run([a.meson,'install','-C',build,'--no-rebuild','--destdir',stage],log,env)
        built[name]=stage/PREFIX.lstrip('/')
        pins.append({'name':name,'commit':entry['upstream_commit'],'archive_sha256':sha(archive),'patches':entry['patches']})
    client=out/'phone-sensor-bus-check'
    flags=shlex.split(run(['pkg-config','--cflags','--libs','gio-2.0'],log))
    run(['gcc','-O2','-Wall','-Wextra','-Werror',REPO/'tools/oneplus13/phone-sensor-bus-check.c','-o',client,*flags,'-lm'],log)
    if run([client,'--self-test'],log)!='PHONE_SENSOR_BUS_VARIANT_CHECKS_PASS_NO_BUS_NO_QRTR':raise ValueError('D-Bus variant tests failed')
    tests=out/'phone-sensor-bus-tests'
    run(['gcc','-O2','-Wall','-Wextra','-Werror',REPO/'tools/oneplus13/phone-sensor-bus-tests.c','-o',tests,*flags,'-lm'],log)
    if run([tests,client],log)!='PHONE_SENSOR_BUS_REAL_GIO_FAKE_SERVICE_TESTS_PASS_NO_QRTR':raise ValueError('Actual GIO fake-bus tests failed')
    sanitized=out/'phone-sensor-bus-check-asan';sanitized_tests=out/'phone-sensor-bus-tests-asan'
    for source,target in [('phone-sensor-bus-check.c',sanitized),('phone-sensor-bus-tests.c',sanitized_tests)]:
        run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',
             REPO/'tools/oneplus13'/source,'-o',target,*flags,'-lm'],log)
    sanenv={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:abort_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'}
    if run([sanitized_tests,sanitized],log,sanenv)!='PHONE_SENSOR_BUS_REAL_GIO_FAKE_SERVICE_TESTS_PASS_NO_QRTR':raise ValueError('Sanitized GIO tests failed')
    entries={'bin/hexagonrpcd':built['hexagonrpc']/'bin/hexagonrpcd',
             'lib/libhexagonrpc.so.0.5':built['hexagonrpc']/'lib/libhexagonrpc.so.0.5',
             'libexec/iio-sensor-proxy':built['iio-sensor-proxy']/'libexec/iio-sensor-proxy',
             'bin/ssccli':sdk/PREFIX.lstrip('/')/'bin/ssccli', 'lib/libssc.so.2':sdk/PREFIX.lstrip('/')/'lib/libssc.so.2',
             'bin/phone-sensor-bus-check':client}
    # Exact dynamic-library closure already reviewed and recorded by the
    # companion native build. Copy bytes, not its SDK or integration hooks.
    metadata=json.loads((ssc/'phone-ssc-probe-manifest.json').read_text())
    extra=out/'extra';extra.mkdir()
    with tarfile.open(ssc/'phone-ssc-probe-arm64.tar.gz') as tf:
        for name in metadata['runtime_libraries']:
            member=tf.getmember('probe/'+name);raw=tf.extractfile(member).read()
            if hashlib.sha256(raw).hexdigest()!=metadata['files']['probe/'+name]['sha256']:raise ValueError('Runtime dependency changed')
            target=extra/name;target.write_bytes(raw);entries['lib/'+name]=target
    files={};archive=out/'phone-sensor-runtime-arm64.tar.gz'
    with tarfile.open(archive,'x:gz') as tf:
        for name,path in entries.items():
            raw=path.read_bytes()
            if raw[:6]!=b'\x7fELF\x02\x01' or struct.unpack_from('<H',raw,18)[0]!=183:raise ValueError('Runtime is not ARM64 ELF')
            item=tarfile.TarInfo(name);item.size=len(raw);item.mode=0o755 if name.startswith(('bin/','libexec/')) else 0o644;item.mtime=0
            tf.addfile(item,io.BytesIO(raw));files[name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'mode':item.mode}
    shutil.copy2('/usr/share/common-licenses/GPL-3',out/'LICENSE-GPL-3')
    result={'scope':'PUBLIC_PHONE_SENSOR_MANUAL_RUNTIME_CANDIDATE','integration_commit':commit,
        'files':files,'archive_sha256':sha(archive),'sources':pins,'runtime_libraries':metadata['runtime_libraries'],
        'registry_or_private_data_included':False,'services_auto_started':False,'hardware_qualified':False,
        'phone_property_and_matrix_fixes':True,'metadata_executable_guard_unchanged':True,
        'bus_client_variant_tests_passed':True,'real_gio_claim_signal_release_tests':True,
        'sanitized_real_gio_tests_passed':True,'builder_sha256':sha(Path(__file__)),
        'bus_client_source_sha256':sha(REPO/'tools/oneplus13/phone-sensor-bus-check.c')}
    (out/'phone-sensor-runtime-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'scope':result['scope'],'native_files':len(files),'source_commit':commit,'hardware_qualified':False}))
if __name__=='__main__':main()
