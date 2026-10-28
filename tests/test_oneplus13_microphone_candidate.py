# SPDX-License-Identifier: GPL-2.0-only
import importlib.util,math,struct,sys,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO=HERE.parent
TOOLS=REPO/'tools/oneplus13'
sys.path.insert(0,str(REPO/'tools/oneplus13'))
from stock import Fdt,cells,strings
def load(name):
 s=importlib.util.spec_from_file_location(name,TOOLS/(name+'.py'))
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
dtb=load('microphone-dtb');capture=load('ram-microphone-check')
acoustic=load('ram-acoustic-check')
class MicrophoneCandidate(unittest.TestCase):
 def test_acoustic_signal_separates_channels_and_requires_volume_contrast(self):
  wave=acoustic.signal();values=struct.unpack('<'+str(len(wave)//2)+'h',wave)
  self.assertEqual(len(wave),48000*2*2*2)
  self.assertFalse(any(values[1:48000*2:2]));self.assertFalse(any(values[48000*2::2]))
  self.assertLessEqual(max(abs(x) for x in values),4125)
  muted=24000;live=168000
  def make(contrast=True):
   out=bytearray()
   for i in range(48000*8):
    v=round(10*math.sin(2*math.pi*997*i/48000))
    for start,level in ((muted,10),(live,100000 if contrast else 10)):
     t=i-start
     if 0<=t<96000:v+=round(level*math.sin(2*math.pi*(440 if t<48000 else 880)*t/48000))
    out.extend(struct.pack('<ii',v,v//2))
   return bytes(out)
  result=acoustic.analyze(make(),muted,live)
  self.assertTrue(result['correlated_two_speaker_response_pass'])
  self.assertFalse(result['human_listening_performed'])
  self.assertFalse(acoustic.analyze(make(False),muted,live)['correlated_two_speaker_response_pass'])
  with self.assertRaises(ValueError):acoustic.analyze(b'',muted,live)
 def test_alternative_changes_only_reviewed_audio_nodes(self):
  base=(REPO/'devices/oneplus13/qualified-data/calibrated.dtb').read_bytes()
  speaker,_=dtb.audio.derive(base);candidate,proof=dtb.derive(base)
  old,new=Fdt(speaker),Fdt(candidate)
  self.assertEqual(set(old.nodes),set(new.nodes))
  for path in old.nodes:
   if path not in {dtb.WCD,'/sound',dtb.CAPTURE}:self.assertEqual(old.nodes[path],new.nodes[path],path)
  wcd=new.nodes[dtb.WCD]
  self.assertEqual(wcd['vdd-px-supply'],new.nodes[dtb.SUPPLY]['phandle'])
  self.assertEqual(cells(wcd['qcom,micbias4-microvolt']),[2700000])
  self.assertEqual(strings(new.nodes[dtb.CAPTURE]['convert-sample-format']),['s24_le'])
  self.assertEqual(strings(new.nodes['/sound/wcd-playback-dai-link']['status']),['disabled'])
  self.assertEqual(strings(new.nodes['/sound/oneplus13-speaker-playback-dai-link'].get('status',b'okay\0')),['okay'])
  self.assertEqual(new.reservations,old.reservations)
  self.assertFalse(proof['microphone_or_acoustic_acceptance'])
 def test_real_s24_container_signed_decode_and_failed_channel(self):
  frames=48000*2
  raw=b''.join(struct.pack('<ii',round(8388608*.01*math.sin(2*math.pi*440*n/48000)),
                                round(8388608*.02*math.cos(2*math.pi*440*n/48000))) for n in range(frames))
  result=capture.summarize(raw)
  self.assertTrue(result['bounded_nonzero_capture_pass'])
  self.assertAlmostEqual(result['channels'][0]['rms'],.01/math.sqrt(2),places=6)
  self.assertAlmostEqual(result['channels'][1]['rms'],.02/math.sqrt(2),places=6)
  self.assertFalse(result['physical_microphone_or_acoustic_response_accepted'])
  zero=bytes(len(raw));self.assertFalse(capture.summarize(zero)['bounded_nonzero_capture_pass'])
  one_dead=b''.join(struct.pack('<ii',1000 if n%2 else -1000,0) for n in range(frames))
  self.assertFalse(capture.summarize(one_dead)['bounded_nonzero_capture_pass'])
  clipped=struct.pack('<ii',8388607,-8388608)*frames
  self.assertFalse(capture.summarize(clipped)['bounded_nonzero_capture_pass'])
  with self.assertRaises(ValueError):capture.summarize(raw[:-8])
if __name__=='__main__':unittest.main()
