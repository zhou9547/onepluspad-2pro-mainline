import importlib.util,sys,unittest
from pathlib import Path
TOOLS=Path(__file__).resolve().parents[1]/'tools/oneplus13'
sys.path.insert(0,str(TOOLS))
spec=importlib.util.spec_from_file_location('profile_image_verifier',TOOLS/'verify-complete-image.py')
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)

class ProfileContainerTests(unittest.TestCase):
    def manifest(self,profile):
        files={'usr/lib/oneplus13-container/kernel.config':'hash',
               'usr/libexec/oneplus13-container-kernel.py':'hash',
               'usr/libexec/oneplus13-ram-container-check.py':'hash'}
        if profile=='full':files['etc/docker/daemon.json']='hash'
        return dict(desktop_profile=profile,container_files=files,
                    container_userspace_installed=profile=='full',container_daemon_auto_started=False)

    def test_diagnostic_keeps_kernel_checks_without_docker_userspace(self):
        self.assertFalse(verifier.validate_container_profile(self.manifest('diagnostic')))

    def test_full_still_requires_docker_configuration(self):
        m=self.manifest('full');self.assertTrue(verifier.validate_container_profile(m))
        del m['container_files']['etc/docker/daemon.json']
        with self.assertRaises(ValueError):verifier.validate_container_profile(m)

    def test_diagnostic_rejects_unexpected_docker_or_missing_kernel_check(self):
        for name,action in [('etc/docker/daemon.json','add'),('usr/lib/oneplus13-container/kernel.config','remove')]:
            m=self.manifest('diagnostic')
            if action=='add':m['container_files'][name]='hash'
            else:del m['container_files'][name]
            with self.assertRaises(ValueError):verifier.validate_container_profile(m)

    def test_userspace_and_autostart_claims_must_match_payload(self):
        for profile in ['full','diagnostic']:
            for key in ['container_userspace_installed','container_daemon_auto_started']:
                m=self.manifest(profile);m[key]=not m[key]
                with self.assertRaises(ValueError):verifier.validate_container_profile(m)

    def test_unknown_profile_rejected(self):
        with self.assertRaises(ValueError):verifier.validate_container_profile(self.manifest('unknown'))

if __name__=='__main__':unittest.main()
