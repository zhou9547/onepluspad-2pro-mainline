"""One bounded NetworkManager WiFi acceptance; credentials stay in RAM files.

No raw iw scan, driver reset, module reload, persistent install or retries.
This file is safe to publish; the separate credentials JSON is private.
"""
import argparse
import json
import math
import os
import re
import shutil
from pathlib import Path
import subprocess
import tempfile
import time
import uuid


HTTPS_WRITE_OUT = ('dns_s=%{time_namelookup}\ntcp_s=%{time_connect}\n'
                   'tls_s=%{time_appconnect}\nfirst_byte_s=%{time_starttransfer}\n'
                   'total_s=%{time_total}\nhttp_code=%{http_code}\nssl_verify_result=%{ssl_verify_result}\n')


def https_metrics(output):
    """Keep numeric timings only; never publish resolver/peer/error strings."""
    result = {}
    for line in output.splitlines():
        key, sep, value = line.partition('=')
        if not sep:
            continue
        if key == 'http_code' and re.fullmatch(r'[0-9]{3}', value):
            result[key] = int(value)
        elif key == 'ssl_verify_result' and re.fullmatch(r'[0-9]{1,4}', value):
            result[key] = int(value)
        elif key in {'dns_s', 'tcp_s', 'tls_s', 'first_byte_s', 'total_s'}:
            try:
                seconds = float(value)
            except ValueError:
                continue
            if math.isfinite(seconds) and 0 <= seconds <= 60:
                result[key] = seconds
    return result


def run(argv, seconds=6):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=seconds)
        if argv[0] == 'curl' and '--write-out' in argv:
            # --silent and --output /dev/null leave only our numeric write-out
            # on stdout, even on failure. Discard raw stderr from this probe.
            return p.returncode, p.stdout[:4096]
        return p.returncode, p.stdout if p.returncode==0 else p.stderr[:4096]
    except subprocess.TimeoutExpired:
        return 124, ''
    except FileNotFoundError:
        return 127, 'executable missing'
    except OSError:
        return 126, 'executable unavailable'


def check(credentials, iface, execute=run, runtime=Path('/run')):
    ssid, password = credentials['ssid'], credentials['password']
    if not isinstance(ssid, str) or not 1 <= len(ssid.encode()) <= 32:
        raise ValueError('Invalid SSID length')
    if not isinstance(password, str) or not 8 <= len(password) <= 63 or '\n' in password or '\r' in password:
        raise ValueError('Invalid WPA passphrase format')
    result = {'scope': 'ONE_NETWORK_RAM_ONLY', 'interface_found': True,
              'association_pass': False, 'dhcp_pass': False, 'https_pass': False,
              'password_logged': False, 'low_level_scan_or_reset': False}

    def command(label, args, seconds):
        rc, output = execute(args, seconds)
        result[label + '_rc'] = rc
        if rc:
            # Store only a fixed error category; raw diagnostics may name SSIDs.
            low=output.lower()
            result[label + '_error_class'] = (
                'executable_missing' if rc==127 else
                'executable_unavailable' if rc==126 else
                'transfer_timeout' if label=='https' and rc==28 else
                'certificate_verification_failed' if label=='https' and rc==60 else
                'device_unavailable' if 'unavailable' in low else
                'permission_denied' if 'not authorized' in low or 'permission denied' in low else
                'secrets_required' if 'secrets were required' in low else
                'timeout' if rc==124 else 'command_failed')
        # Print progress codes only. Never expose nmcli stdout/stderr or credentials.
        print('AUTO_WIFI_PHASE ' + json.dumps({'phase': label, 'returncode': rc}), flush=True)
        return rc, output

    rc, _ = command('supplicant_dbus', ['busctl','--system','--timeout=4','get-property',
            'fi.w1.wpa_supplicant1','/fi/w1/wpa_supplicant1','fi.w1.wpa_supplicant1','Interfaces'], 6)
    if rc:
        return result
    rc, state = command('nm_ready', ['nmcli', '--wait', '4', '-g', 'GENERAL.STATE', 'device', 'show', iface], 6)
    if rc:
        return result
    code=re.match(r'\s*(\d+)',state)
    result['nm_device_state_code']=int(code[1]) if code else None
    result['nm_device_ready']=code is not None and 30<=int(code[1])<=100
    if not result['nm_device_ready']:
        return result
    rc, _ = command('managed', ['nmcli', '--wait', '4', 'device', 'set', iface, 'managed', 'yes'], 6)
    if rc:
        return result
    rc, _ = command('rescan', ['nmcli', '--wait', '8', 'device', 'wifi', 'rescan', 'ifname', iface], 10)
    if rc:
        return result
    time.sleep(3)  # Request completion is asynchronous; give the single scan time.
    rc, output = command('ap_list', ['nmcli', '--wait', '4', '--escape', 'no', '-g', 'SSID',
                                    'device', 'wifi', 'list', 'ifname', iface, '--rescan', 'no'], 6)
    result['target_seen'] = rc == 0 and ssid in output.splitlines()
    if rc or not result['target_seen']:
        return result
    ident = str(uuid.uuid4())
    rc, _ = command('profile', ['nmcli', '--wait', '4', 'connection', 'add', 'type', 'wifi',
                               'ifname', iface, 'con-name', 'oneplus13-ram-acceptance',
                               'connection.uuid', ident, 'ssid', ssid,
                               'connection.autoconnect', 'no', 'wifi-sec.key-mgmt', 'wpa-psk'], 6)
    if rc:
        return result
    fd, name = tempfile.mkstemp(prefix='oneplus13-wifi-', dir=runtime)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write('802-11-wireless-security.psk:' + password + '\n')
        rc, _ = command('authentication', ['nmcli', '--wait', '15', 'connection', 'up', 'uuid', ident,
                                          'ifname', iface, 'passwd-file', name], 18)
    finally:
        Path(name).unlink(missing_ok=True)
    if rc:
        return result
    rc, active = command('active_profile', ['nmcli', '--wait', '4', '-g', 'GENERAL.CON-UUID',
                                          'device', 'show', iface], 6)
    result['association_pass'] = rc == 0 and active.strip() == ident
    if not result['association_pass']:
        return result
    # Activation can complete on IPv6 before DHCPv4 finishes. Observe the same
    # connection for at most 15 seconds; do not reconnect or invent a lease.
    deadline = time.monotonic() + 15
    for attempt in range(8):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        rc, addresses = command('ipv4_address', ['ip', '-j', '-4', 'address', 'show', 'dev', iface], min(3, remaining))
        remaining = deadline - time.monotonic()
        if rc or remaining <= 0:
            break
        rr, routes = command('ipv4_route', ['ip', '-j', '-4', 'route', 'show', 'dev', iface, 'default'], min(3, remaining))
        result['ipv4_observations'] = attempt + 1
        if rr:
            break
        try:
            has_ip = any(a.get('scope') == 'global' for dev in json.loads(addresses) for a in dev.get('addr_info', []))
            defaults = [x for x in json.loads(routes) if x.get('dst') == 'default' and x.get('gateway')]
        except (ValueError, TypeError, AttributeError):
            result['ipv4_observation_invalid'] = True
            break
        result['ipv4_global_address_present'] = has_ip
        result['ipv4_default_route_present'] = bool(defaults)
        result['dhcp_pass'] = has_ip and bool(defaults)
        if result['dhcp_pass']:
            break
        time.sleep(min(2, max(0, deadline - time.monotonic())))
    if not result['dhcp_pass']:
        return result
    # These are diagnostics, not prerequisites: curl resolves the hostname and
    # proves traffic on the selected WiFi interface even in a minimal rootfs.
    rc, _ = command('gateway', ['ping', '-I', iface, '-c', '2', '-W', '2', defaults[0]['gateway']], 6)
    result['gateway_probe_skipped'] = rc in (126, 127)
    rc, _ = command('dns', ['getent', 'ahostsv4', 'example.com'], 5)
    result['dns_probe_skipped'] = rc in (126, 127)
    rc, output = command('https', ['curl', '--ipv4', '--noproxy', '*', '--interface', iface, '--connect-timeout', '4',
                             '--max-time', '7', '--fail', '--silent', '--output', '/dev/null',
                             '--write-out', HTTPS_WRITE_OUT,
                             'https://example.com/'], 9)
    result['https_address_family'] = 'IPv4'
    result['https_metrics'] = https_metrics(output)
    result['https_pass'] = rc == 0
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--credentials', type=Path, required=True)
    args = parser.parse_args()
    if ' / overlay ' not in Path('/proc/mounts').read_text():
        raise SystemExit('Refusing WiFi credential staging outside RAM overlay')
    credentials = json.loads(args.credentials.read_text())
    args.credentials.unlink()  # Remove transport copy before invoking any subprocess.
    required=['nmcli','busctl','ip','curl']
    missing=[name for name in required if shutil.which(name) is None]
    interfaces = [p.name for p in Path('/sys/class/net').iterdir()
                  if (p/'phy80211').exists() or (p/'wireless').is_dir()]
    if missing:
        result={'missing_required_commands':missing,'automatic_acceptance_pass':False}
    elif len(interfaces) != 1:
        result = {'interface_found': False, 'interface_count': len(interfaces)}
    else:
        result = check(credentials, interfaces[0])
    result['automatic_acceptance_pass'] = all(result.get(k) for k in ['association_pass', 'dhcp_pass', 'https_pass'])
    print('AUTO_WIFI_RESULT ' + json.dumps(result, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
