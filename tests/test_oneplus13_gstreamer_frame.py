# SPDX-License-Identifier: GPL-2.0-only
import importlib.util,json,os,subprocess,sys,unittest
from unittest.mock import Mock
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'tools/oneplus13/ram-gstreamer-frame.py'
spec=importlib.util.spec_from_file_location('gst_phone_frame',SCRIPT)
video=importlib.util.module_from_spec(spec);spec.loader.exec_module(video)

class GStreamerFrame(unittest.TestCase):
    def decoder_registry(self,rows):
        gst=Mock();factories=[];devices={}
        for name,plugin,path in rows:
            factory=Mock();factory.get_name.return_value=name;factory.get_plugin_name.return_value=plugin
            factories.append(factory)
            candidate=Mock();candidate.find_property.return_value=object()
            candidate.get_property.return_value=path
            candidate.set_property.side_effect=TypeError('property device is not writable')
            devices[name]=candidate
        gst.ElementFactory.list_get_elements.return_value=factories
        gst.ElementFactory.make.side_effect=lambda name,unused:devices[name]
        return gst,devices

    def test_selects_exact_read_only_device_without_writing_property(self):
        gst,devices=self.decoder_registry([
            ('v4l2h264dec','video4linux2','/dev/video0'),
            ('v4l2video1h264dec','video4linux2','/dev/video1')])
        decoder,name=video.select_decoder(gst,'/dev/video1')
        self.assertIs(decoder,devices['v4l2video1h264dec'])
        self.assertEqual(name,'v4l2video1h264dec')
        for item in devices.values():item.set_property.assert_not_called()

    def test_rejects_other_device_plugin_and_software_decoder(self):
        gst,devices=self.decoder_registry([
            ('v4l2h264dec','video4linux2','/dev/video0'),
            ('v4l2video1h264dec','untrusted','/dev/video1'),
            ('avdec_h264','libav','/dev/video1')])
        with self.assertRaises(ValueError):video.select_decoder(gst,'/dev/video1')
        self.assertEqual([item.args[0] for item in gst.ElementFactory.make.call_args_list],['v4l2h264dec'])
        for item in devices.values():item.set_property.assert_not_called()

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
