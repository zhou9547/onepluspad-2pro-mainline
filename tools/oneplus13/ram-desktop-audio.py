#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Explicit, reversible RAM speaker integration with the desktop volume mixer."""
import argparse,hashlib,json,os,pwd,re,shutil,subprocess,time
from pathlib import Path
ROOT=Path('/usr/lib/oneplus13-audio')
BINDINGS=ROOT/'desktop-bindings.json'
RULE=Path('/etc/wireplumber/wireplumber.conf.d/95-oneplus13-desktop-audio.conf')
CARD='OnePlus13-Audio-Probe'
UNITS=['pipewire.service','pipewire-pulse.service','wireplumber.service']

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(args,timeout=8,user=False):
    if user:
        uid=pwd.getpwnam('a').pw_uid
        args=['runuser','-u','a','--','env','XDG_RUNTIME_DIR=/run/user/'+str(uid),
              'DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/'+str(uid)+'/bus',*args]
    p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    if p.returncode:raise ValueError('Desktop audio command failed: '+Path(args[0]).name+' rc='+str(p.returncode))
    if len(p.stdout)>2*1024*1024:raise ValueError('Oversized desktop audio output')
    return p.stdout

def validate_policy(actual,expected):
    if hashlib.sha256(actual).hexdigest()==expected:return
    original=actual
    for name in ('cec','ubwc_config'):
        rule=('install '+name+' /bin/true\n').encode()
        if original.count(rule)!=1:raise ValueError('Unknown post-display policy')
        original=original.replace(rule,('install '+name+' /bin/false\n').encode(),1)
    if hashlib.sha256(original).hexdigest()!=expected:raise ValueError('Peripheral denial changed')

def guard():
    doc=json.loads(BINDINGS.read_text())
    if os.geteuid()!=0 or doc['kernel_release']!=os.uname().release:raise ValueError('Wrong root/kernel')
    if not Path('/run/oneplus13/ram-session').is_file() or not any(r.split()[1:3]==['/','overlay'] for r in Path('/proc/mounts').read_text().splitlines()):
        raise ValueError('Protected RAM root required')
    for p in Path('/sys/class/block').iterdir():
        if not p.name.startswith(('ram','loop','zram')) and (p/'ro').read_text().strip()!='1':raise ValueError('Writable physical storage')
    for unit in ('oneplus13-ram-guard.service','oneplus13-ram-deadline.timer'):run(['systemctl','is-active','--quiet',unit])
    for name,digest in doc['files'].items():
        if sha(Path('/')/name)!=digest:raise ValueError('Desktop audio source changed: '+name)
    module=Path('/usr/lib/modules')/doc['kernel_release']/'kernel/sound/soc/codecs/snd-soc-aw88461.ko'
    if sha(module)!=doc['amplifier_module_sha256']:raise ValueError('Wrong amplifier module')
    validate_policy(Path('/etc/modprobe.d/91-oneplus13-unreviewed-peripherals.conf').read_bytes(),doc['original_policy_sha256'])
    if Path('/proc/device-tree/sound/model').read_bytes()!=CARD.encode()+b'\0':raise ValueError('Wrong audio boot alternative')
    cards=re.findall(r'^\s*(\d+) \[.*\]: .* - '+re.escape(CARD)+r'$',Path('/proc/asound/cards').read_text(),re.M)
    if len(cards)!=1:raise ValueError('Unique phone card required')
    return doc,cards[0]

def mixer(card,name,value):run(['amixer','-q','-c',card,'cset','name='+name,value])

def disable(card):
    errors=[]
    try:
        if RULE.exists():
            if RULE.is_symlink() or RULE.read_bytes()!=(ROOT/RULE.name).read_bytes():raise ValueError('Unknown desktop rule')
            RULE.unlink()
        run(['systemctl','--user','restart',*UNITS],timeout=15,user=True)
    except Exception as e:errors.append(str(e))
    for name,value in [('Amp0 Playback Volume','0'),('Amp1 Playback Volume','0'),('Secondary MI2S Audio Mixer MultiMedia1','off,off')]:
        try:mixer(card,name,value)
        except Exception as e:errors.append(str(e))
    if errors:raise ValueError('Desktop audio cleanup failed: '+'; '.join(errors))

def enable(card):
    for folder,keys in [('microphone-check',('bounded_nonzero_capture_pass','controls_restored','raw_audio_deleted')),
                        ('acoustic-check',('correlated_two_speaker_response_pass','controls_restored','raw_audio_deleted','amplifiers_stopped'))]:
        result=json.loads((Path('/run/oneplus13')/folder/'result.json').read_text())
        if not all(result.get(k) is True for k in keys):raise ValueError('Independent native audio precheck required')
    if RULE.exists():raise ValueError('Desktop audio already attempted')
    if 'HiFi' not in run(['alsaucm','-c','hw:'+card,'list','_verbs']):raise ValueError('Phone UCM profile unavailable')
    # Keep GNOME from exposing amplification beyond the software-unity ceiling.
    run(['gsettings','set','org.gnome.desktop.sound','allow-volume-above-100-percent','false'],user=True)
    shutil.copyfile(ROOT/RULE.name,RULE)
    run(['systemctl','--user','restart',*UNITS],timeout=15,user=True)
    until=time.monotonic()+12
    while True:
        sinks=[]
        for obj in json.loads(run(['pw-dump'],user=True)):
            props=obj.get('info',{}).get('props',{})
            if props.get('media.class')=='Audio/Sink' and str(props.get('api.alsa.pcm.card'))==card:
                sinks.append({'id':obj['id'],'name':props.get('node.name'),'properties':props})
        if len(sinks)==1:break
        if time.monotonic()>until:raise ValueError('Unique desktop speaker sink did not appear')
        time.sleep(.3)
    sink=sinks[0]
    run(['wpctl','set-default',str(sink['id'])],user=True)
    run(['wpctl','set-volume','--limit','1',str(sink['id']),'0.5'],user=True)
    run(['wpctl','set-mute',str(sink['id']),'0'],user=True)
    return {'scope':'EXPLICIT_RAM_PIPEWIRE_SPEAKER_CANDIDATE','sink_id':sink['id'],'sink_name':sink['name'],
            'ucm_speakers':True,'desktop_software_volume':True,'initial_volume':0.5,
            'hardware_test_level':896,'extra_profile_attenuation_db':11.921875,
            'dynamic_protection_qualified':False,'normal_desktop_playback_qualified':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['enable','disable']);args=p.parse_args()
    doc,card=guard()
    if args.mode=='disable':disable(card);print('RAM_DESKTOP_AUDIO_DISABLED');return
    try:result=enable(card)
    except Exception:
        disable(card)
        raise
    print('RAM_DESKTOP_AUDIO_RESULT '+json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
