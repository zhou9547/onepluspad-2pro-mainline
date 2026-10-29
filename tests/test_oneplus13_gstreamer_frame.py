# SPDX-License-Identifier: GPL-2.0-only
import importlib.util,json,os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools/oneplus13/ram-gstreamer-frame.py'
spec=importlib.util.spec_from_file_location('gst_phone_frame',SCRIPT)
video=importlib.util.module_from_spec(spec);spec.loader.exec_module(video)

class GStreamerFrame(unittest.TestCase):
    def test_pixels_reject_truncation_bad_layout_and_single_corrupted_pixel(self):
        stride=384;raw=bytearray(stride*256*3//2)
        for y in range(240):
            for bar,value in enumerate((81,145,41,235)):
                raw[y*stride+bar*80:y*stride+(bar+1)*80]=bytes([value])*80
        video.verify_pixels(raw,stride)
        for data,s,o in [(raw[:100],384,0),(raw,319,0),(raw,2049,0),
                         (raw,384,-1),(raw,384,65537),(raw,True,0)]:
            with self.subTest(stride=s,offset=o),self.assertRaises(ValueError):
                video.verify_pixels(data,s,o)
        raw[20*stride+20]+=7
        with self.assertRaises(ValueError):video.verify_pixels(raw,stride)

    @unittest.skipUnless(os.name=='posix','Linux guard check')
    def test_unguarded_cli_rejects_before_framework_or_device_access(self):
        env={k:v for k,v in os.environ.items() if k!='ONEPLUS13_GUARDED_VIDEO_TEST'}
        r=subprocess.run([sys.executable,str(SCRIPT),'--device','/dev/video999',
                          '--fixture','/nonexistent'],capture_output=True,text=True,env=env,timeout=5)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('Guarded explicit device',r.stderr)
        self.assertNotIn('gi.repository',r.stderr)

    @unittest.skipUnless(os.name=='posix','Native framework selftest')
    def test_native_raw_framework_pts_pixels_and_null_teardown(self):
        try:video.gstreamer()
        except (ImportError,ValueError):self.skipTest('GStreamer GI packages unavailable')
        r=subprocess.run([sys.executable,str(SCRIPT),'--selftest'],check=True,
                         capture_output=True,text=True,timeout=15)
        row=json.loads(r.stdout.strip().removeprefix('GSTREAMER_FRAME_RESULT '))
        self.assertTrue(row['frame_verified'] and row['pipeline_stopped'])
        self.assertIsNone(row['hardware_decoder_factory'])
        self.assertFalse(row['software_fallback'])
        self.assertEqual(row['pts_ns'],12345000000)
        self.assertEqual(row['scope'],'GSTREAMER_RAW_PIPELINE_SELFTEST_NO_DECODE_REQUEST')

if __name__=='__main__':unittest.main()
