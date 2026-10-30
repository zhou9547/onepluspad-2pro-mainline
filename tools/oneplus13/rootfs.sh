#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
[[ $(id -u) == 0 ]] || { echo 'Run in the dedicated CI VM with sudo' >&2; exit 1; }
[[ $(uname -m) == aarch64 ]] || { echo 'Native ARM64 build host required' >&2; exit 1; }
repo=$(cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repo"
root="$repo/out/oneplus13-rootfs-stage"
dest="$repo/out/oneplus13-rootfs-artifacts"
mkdir -p "$root" "$dest" "$repo/cache"
[[ ! -e $root/etc/os-release ]] || { echo 'Use a fresh staging directory' >&2; exit 1; }
readarray -t pin < <(python3 - <<'PY'
import json
s=json.load(open('devices/oneplus13/ubuntu.json'))
print(s['base_url']); print(s['base_sha256']); print(s['apt_uri'])
print(' '.join(s['packages']))
PY
)
base="$repo/cache/oneplus13-ubuntu-base.tar.gz"
curl --fail --location --retry 5 --retry-delay 10 --retry-max-time 180 --output "$base" "${pin[0]}"
printf '%s  %s\n' "${pin[1]}" "$base" | sha256sum --check -
tar --extract --gzip --numeric-owner --preserve-permissions --file "$base" --directory "$root"
# Ubuntu Base intentionally omits ca-certificates. Bootstrap HTTPS using the
# runner's standard trust bundle; apt replaces it when installing the target
# ca-certificates package. Never disable TLS verification or archive signatures.
install -D -m 0644 /etc/ssl/certs/ca-certificates.crt "$root/etc/ssl/certs/ca-certificates.crt"
# Diagnose transport before entering the chroot, then name the trust file
# explicitly: Ubuntu Base's TLS backend has no ca-certificates configuration yet.
curl --fail --silent --show-error --retry 5 --retry-delay 10 --retry-max-time 180 --output /dev/null "${pin[2]}dists/resolute/InRelease"
test -r "$root/etc/ssl/certs/ca-certificates.crt"
cat > "$root/etc/apt/apt.conf.d/80bootstrap-ca" <<'EOF'
Acquire::https::CaInfo "/etc/ssl/certs/ca-certificates.crt";
Acquire::Retries "5";
Acquire::Languages "none";
Acquire::https::Timeout "30";
EOF
# The archive's symlink layout is preserved; never copy the host machine identity.
printf 'nameserver 1.1.1.1\n' > "$root/etc/resolv.conf"
cat > "$root/etc/apt/sources.list.d/ubuntu.sources" <<EOF
Types: deb
URIs: ${pin[2]}
Suites: resolute resolute-updates resolute-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
EOF
rm -f "$root/etc/apt/sources.list"
cat > "$root/usr/sbin/policy-rc.d" <<'EOF'
#!/bin/sh
exit 101
EOF
chmod 755 "$root/usr/sbin/policy-rc.d"
cleanup() {
  for d in run sys proc dev; do
    if mountpoint -q "$root/$d"; then umount -R "$root/$d"; fi
  done
}
trap cleanup EXIT
for d in dev proc sys run; do
  mount --rbind "/$d" "$root/$d"
  mount --make-rslave "$root/$d"
done
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive apt-get -o APT::Update::Error-Mode=any update
# Read the exact package set from the locked JSON. Package versions are fixed by
# the signed Ubuntu snapshot and recorded in the delivered manifest.
read -r -a packages <<< "${pin[3]}"
# Resolve using the validated snapshot indexes, then fetch eight packages at a
# time. Cached bytes are accepted only against this plan's size and SHA256.
chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive \
  apt-get -o Acquire::ForceHash=SHA256 --print-uris --download-only \
  install -y --no-install-recommends "${packages[@]}" > "$dest/apt-package-plan.txt"
python3 tools/oneplus13/prefetch-rootfs-debs.py \
  --plan "$dest/apt-package-plan.txt" --apt-uri "${pin[2]}" \
  --cache "$repo/cache/oneplus13-rootfs-debs" \
  --archives "$root/var/cache/apt/archives" --report "$dest/deb-prefetch.json"
time chroot "$root" /usr/bin/env DEBIAN_FRONTEND=noninteractive \
  apt-get install --no-download -y --no-install-recommends "${packages[@]}"
chroot "$root" locale-gen en_US.UTF-8 zh_CN.UTF-8
test -f "$root/usr/share/zoneinfo/Asia/Shanghai"
ln -sfn /usr/share/zoneinfo/Asia/Shanghai "$root/etc/localtime"
printf 'Asia/Shanghai\n' > "$root/etc/timezone"
cat > "$root/etc/default/locale" <<'EOF'
LANG=zh_CN.UTF-8
LANGUAGE=zh_CN:zh
LC_MESSAGES=zh_CN.UTF-8
EOF
cat > "$root/etc/profile.d/90-oneplus13-locale.sh" <<'EOF'
export LANG=zh_CN.UTF-8
export LANGUAGE=zh_CN:zh
export LC_MESSAGES=zh_CN.UTF-8
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
EOF
cat > "$root/etc/environment" <<'EOF'
LANG=zh_CN.UTF-8
LANGUAGE=zh_CN:zh
LC_MESSAGES=zh_CN.UTF-8
GTK_IM_MODULE=ibus
QT_IM_MODULE=ibus
XMODIFIERS=@im=ibus
GSK_RENDERER=cairo
EOF
echo oneplus13-linux > "$root/etc/hostname"
printf '127.0.0.1 localhost\n127.0.1.1 oneplus13-linux\n::1 localhost ip6-localhost\n' > "$root/etc/hosts"
mkdir -p "$root/etc/systemd/system" "$root/etc/systemd/logind.conf.d"
ln -sfn /usr/lib/systemd/system/graphical.target "$root/etc/systemd/system/default.target"
cat > "$root/etc/systemd/logind.conf.d/50-oneplus13-bringup.conf" <<'EOF'
[Login]
HandlePowerKey=ignore
IdleAction=ignore
EOF
# Suspend/resume is not established on the phone; prevent an unattended desktop
# from entering an untested sleep path. This is an explicit staging policy.
for unit in sleep.target suspend.target hibernate.target hybrid-sleep.target; do
  ln -sfn /dev/null "$root/etc/systemd/system/$unit"
done
chroot "$root" passwd -l root
# Supply the real engine and both firewall frontends, but do not create a
# docker0 bridge or modify the phone's forwarding policy during qualification.
# The owner can start docker.service explicitly in the RAM desktop.
chroot "$root" systemctl disable docker.service docker.socket containerd.service
install -D -m 0644 devices/oneplus13/docker/daemon.json "$root/etc/docker/daemon.json"
mkdir -p "$root/etc/ssh/sshd_config.d"
cat > "$root/etc/ssh/sshd_config.d/60-oneplus13.conf" <<'EOF'
PasswordAuthentication yes
KbdInteractiveAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
AllowUsers a
EOF
cat > "$root/usr/lib/systemd/system/oneplus13-ssh-host-keys.service" <<'EOF'
[Unit]
Description=Generate volatile OnePlus 13 SSH host keys
RequiresMountsFor=/etc/ssh
Before=ssh.service

[Service]
Type=oneshot
ExecStart=/usr/bin/ssh-keygen -A
ExecStartPost=/usr/sbin/sshd -t
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
mkdir -p "$root/etc/systemd/system/multi-user.target.wants"
ln -sfn /usr/lib/systemd/system/oneplus13-ssh-host-keys.service \
  "$root/etc/systemd/system/multi-user.target.wants/oneplus13-ssh-host-keys.service"
ln -sfn /usr/lib/systemd/system/ssh.service \
  "$root/etc/systemd/system/multi-user.target.wants/ssh.service"
ln -sfn /usr/lib/systemd/system/rmtfs.service \
  "$root/etc/systemd/system/multi-user.target.wants/rmtfs.service"
ln -sfn /usr/lib/systemd/system/tqftpserv.service \
  "$root/etc/systemd/system/multi-user.target.wants/tqftpserv.service"

install -Dm0644 devices/oneplus13/rmtfs-uio.rules "$root/etc/udev/rules.d/90-oneplus13-rmtfs-uio.rules"
rm -f "$root"/etc/ssh/ssh_host_*
desktop_args=("$root")
if [[ -n ${ONEPLUS13_KERNEL_ARTIFACT:-} ]]; then
  desktop_args+=(--kernel "$ONEPLUS13_KERNEL_ARTIFACT")
fi
if [[ -n ${ONEPLUS13_STOCK_FIRMWARE:-} ]]; then
  desktop_args+=(--firmware "$ONEPLUS13_STOCK_FIRMWARE")
fi
python3 tools/oneplus13/install-desktop.py "${desktop_args[@]}"
chroot "$root" /usr/bin/systemd-analyze verify \
  oneplus13-ram-guard.service oneplus13-ram-deadline.timer \
  oneplus13-ram-evidence.service oneplus13-ram-usb.service \
  oneplus13-ram-dhcp.service oneplus13-ram-http.service \
  oneplus13-ram-shell.service oneplus13-ram-serial.service \
  ssh.service oneplus13-ssh-host-keys.service
udevadm verify "$root/usr/lib/udev/rules.d/10-oneplus13-ram-storage.rules"
chroot "$root" dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' > "$dest/packages.tsv"
chroot "$root" /usr/bin/gnome-shell --version > "$dest/gnome-version.txt"
chroot "$root" /usr/bin/env bash -n /etc/profile
chroot "$root" dpkg-query -W systemd-resolved > /dev/null
chroot "$root" locale -a | grep -qx 'zh_CN.utf8'
test -x "$root/usr/sbin/sshd"
test -x "$root/usr/bin/docker"
test -x "$root/usr/bin/dockerd"
test -x "$root/usr/sbin/iptables-nft"
test -x "$root/usr/sbin/iptables-legacy"
grep -qx 'PermitRootLogin no' "$root/etc/ssh/sshd_config.d/60-oneplus13.conf"
test ! -e "$root/etc/ssh/ssh_host_rsa_key"
test -L "$root/etc/systemd/system/multi-user.target.wants/ssh.service"
chroot "$root" apt-get clean
rm -f "$root/etc/apt/apt.conf.d/80bootstrap-ca"
rm -f "$root/usr/sbin/policy-rc.d"
cleanup
trap - EXIT
# Remove transient and machine-specific state only inside this fresh staging tree.
find "$root/var/lib/apt/lists" -type f -delete
find "$root/var/log" -type f -exec truncate -s 0 {} +
truncate -s 0 "$root/etc/machine-id"
rm -f "$root/var/lib/dbus/machine-id"
rm -f "$root/var/lib/systemd/random-seed"
ln -s /etc/machine-id "$root/var/lib/dbus/machine-id"
rm -f "$root/etc/resolv.conf"
ln -s /run/systemd/resolve/stub-resolv.conf "$root/etc/resolv.conf"
epoch=$(git show -s --format=%ct HEAD)
time mksquashfs "$root" "$dest/rootfs.squashfs" -noappend -comp zstd \
  -processors "$(nproc)" -mkfs-time "$epoch" -all-time "$epoch" -no-progress
unsquashfs -s "$dest/rootfs.squashfs" > "$dest/squashfs-info.txt"
unsquashfs -cat "$dest/rootfs.squashfs" etc/os-release > "$dest/os-release"
cp devices/oneplus13/ubuntu.json "$dest/ubuntu-source.json"
cp docs/oneplus13/README.md "$dest/README.md"
test -z "$(unsquashfs -cat "$dest/rootfs.squashfs" etc/machine-id)"
unsquashfs -cat "$dest/rootfs.squashfs" etc/shadow | \
  awk -F: '$1 == "root" { if ($2 !~ /^[!*]/) exit 1; found=1 } END { if (!found) exit 1 }'
python3 - "$dest" <<'PY'
import hashlib,json,pathlib,subprocess,sys
out=pathlib.Path(sys.argv[1])
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
result={'status':'OFFLINE_ROOTFS_BUILD_NOT_DEVICE_TESTED','hardware_tested':False,
 'integration_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'user_account':'No default password or autologin; create user before deployment',
 'kernel_modules':'Delivered separately with the matching kernel artifact',
 'files':{p.name:{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}}
(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file() and p.name!='SHA256SUMS'))
PY
