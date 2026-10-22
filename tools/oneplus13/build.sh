#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repo"
src="$repo/out/oneplus13-linux"
kout="$repo/out/oneplus13-kbuild"
dest="$repo/out/oneplus13"
mkdir -p "$kout" "$dest"
exec 9>"$kout/.build.lock"
flock -n 9 || { echo 'Build already running' >&2; exit 1; }
python3 tools/oneplus13/package.py --output "$dest" --initramfs-only
readarray -t pin < <(python3 - <<'PY'
import json
s=json.load(open('devices/oneplus13/source.json'))['kernel']
print(s['repository']); print(s['commit'])
PY
)
if [[ ! -d $src/.git ]]; then
  git init "$src"
  git -C "$src" remote add origin "${pin[0]}"
fi
git -C "$src" fetch --depth 1 origin "${pin[1]}"
git -C "$src" checkout --detach FETCH_HEAD
[[ $(git -C "$src" rev-parse HEAD) == "${pin[1]}" ]]
cp devices/oneplus13/sm8750-oneplus-dodge.dts "$src/arch/arm64/boot/dts/qcom/"
grep -q 'sm8750-oneplus-dodge.dtb' "$src/arch/arm64/boot/dts/qcom/Makefile" || \
  printf '\ndtb-$(CONFIG_ARCH_QCOM) += sm8750-oneplus-dodge.dtb\n' >> "$src/arch/arm64/boot/dts/qcom/Makefile"
git -C "$src" add --intent-to-add arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dts
git -C "$src" diff --binary HEAD > "$dest/phone-kernel.patch"
export ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu-
export KBUILD_BUILD_USER=codex KBUILD_BUILD_HOST=github-actions KBUILD_BUILD_VERSION=1
export KBUILD_BUILD_TIMESTAMP
KBUILD_BUILD_TIMESTAMP=$(git -C "$repo" show -s --format=%cI HEAD)
export KCFLAGS="-ffile-prefix-map=$src=/linux -ffile-prefix-map=$kout=/kbuild"
args=(-C "$src" O="$kout" 'CC=ccache aarch64-linux-gnu-gcc')
make "${args[@]}" defconfig > "$kout/configure.log" 2>&1
"$src/scripts/kconfig/merge_config.sh" -m -O "$kout" "$kout/.config" \
  "$repo/devices/oneplus13/oneplus13.config" >> "$kout/configure.log" 2>&1
make "${args[@]}" olddefconfig >> "$kout/configure.log" 2>&1
python3 tools/oneplus13/verify.py --config "$kout/.config"
config_id=$(sha256sum "$kout/.config" | cut -c1-12)
args+=("LOCALVERSION=-g${pin[1]:0:12}-c$config_id")
# DTB first: reject unresolved phandles before the expensive kernel build.
make "${args[@]}" -j"$(nproc)" qcom/sm8750-erhai.dtb 2>&1 | tee "$kout/reference-dtb.log"
make "${args[@]}" -j"$(nproc)" qcom/sm8750-oneplus-dodge.dtb 2>&1 | tee "$kout/dtb.log"
time make "${args[@]}" -j"$(nproc)" Image Image.gz modules 2>&1 | tee "$kout/build.log"
make "${args[@]}" -j"$(nproc)" modules_install INSTALL_MOD_PATH="$dest/modules" INSTALL_MOD_STRIP=1 \
  2>&1 | tee "$kout/modules.log"
find "$dest/modules" -type l -name build -delete
find "$dest/modules" -type l -name source -delete
tar --sort=name --mtime="@$(( $(git -C "$repo" show -s --format=%ct HEAD) ))" \
  --owner=0 --group=0 --numeric-owner -C "$dest/modules" -czf "$dest/modules.tar.gz" .
rm -rf -- "$dest/modules"
cp "$kout/arch/arm64/boot/Image" "$kout/arch/arm64/boot/Image.gz" "$dest/"
cp "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dtb" "$dest/"
cp "$kout/.config" "$dest/kernel.config"
cp "$kout/include/config/kernel.release" "$dest/kernel.release"
cp "$kout/System.map" "$dest/"
python3 tools/oneplus13/package.py --kernel-out "$kout" --output "$dest"
python3 tools/oneplus13/verify.py --artifacts "$dest"
ccache --show-stats
