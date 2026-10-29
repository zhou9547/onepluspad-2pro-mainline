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


def record(doc):
    temporary=STATE/'result.tmp'
    temporary.write_text(json.dumps(doc,sort_keys=True)+'\n')
    temporary.replace(STATE/'result.json')
    print('WATCHDOG_RECOVERY_RESULT '+json.dumps(doc,sort_keys=True),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',required=True)
    parser.add_argument('--arm-one-reset',action='store_true',required=True)
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
            'keepalive_verified':False,'reset_observed':False}
    fd=None
    try:
        fd=os.open(device,os.O_WRONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
        support=bytearray(40);fcntl.ioctl(fd,WDIOC_GETSUPPORT,support,True)
        if bytes(support[8:]).split(b'\0')[0]!=b'Gunyah Watchdog':raise ValueError('Wrong ioctl identity')
        options=int.from_bytes(support[:4],'little')
        if options&0x8180!=0x8180:raise ValueError('Missing timeout/keepalive/magic-close support')
        if ioctl_int(fd,WDIOC_SETTIMEOUT,12)!=12 or ioctl_int(fd,WDIOC_GETTIMEOUT)!=12:
            raise ValueError('Watchdog timeout readback mismatch')
        ioctl_int(fd,WDIOC_KEEPALIVE)
        first=ioctl_int(fd,WDIOC_GETTIMELEFT)
        time.sleep(2)
        second=ioctl_int(fd,WDIOC_GETTIMELEFT)
        if not 0<second<first<=12:raise ValueError('Watchdog countdown not observed')
        report['countdown_verified']=True
        ioctl_int(fd,WDIOC_KEEPALIVE)
        third=ioctl_int(fd,WDIOC_GETTIMELEFT)
        if not second<third<=12:raise ValueError('Watchdog keepalive not observed')
        if (base/'state').read_text().strip()!='active':raise ValueError('Watchdog not active')
        report.update(armed=True,keepalive_verified=True,timeout_seconds=12,
                      last_timeleft=third,remaining_no_ping_wait_seconds=20)
        record(report)
        # Keep the open descriptor alive without pings; do not ask PID1 to reboot.
        # If the hypervisor fails to reset, the finally block disarms after20s.
        time.sleep(20)
        report['reset_failed']=True
        raise RuntimeError('Watchdog failed to reset within bounded no-ping wait')
    finally:
        if fd is not None:
            os.write(fd,b'V');os.close(fd)
            report['disarmed_after_return']=True
        record(report)


if __name__=='__main__':main()
