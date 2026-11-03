#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Native ARM64, disposable CI chroot. No phone or host sound/display access.
set -euo pipefail
[[ $(id -u) == 0 && $(uname -m) == aarch64 ]] || exit 1
cd "$(dirname "$0")/../.."
repo=$PWD
build="$repo/out/resources-build"
root="$build/root"
out="$repo/out/oneplus13-resources"
[[ ! -e $build && ! -e $out ]] || { echo 'Fresh Resources build required' >&2; exit 1; }
mkdir -p "$root" "$out" "$repo/cache"
python3 - "$repo" <<'PY'
import hashlib,json,pathlib,subprocess,sys
repo=pathlib.Path(sys.argv[1]);pin=json.loads((repo/'devices/oneplus13/ubuntu.json').read_text())
inputs=[dict(file='ubuntu-base.tar.gz',url=pin['base_url'],sha256=pin['base_sha256']),*json.loads((repo/'packaging/oneplus13-resources/ubuntu/source.json').read_text())['files']]
for item in inputs:
 p=repo/'cache'/item['file']
 if not p.is_file() or hashlib.file_digest(p.open('rb'),'sha256').hexdigest()!=item['sha256']:
  subprocess.run(['curl','--fail','--location','--retry','4','--connect-timeout','15','--max-time','300','-o',str(p),item['url']],check=True)
 assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==item['sha256']
PY
tar -xzf cache/ubuntu-base.tar.gz -C "$root"
install -Dm0644 /etc/ssl/certs/ca-certificates.crt "$root/etc/ssl/certs/ca-certificates.crt"
printf 'nameserver 1.1.1.1\n' > "$root/etc/resolv.conf"
cat > "$root/etc/apt/sources.list.d/ubuntu.sources" <<'EOF'
Types: deb deb-src
URIs: https://snapshot.ubuntu.com/ubuntu/20261024T000000Z/
Suites: resolute resolute-updates resolute-security
Components: main universe restricted multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
EOF
rm -f "$root/etc/apt/sources.list"
printf 'Acquire::https::CaInfo "/etc/ssl/certs/ca-certificates.crt";\nAcquire::Retries "4";\nAcquire::https::Timeout "30";\n' > "$root/etc/apt/apt.conf.d/80bootstrap"
printf '#!/bin/sh\nexit 101\n' > "$root/usr/sbin/policy-rc.d"
chmod 755 "$root/usr/sbin/policy-rc.d"
cleanup() { for dir in proc dev; do mountpoint -q "$root/$dir" && umount -R "$root/$dir" || true; done; }
trap cleanup EXIT
mount --rbind /dev "$root/dev"; mount --make-rslave "$root/dev"
mount -t proc proc "$root/proc"
export DEBIAN_FRONTEND=noninteractive
chroot "$root" apt-get -o APT::Update::Error-Mode=any update
chroot "$root" apt-get install -y --no-install-recommends ca-certificates dpkg-dev quilt build-essential
mkdir -p "$root/build"
cp cache/resources_1.10.2* "$root/build/"
chroot "$root" sh -c 'cd /build && dpkg-source -x resources_1.10.2-0ubuntu3.1.dsc resources'
mkdir "$build/telemetry-patches"
cp packaging/oneplus13-resources/upstream/patches/*.patch "$build/telemetry-patches/"
(cd "$build/telemetry-patches" && patch --batch --fuzz=0 -p1 < "$repo/packaging/oneplus13-resources/ubuntu/backport.patch")
cp "$build/telemetry-patches/"*.patch "$root/build/resources/debian/patches/"
for file in "$build/telemetry-patches/"*.patch; do basename "$file" >> "$root/build/resources/debian/patches/series"; done
python3 - "$root/build/resources/debian/changelog" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]);p.write_text('''resources (1.10.2-0ubuntu3.1+op13.1) resolute; urgency=medium

  * Backport the GPL-3.0-or-later MSM/Adreno telemetry and thermal patches
    from yzddmr6/xiaomipad-8pro-mainline, retaining Ubuntu's source/vendor set.
  * OnePlus13 offline diagnostic candidate; no hardware acceptance claim.

 -- Codex <codex@openai.com>  Tue, 03 Nov 2026 14:00:00 +0800

'''+p.read_text())
PY
chroot "$root" sh -c 'cd /build/resources && QUILT_PATCHES=debian/patches quilt push -a'
chroot "$root" apt-get build-dep -y --no-install-recommends /build/resources
# Debian's native Meson/Cargo build and test rules, with vendored crate inputs.
chroot "$root" sh -c 'cd /build/resources && dpkg-buildpackage -b -us -uc'
# Ship corresponding patched source as well as the ARM64 binaries.
chroot "$root" sh -c 'cd /build/resources && dpkg-buildpackage -S -us -uc -d'
find "$root/build" -maxdepth 1 -type f \( -name '*.deb' -o -name '*.dsc' -o -name '*.tar.*' -o -name '*.buildinfo' -o -name '*.changes' \) -exec cp {} "$out/" \;
python3 - "$out" <<'PY'
import hashlib,json,pathlib,subprocess,sys
p=pathlib.Path(sys.argv[1]);debs=list(p.glob('resources_*_arm64.deb'));assert len(debs)==1
assert subprocess.check_output(['dpkg-deb','-f',str(debs[0]),'Version'],text=True).strip()=='1.10.2-0ubuntu3.1+op13.1'
sha=lambda f:hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
result=dict(scope='RESOURCES_ARM64_SOURCE_BUILD_NOT_PHONE_TESTED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),version='1.10.2-0ubuntu3.1+op13.1',hardware_tested=False,corresponding_source_included=True,files={f.name:sha(f) for f in p.iterdir() if f.is_file()})
(p/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(p/'SHA256SUMS').write_text(''.join(sha(f)+'  '+f.name+'\n' for f in sorted(p.iterdir()) if f.is_file()))
PY
