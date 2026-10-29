#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One manual RAM-only Gunyah watchdog reset; no suspend or storage writes."""
import argparse,array,fcntl,json,os,stat,subprocess,time
from pathlib import Path

STATE=Path('/run/oneplus13/watchdog-recovery')
WDIOC_GETSUPPORT=0x80285700
WDIOC_SETTIMEOUT=0xc0045706
WDIOC_GETTIMEOUT=0x80045707
WDIOC_KEEPALIVE=0x80045705
WDIOC_GETTIMELEFT=0x8004570a


def validate_inventory(base):
    fields={name:(base/name).read_text().strip() for name in
            ('identity','state','timeout','nowayout','dev')}
    if fields['identity']!='Gunyah Watchdog':raise ValueError('Wrong watchdog identity')
    if fields['state']!='inactive' or fields['nowayout']!='0':
        raise ValueError('Watchdog already owned or cannot be disarmed')
    if fields['timeout']!='32':raise ValueError('Unexpected Gunyah timeout range')
    numbers=fields['dev'].split(':')
    if len(numbers)!=2 or not all(x.isdecimal() for x in numbers):raise ValueError('Invalid watchdog dev_t')
    return tuple(map(int,numbers))


def ioctl_int(fd,request,value=0):
    data=array.array('i',[value]);fcntl.ioctl(fd,request,data,True)
    return data[0]


def status_sample(base,label,required=False):
    """Read the driver's STATUS-only diagnostic, without petting the timer."""
    path=base/'device/hypervisor_status'
    if not path.is_file():
        if required:raise ValueError('Required hypervisor status diagnostic is absent')
        return {'label':label,'available':False}
    with path.open() as stream:text=stream.read(257)
    if len(text)>256:raise ValueError('Oversized hypervisor status diagnostic')
    pairs=[item.split('=') for item in text.split()]
    if (len(pairs)!=4 or any(len(p)!=2 for p in pairs) or
        {p[0] for p in pairs}!={'result','enabled','expired','elapsed_raw'}):
        raise ValueError('Malformed hypervisor status diagnostic')
    values={key:int(value) for key,value in pairs}
    if (values['result']!=0 or values['enabled'] not in (0,1) or
        values['expired'] not in (0,1) or not 0<=values['elapsed_raw']<=0xffffffff):
        raise ValueError('Invalid hypervisor status diagnostic values')
    return {'label':label,'available':True,'monotonic_seconds':time.monotonic(),**values}


def record(doc):
    temporary=STATE/'result.tmp'
    temporary.write_text(json.dumps(doc,sort_keys=True)+'\n')
    temporary.replace(STATE/'result.json')
    print('WATCHDOG_RECOVERY_RESULT '+json.dumps(doc,sort_keys=True),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',required=True)
    parser.add_argument('--arm-one-reset',action='store_true',required=True)
    parser.add_argument('--require-hypervisor-status',action='store_true')
    args=parser.parse_args()
    if os.geteuid()!=0 or os.uname().release!=args.release:raise ValueError('Wrong root/kernel')
    if not Path('/run/oneplus13/ram-session').is_file():raise ValueError('Protected RAM session required')
    if not any(x.startswith('overlay / overlay ') for x in Path('/proc/mounts').read_text().splitlines()):
        raise ValueError('RAM overlay required')
    for p in Path('/sys/class/block').iterdir():
        if not p.name.startswith(('ram','zram','loop')) and (p/'ro').read_text().strip()!='1':
            raise ValueError('Writable physical storage')
    for unit in ('oneplus13-ram-guard.service','oneplus13-ram-deadline.timer'):
        subprocess.run(['systemctl','is-active','--quiet',unit],check=True,timeout=3)
    uptime=float(Path('/proc/uptime').read_text().split()[0])
    if not 60<uptime<510:raise ValueError('Insufficient bounded recovery window')
    candidates=[p for p in Path('/sys/class/watchdog').glob('watchdog[0-9]*')
                if (p/'identity').read_text().strip()=='Gunyah Watchdog']
    if len(candidates)!=1:raise ValueError('Ambiguous Gunyah watchdog')
    base=candidates[0];device=Path('/dev')/base.name
    major,minor=validate_inventory(base)
    node=device.stat()
    if not stat.S_ISCHR(node.st_mode) or (os.major(node.st_rdev),os.minor(node.st_rdev))!=(major,minor):
        raise ValueError('Wrong watchdog character device')
    STATE.mkdir(mode=0o700,exist_ok=False)
    report={'scope':'ONE_MANUAL_RAM_GUNYAH_WATCHDOG_RESET','suspend_requested':False,
            'partition_writes':0,'armed':False,'countdown_verified':False,
            'keepalive_verified':False,'reset_observed':False,'hardware_samples':[]}
    def sample(label):
        report['hardware_samples'].append(status_sample(base,label,args.require_hypervisor_status))
    fd=None
    try:
        report['stage']='inactive-status'
        sample('inactive-before-open')
        report['stage']='device-open'
        fd=os.open(device,os.O_WRONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
        sample('after-open')
        report['stage']='support'
        support=bytearray(40);fcntl.ioctl(fd,WDIOC_GETSUPPORT,support,True)
        if bytes(support[8:]).split(b'\0')[0]!=b'Gunyah Watchdog':raise ValueError('Wrong ioctl identity')
        options=int.from_bytes(support[:4],'little')
        report['support_options']=options
        if options&0x8180!=0x8180:raise ValueError('Missing timeout/keepalive/magic-close support')
        report['stage']='timeout'
        report['set_timeout_readback']=ioctl_int(fd,WDIOC_SETTIMEOUT,12)
        report['get_timeout_readback']=ioctl_int(fd,WDIOC_GETTIMEOUT)
        if report['set_timeout_readback']!=12 or report['get_timeout_readback']!=12:
            raise ValueError('Watchdog timeout readback mismatch')
        report['stage']='first-keepalive'
        ioctl_int(fd,WDIOC_KEEPALIVE)
        sample('first-keepalive')
        report['stage']='countdown'
        first=ioctl_int(fd,WDIOC_GETTIMELEFT)
        report['first_timeleft']=first
        sample('first-timeleft')
        time.sleep(2)
        second=ioctl_int(fd,WDIOC_GETTIMELEFT)
        report['second_timeleft']=second
        sample('second-timeleft')
        if not 0<second<first<=12:raise ValueError('Watchdog countdown not observed')
        report['countdown_verified']=True
        report['stage']='second-keepalive'
        ioctl_int(fd,WDIOC_KEEPALIVE)
        sample('second-keepalive')
        third=ioctl_int(fd,WDIOC_GETTIMELEFT)
        report['third_timeleft']=third
        if not second<third<=12:raise ValueError('Watchdog keepalive not observed')
        if (base/'state').read_text().strip()!='active':raise ValueError('Watchdog not active')
        report.update(armed=True,keepalive_verified=True,timeout_seconds=12,
                      last_timeleft=third,remaining_no_ping_wait_seconds=20,stage='no-ping-wait')
        record(report)
        # Keep the open descriptor alive without pings; do not ask PID1 to reboot.
        # If the hypervisor fails to reset, the finally block disarms after20s.
        time.sleep(20)
        report['reset_failed']=True
        raise RuntimeError('Watchdog failed to reset within bounded no-ping wait')
    except (OSError,ValueError,RuntimeError) as error:
        report['failure_category']=type(error).__name__
        report['failure_reason']=str(error)
        if isinstance(error,OSError):report['errno']=error.errno
        raise
    finally:
        if fd is not None:
            try:os.write(fd,b'V')
            finally:os.close(fd)
            report['disarmed_after_return']=(base/'state').read_text().strip()=='inactive'
        record(report)


if __name__=='__main__':main()
