# SPDX-License-Identifier: GPL-2.0-only
import copy,hashlib,importlib.util,io,json,os,stat,struct,tarfile,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parents[1]/'tools/oneplus13/ram-sensor-fileserver.py'
spec=importlib.util.spec_from_file_location('phone_sensor_fileserver',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

TRACE='''100 ioctl(0x3, 0x5208, 0) = 0 <0.001>
100 ioctl(0x3, 0xc0105203, 0xffff) = 0 <0.001>
100 ioctl(0x3, 0xc0105203, 0xffff) = 0 <0.001>
100 ioctl(0x3, 0xc0105203, 0xffff) = 0 <0.001>
100 openat(AT_FDCWD, "/usr/share/erhai-sensors/hexagonrpcd/sensors/registry", O_RDONLY|O_DIRECTORY) = 4 <0.001>
100 openat(AT_FDCWD, "/usr/share/erhai-sensors/hexagonrpcd/sensors/sns_reg.conf", O_RDONLY) = 5 <0.001>
'''

class Archive(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        elf=bytearray(64);elf[:6]=b'\x7fELF\x02\x01';struct.pack_into('<H',elf,18,183)
        self.entries={m.PREFIX+n:(bytes(elf),0o755,None) for n in ['bin/hexagonrpcd','bin/ssccli','libexec/iio-sensor-proxy','lib/hex.so','lib/ssc.so']}
        for name in ['usr/share/erhai-sensors/hexagonrpcd/sensors/sns_reg.conf','var/lib/erhai/sensors/persist/registry/sample']:
            self.entries[name]=(b'phone-data',0o640,None)
        self.entries.update({n:(None,0o777,t) for n,t in m.LINKS.items()})
        self.manifest={'scope':'PRIVATE_PHONE_SENSOR_FILESERVER_INPUTS','links':m.LINKS,
            'files':{n:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest(),'mode':mode} for n,(v,mode,t) in self.entries.items() if v is not None}}
    def archive(self,entries=None):
        path=self.root/'runtime.tar.gz'
        with tarfile.open(path,'w:gz') as tf:
            for n,(value,mode,target) in (entries or self.entries).items():
                member=tarfile.TarInfo(n);member.mode=mode
                if target is None:member.size=len(value);tf.addfile(member,io.BytesIO(value))
                else:member.type=tarfile.SYMTYPE;member.linkname=target;tf.addfile(member)
        return path
    def test_exact_elf_data_and_three_mapping_links(self):
        self.assertEqual(m.archive_entries(self.archive(),self.manifest),self.entries)
    def test_changed_private_byte_rejected(self):
        changed=dict(self.entries);changed['var/lib/erhai/sensors/persist/registry/sample']=(b'other-data',0o640,None)
        with self.assertRaises(ValueError):m.archive_entries(self.archive(changed),self.manifest)
    def test_hook_outside_allowlist_rejected(self):
        changed=dict(self.entries);changed['etc/systemd/system/automatic.service']=(b'start',0o644,None)
        with self.assertRaises(ValueError):m.archive_entries(self.archive(changed),self.manifest)
    def test_wrong_mapping_rejected(self):
        changed=dict(self.entries);changed[next(iter(m.LINKS))]=(None,0o777,'/persist/registry')
        with self.assertRaises(ValueError):m.archive_entries(self.archive(changed),self.manifest)
    def test_nonarm64_elf_rejected(self):
        key=m.PREFIX+'bin/ssccli';data=bytearray(self.entries[key][0]);struct.pack_into('<H',data,18,62)
        changed=dict(self.entries);changed[key]=(bytes(data),0o755,None)
        mf=copy.deepcopy(self.manifest);mf['files'][key]['sha256']=hashlib.sha256(data).hexdigest()
        with self.assertRaises(ValueError):m.archive_entries(self.archive(changed),mf)
    def test_executable_registry_rejected(self):
        key='var/lib/erhai/sensors/persist/registry/sample';changed=dict(self.entries);changed[key]=(b'phone-data',0o755,None)
        mf=copy.deepcopy(self.manifest);mf['files'][key]['mode']=0o755
        with self.assertRaises(ValueError):m.archive_entries(self.archive(changed),mf)
    def test_traversal_rejected(self):
        for name in ['../etc/file','/etc/file','usr/../etc/file','usr//lib/file','usr\\lib\\file']:
            with self.subTest(name=name),self.assertRaises(ValueError):m.canonical(name)
    @unittest.skipIf(os.name=='nt','Install uses target Linux symlink semantics')
    def test_install_private_data_and_preserve_bytes_modes(self):
        target=self.root/'target';target.mkdir();ownership=[]
        m.install(target,self.entries,lambda *a:ownership.append(a))
        for n,(value,mode,t) in self.entries.items():
            if value is not None:
                self.assertEqual((target/n).read_bytes(),value)
                self.assertEqual(stat.S_IMODE((target/n).stat().st_mode),mode)
            else:self.assertEqual(os.readlink(target/n),t)
        self.assertEqual(len(ownership),2)
    @unittest.skipIf(os.name=='nt','Install uses target Linux symlink semantics')
    def test_preexisting_parent_link_refused_before_any_write(self):
        target=self.root/'target';target.mkdir();outside=self.root/'outside';outside.mkdir()
        (target/'usr').symlink_to(outside)
        with self.assertRaises(ValueError):m.install(target,self.entries,lambda *a:None)
        self.assertEqual(list(outside.iterdir()),[])
    def test_existing_destination_is_not_overwritten(self):
        target=self.root/'target';file=target/m.PREFIX/'bin/hexagonrpcd';file.parent.mkdir(parents=True);file.write_bytes(b'existing')
        with self.assertRaises(ValueError):m.install(target,self.entries,lambda *a:None)
        self.assertEqual(file.read_bytes(),b'existing')

class Trace(unittest.TestCase):
    def test_success_evidence_keeps_remote_release_unclaimed(self):
        result=m.trace_facts(TRACE)
        self.assertEqual(result['attach_calls'],1)
        self.assertEqual(result['successful_invoke_calls_observed'],3)
        self.assertTrue(result['registry_mapping_open_observed'])
        self.assertFalse(result['raw_rpc_arguments_or_samples_saved'])
    def test_failed_attach_cannot_pass(self):
        with self.assertRaises(ValueError):m.trace_facts(TRACE.replace('0x5208, 0) = 0','0x5208, 0) = -1 EPERM'))
    def test_second_attach_cannot_pass(self):
        with self.assertRaises(ValueError):m.trace_facts(TRACE+TRACE.splitlines()[0]+'\n')
    def test_failed_file_open_is_not_a_mapping_pass(self):
        result=m.trace_facts(TRACE.replace('O_RDONLY|O_DIRECTORY) = 4','O_RDONLY|O_DIRECTORY) = -1 ENOENT'))
        self.assertFalse(result['registry_mapping_open_observed'])

class BoundedService(unittest.TestCase):
    def test_service_has_bounds_and_no_client_or_dynamic_pd(self):
        cmd=m.service_command('/run/trace');joined=' '.join(cmd)
        for value in ['RuntimeMaxSec=40s','TimeoutStopSec=12s','Restart=no','ProtectSystem=strict','PrivateNetwork=yes','User=65534','DevicePolicy=closed']:
            self.assertIn('--property='+value,cmd)
        self.assertNotIn('ssccli',joined);self.assertNotIn('iio-sensor-proxy',joined)
        self.assertNotIn('-p',cmd);self.assertNotIn('-c',cmd)
        self.assertIn('raw=ioctl',cmd)
    def run_service(self,active='active',result='success',log='',trace=TRACE):
        calls=[];now=[0]
        def run(args,seconds=8):
            calls.append((args,seconds))
            if args[0].endswith('systemd-run'):return ''
            if args[1]=='is-active':return active
            if args[1]=='stop':return ''
            if args[1]=='show':return 'ActiveState=inactive\nSubState=dead\nMainPID=0\nResult='+result
            raise AssertionError(args)
        def sleep(value):now[0]+=value
        def contents(path,*a,**k):return trace if str(path).endswith('syscalls.log') else log
        with patch.object(m.Path,'read_text',contents):
            answer=m.serve('/run/trace',run,sleep,lambda:now[0])
        return answer,calls
    def test_success_stops_once_before_acceptance(self):
        answer,calls=self.run_service()
        self.assertTrue(answer['file_server_cleanly_stopped'])
        self.assertFalse(answer['dsp_release_acknowledgement_observed'])
        self.assertEqual(sum(a[1]=='stop' for a,s in calls if len(a)>1),1)
        self.assertIn(16,[s for a,s in calls if a[1]=='stop'])
    def test_early_exit_requests_stop_and_refuses_pass(self):
        with self.assertRaises(ValueError):self.run_service(active='inactive')
    def test_kernel_close_timeout_refuses_pass(self):
        with self.assertRaises(ValueError):self.run_service(result='timeout')
    def test_unsupported_reverse_method_refuses_pass(self):
        with self.assertRaises(ValueError):self.run_service(log='Refused request on handle 1')

if __name__=='__main__':unittest.main()
