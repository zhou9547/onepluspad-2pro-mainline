#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One RAM-only speaker graph experiment: maximum attenuation and digital zero."""
import argparse,hashlib,json,os,re,subprocess,time
from pathlib import Path

MARKER=Path('/run/oneplus13/audio-silence-attempted')
POLICY=Path('/etc/modprobe.d/91-oneplus13-unreviewed-peripherals.conf')
CARD='OnePlus13-Speaker-Test'

def run(argv,timeout=5):
    p=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
    if p.returncode:raise ValueError('Audio command failed: '+Path(argv[0]).name+' rc='+str(p.returncode))
    if len(p.stdout)>65536:raise ValueError('Audio output bound exceeded')
    return p.stdout

def module_order(text,roots):
    graph={}
    for row in text.splitlines():
        path,sep,deps=row.partition(':')
        if not sep:raise ValueError('Malformed module dependency')
        for p in [path,*deps.split()]:
            if not re.fullmatch(r'kernel/[A-Za-z0-9_./+-]+\.ko',p) or '..' in Path(p).parts:
                raise ValueError('Unsafe module dependency')
        name=Path(path).stem.replace('-','_')
        if name in graph:raise ValueError('Duplicate module name')
        graph[name]=[Path(p).stem.replace('-','_') for p in deps.split()]
    result=[];pending=set()
    def visit(name):
        if name in result:return
        if name in pending or name not in graph:raise ValueError('Cyclic or missing audio dependency')
        pending.add(name)
        for dep in graph[name]:visit(dep)
        pending.remove(name);result.append(name)
    for name in roots:visit(name)
    if len(result)>64:raise ValueError('Oversized audio module closure')
    return result

def amp_state(text):
    match=re.fullmatch(r'id=([0-9a-f]{4}) channel=([01]) volume=([0-9]{1,4}) powered=([01]) faulted=([01]) sysst=([0-9a-f]{4}) sysctrl=([0-9a-f]{4}) attenuation=([0-9]{1,4})\s*',text)
    if not match:raise ValueError('Unknown amplifier status')
    v=match.groups()
    state=dict(zip(['id','channel','volume','powered','faulted','sysst','sysctrl','attenuation'],
                   [int(x,16) if i in (0,5,6) else int(x) for i,x in enumerate(v)]))
    if state['id']!=0x2308 or state['volume']!=0 or state['faulted'] or state['attenuation']!=1023:
        raise ValueError('Amplifier identity, mute or health condition failed')
    return state

def active_state(state):
    required=(1<<4)|(1<<0)|(1<<9)|(1<<8)
    faults=(1<<14)|(1<<11)|(1<<5)|(1<<3)|(1<<1)
    return bool(state['powered'] and state['sysst']&required==required and
                not state['sysst']&faults and not state['sysctrl']&3)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--release',required=True)
    p.add_argument('--policy-sha256',required=True)
    a=p.parse_args()
    if os.geteuid()!=0 or os.uname().release!=a.release:raise ValueError('Wrong audio root/kernel')
    if not Path('/run/oneplus13/ram-session').is_file():raise ValueError('Not a protected RAM session')
    mounts=Path('/proc/mounts').read_text()
    if not re.search(r'^overlay / overlay ',mounts,re.M):raise ValueError('RAM overlay required')
    for d in Path('/sys/class/block').iterdir():
        if not d.name.startswith(('ram','zram','loop')) and (d/'ro').read_text().strip()!='1':
            raise ValueError('Physical storage is writable')
    for unit in ['oneplus13-ram-guard.service','oneplus13-ram-deadline.timer']:
        run(['systemctl','is-active','--quiet',unit])
    if hashlib.sha256(POLICY.read_bytes()).hexdigest()!=a.policy_sha256:raise ValueError('Wrong peripheral policy')
    if 'install snd_soc_aw88461 /bin/false\n' not in POLICY.read_text():raise ValueError('Missing amplifier policy')
    with MARKER.open('x') as f:f.write('ONE_MAX_ATTENUATION_DIGITAL_ZERO_TEST\n')
    dep=Path('/usr/lib/modules')/a.release/'modules.dep'
    # These names are checked against the actual module dependency inventory.
    roots=['snd_soc_aw88461','snd_q6apm','q6apm_dai',
           'q6apm_lpass_dais','q6prm','q6prm_clocks',
           'snd_soc_sc8280xp']
    ordered=module_order(dep.read_text(),roots)
    for name in ordered:run(['modprobe','--ignore-install',name],timeout=8)
    until=time.monotonic()+12
    while True:
        cards=Path('/proc/asound/cards').read_text()
        matches=re.findall(r'^\s*(\d+) \[.*\]: .* - '+re.escape(CARD)+r'$',cards,re.M)
        if len(matches)==1:break
        if time.monotonic()>=until:raise ValueError('Speaker test card did not register')
        time.sleep(.2)
    card=matches[0]
    paths=sorted(Path('/sys/bus/i2c/devices').glob('*/phone_state'))
    if len(paths)!=2:raise ValueError('Expected exactly two bound AW88461 state nodes')
    before=[amp_state(x.read_text()) for x in paths]
    if {s['channel'] for s in before}!={0,1} or any(s['powered'] for s in before):
        raise ValueError('Amplifiers already active')
    route='Secondary MI2S Audio Mixer MultiMedia1'
    dump=run(['amixer','-c',card,'cget','name='+route])
    old=re.search(r'^\s*: values=(.*)$',dump,re.M)
    if not old or old[1] not in ('off,off','off'):raise ValueError('Unexpected initial audio route')
    player=None;active=[]
    try:
        run(['amixer','-q','-c',card,'cset','name='+route,'on,on' if ',' in old[1] else 'on'])
        player=subprocess.Popen(['aplay','-q','-D','hw:'+card+',0','-t','raw',
             '-f','S16_LE','-r','48000','-c','2','-d','2','/dev/zero'],
             stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        for _ in range(2):
            time.sleep(.45)
            states=[amp_state(x.read_text()) for x in paths]
            active.append(states)
            if not all(active_state(s) for s in states):raise ValueError('Amplifier clock/power state did not qualify')
        if player.wait(timeout=4)!=0:raise ValueError('Digital-zero PCM stream failed')
    finally:
        if player is not None:
            if player.poll() is None:player.terminate()
            try:player.communicate(timeout=3)
            except subprocess.TimeoutExpired:player.kill();player.communicate(timeout=2)
        run(['amixer','-q','-c',card,'cset','name='+route,old[1]])
    time.sleep(.2)
    after=[amp_state(x.read_text()) for x in paths]
    if any(s['powered'] for s in after):raise ValueError('Amplifiers did not stop')
    print('RAM_AUDIO_SILENCE_RESULT '+json.dumps({'source':'NATIVE_AW88461_SECONDARY_MI2S',
        'card_registered':True,'format':'S16_LE','rate_hz':48000,'channels':2,
        'amplifier_ids':[s['id'] for s in before],'active_state_samples':active,
        'digital_zero_pcm_pass':True,'default_attenuation_preserved':True,
        'route_restored':True,'amplifiers_stopped':True,
        'audible_playback_tested':False,'dynamic_protection_qualified':False,
        'audio_accepted':False},sort_keys=True),flush=True)

if __name__=='__main__':main()
