#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Dummy-virt only: actual concurrent units with synthetic trace/metadata."""
import importlib.util,json,os,subprocess,time
from pathlib import Path

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def main():
    if b'linux,dummy-virt' not in Path('/sys/firmware/devicetree/base/compatible').read_bytes().split(b'\0'):
        raise ValueError('QEMU-only composite fixture')
    here=Path('/run/oneplus13')
    fs=load('qemu_composite_fs',here/'ram-sensor-fileserver.py')
    ssc=load('qemu_composite_ssc',here/'ram-ssc-metadata.py')
    composite=load('qemu_composite',here/'ram-sensor-discovery.py')
    original=ssc.command
    good='\n'.join('SSC_PHONE_METADATA type='+n+' available=yes completed=yes' for n in sorted(ssc.TYPES))+'\nSSC_PHONE_METADATA_RESULT complete=yes samples_requested=no cleanup_returned=yes\n'
    trace='100 ioctl(0x3, 0x5208, 0) = 0 <0.001>\n'+('100 ioctl(0x3, 0xc0105203, 0xffff) = 0 <0.001>\n'*3)+'100 openat(AT_FDCWD, "/public/sensors/registry", O_RDONLY) = 4 <0.001>\n100 openat(AT_FDCWD, "/public/sensors/sns_reg.conf", O_RDONLY) = 5 <0.001>\n'
    observations=[]
    for timeout_fixture in (False,True):
        fs.STATE=str(here/('composite-timeout' if timeout_fixture else 'composite-success'))
        state=Path(fs.STATE);state.mkdir(mode=0o700);os.chown(state,65534,65534)
        tracer=here/('synthetic-tracer-timeout' if timeout_fixture else 'synthetic-tracer-success')
        tracer.write_text('#!/usr/bin/python3\nimport os,time\nfrom pathlib import Path\nassert os.getuid()==65534\nassert not Path("/dev/fastrpc-adsp-secure").exists()\nPath('+repr(str(state/'syscalls.log'))+').write_text('+repr(trace)+')\ntime.sleep(35)\n')
        tracer.chmod(0o755)
        def synthetic(mode,state=ssc.STATE):
            unit,command=original(mode,state)
            # Replace only the fixture executable, retain sandbox/cleanup and
            # restrict even discovery to AF_UNIX + PrivateNetwork. No QRTR.
            command=[x.replace('RestrictAddressFamilies=AF_UNIX AF_QIPCRTR','RestrictAddressFamilies=AF_UNIX').replace('PrivateNetwork=no','PrivateNetwork=yes') for x in command]
            if timeout_fixture:command=[x.replace('RuntimeMaxSec=20s','RuntimeMaxSec=2s') for x in command]
            assertion='test "$(id -u)" = 65534; test ! -e /dev/fastrpc-adsp-secure; '
            script=assertion+('sleep 30' if timeout_fixture else 'printf %s '+__import__('shlex').quote(good))
            return unit,command[:-1]+['/bin/sh','-eu','-c',script]
        ssc.command=synthetic
        results=[]
        def callback():results.append(composite.metadata_callback(fs,ssc))
        began=time.monotonic();refused=False
        try:worker=fs.serve(tracer,diagnostic=True,during_active=callback)
        except ValueError:
            if not timeout_fixture:raise
            refused=True
        for unit in (fs.UNIT,'oneplus13-ssc-metadata-discover.service'):
            result=subprocess.run(['/usr/bin/systemctl','is-active',unit],capture_output=True,text=True,timeout=3)
            assert result.returncode in (3,4) and result.stdout.strip() in ('inactive','unknown'),unit
        if timeout_fixture:assert refused and not results
        else:
            assert len(results)==1 and worker['file_server_cleanly_stopped'] and not worker['file_server_accepted']
        assert not Path('/sys/module/fastrpc').exists() and not Path('/dev/fastrpc-adsp-secure').exists()
        observations.append({'synthetic_timeout':timeout_fixture,'metadata_callbacks_completed':len(results),
             'both_units_inactive':True,'elapsed_seconds':round(time.monotonic()-began,3)})
    print('QEMU_SENSOR_DISCOVERY_SELFTEST_RESULT '+json.dumps({'scope':'SYNTHETIC_CONCURRENT_UNITS_ONLY',
       'cases':observations,'actual_qrtr_or_fastrpc_calls':False,'phone_hardware_qualified':False},sort_keys=True),flush=True)

if __name__=='__main__':main()
