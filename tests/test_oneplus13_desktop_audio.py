"""Desktop audio preserves all unrelated denials and caps hardware/software gain."""
import hashlib,importlib.util,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('desktop_audio',R/'tools/oneplus13/ram-desktop-audio.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class DesktopAudio(unittest.TestCase):
    def test_sink_binding_follows_pipewire_device_id(self):
        objects=[
            {'id':7,'type':'PipeWire:Interface:Device','info':{'props':{
                'api.alsa.card':'0','api.alsa.card.name':'OnePlus13-Audio-Probe'}}},
            {'id':10,'type':'PipeWire:Interface:Node','info':{'props':{
                'media.class':'Audio/Sink','device.id':7,'node.name':'phone_speaker'}}},
            {'id':11,'type':'PipeWire:Interface:Node','info':{'props':{
                'media.class':'Audio/Sink','device.id':99,'node.name':'other'}}},
        ]
        result=m.desktop_sinks(objects,'0')
        self.assertEqual([item['name'] for item in result],['phone_speaker'])
        self.assertNotIn('OnePlus13-Audio-Probe',str(result))

    def test_only_original_or_exact_display_prerequisite_policy_is_allowed(self):
        original=b'install cec /bin/false\ninstall ubwc_config /bin/false\ninstall snd_soc_aw88461 /bin/false\n'
        digest=hashlib.sha256(original).hexdigest()
        m.validate_policy(original,digest)
        display=original.replace(b'install cec /bin/false',b'install cec /bin/true').replace(b'install ubwc_config /bin/false',b'install ubwc_config /bin/true')
        m.validate_policy(display,digest)
        with self.assertRaises(ValueError):m.validate_policy(display.replace(b'install snd_soc_aw88461 /bin/false',b'install snd_soc_aw88461 /bin/true'),digest)

    def test_phone_ucm_uses_qualified_mi2s_and_restores_mute(self):
        text=(R/'devices/oneplus13/audio/HiFi.conf').read_text()
        self.assertIn("name='Secondary MI2S Audio Mixer MultiMedia1' 1,1",text)
        self.assertIn("name='Secondary MI2S Audio Mixer MultiMedia1' 0,0",text)
        for channel in (0,1):
            self.assertIn("name='Amp"+str(channel)+" Playback Volume' 896",text)
            self.assertIn("name='Amp"+str(channel)+" Playback Volume' 0",text)
        self.assertNotIn('Secondary TDM',text)

    def test_desktop_volume_is_soft_and_never_amplifies_above_unity(self):
        text=(R/'devices/oneplus13/audio/95-oneplus13-desktop-audio.conf').read_text()
        self.assertIn('api.alsa.soft-mixer = true',text)
        self.assertIn('channelmix.max-volume = 1.0',text)
        self.assertIn('audio.format = "S16LE"',text)
        self.assertIn('OnePlus13-Audio-Probe',text)
        self.assertIn('device.disabled = true',(R/'devices/oneplus13/audio/90-oneplus13-manual-audio.conf').read_text())

if __name__=='__main__':unittest.main()
