#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
set -euo pipefail
repo=$(cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$repo"
src="$repo/out/oneplus13-linux"
kout="$repo/out/oneplus13-kbuild"
dest="$repo/out/oneplus13"
jobs=${ONEPLUS13_BUILD_JOBS:-$(nproc)}
[[ $jobs =~ ^[1-9][0-9]*$ ]] || { echo "Invalid build job count" >&2; exit 2; }
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
if [[ ${PHONE_WIFI_TRANSPORT_DRAFT:-0} == 1 ]]; then
  # Offline-only transport integration. This installs no RF policy/caller and
  # adds no firmware; hardware acceptance remains separately gated.
  python3 tools/oneplus13/wifi-draft/integrate-driver.py --kernel "$src" \
    > "$dest/wifi-driver-integration.json"
  git -C "$src" add --intent-to-add \
    drivers/net/wireless/ath/ath12k/phone-sar.c \
    drivers/net/wireless/ath/ath12k/phone-sar.h \
    drivers/net/wireless/ath/ath12k/sar-wire.c \
    drivers/net/wireless/ath/ath12k/sar-wire.h
fi
for patch in "$repo"/devices/oneplus13/kernel-patches/*.patch; do
  if git -C "$src" apply --reverse --check "$patch" 2>/dev/null; then
    continue # an identical rerun in this disposable build tree
  fi
  git -C "$src" apply --check "$patch"
  git -C "$src" apply "$patch"
done
python3 tools/oneplus13/check-wcn7860-scan.py --kernel-source "$src" \
  --output "$dest/wcn7860-scan-verification.json"
python3 tools/oneplus13/dsc.py \
  --panel-json devices/oneplus13/panel-aa569-120hz.json \
  --output "$dest/aa569-dsc.json" --c-output "$dest/aa569-dsc.h"
python3 tools/oneplus13/check-display.py --kernel-source "$src" \
  --output "$dest/display-conversion-verification.json" --sanitize
python3 tools/oneplus13/check-command-clock.py --kernel-source "$src" \
  --output "$dest/command-clock-verification.json" --sanitize
python3 tools/oneplus13/check-panel.py --kernel-source "$src" \
  --output "$dest/panel-component-verification.json" --sanitize
python3 tools/oneplus13/check-dsi-batch.py --kernel-source "$src" \
  --output "$dest/dsi-batch-verification.json" --sanitize
python3 tools/oneplus13/check-fixed-phy.py --kernel-source "$src" \
  --output "$dest/fixed-phy-verification.json" --sanitize
python3 tools/oneplus13/check-dpu.py --kernel-source "$src" \
  --output "$dest/dpu-buffer-verification.json" --sanitize
python3 tools/oneplus13/check-spr-profile.py \
  --output "$dest/spr-profile-verification.json" --sanitize
python3 tools/oneplus13/check-native-identity.py \
  --output "$dest/native-identity-verification.json" --sanitize
python3 tools/oneplus13/check-spr-runtime.py --kernel-source "$src" \
  --output "$dest/spr-runtime-verification.json" --sanitize
cp devices/oneplus13/sm8750-oneplus-dodge*.dts "$src/arch/arm64/boot/dts/qcom/"
cp -a devices/oneplus13/kernel/synaptics-dodge "$src/drivers/input/touchscreen/"
cp -a devices/oneplus13/kernel/panel-aa569 "$src/drivers/gpu/drm/panel/"
cp devices/oneplus13/kernel/spr-aa569/dpu_aa569_spr*.[ch] "$src/drivers/gpu/drm/msm/disp/dpu1/"
if ! grep -q DRM_PANEL_ONEPLUS_AA569_EXPERIMENTAL "$src/drivers/gpu/drm/panel/Kconfig"; then
  cat >> "$src/drivers/gpu/drm/panel/Kconfig" <<'KCONFIG'

config DRM_PANEL_ONEPLUS_AA569_EXPERIMENTAL
	tristate "Experimental OnePlus 13 AA569 panel component"
	depends on DRM_MIPI_DSI && OF && GPIOLIB && EXPERT
	help
	  Experimental fixed120Hz component for the isolated native-display DTB.
	  Requires the guarded SPR backend and the owner's private local profile.
KCONFIG
  printf '\nobj-$(CONFIG_DRM_PANEL_ONEPLUS_AA569_EXPERIMENTAL) += panel-aa569/\n' >> "$src/drivers/gpu/drm/panel/Makefile"
fi
if ! grep -q TOUCHSCREEN_DODGE_S3910 "$src/drivers/input/touchscreen/Kconfig"; then
  cat >> "$src/drivers/input/touchscreen/Kconfig" <<'KCONFIG'

config TOUCHSCREEN_DODGE_S3910
	tristate "Experimental OnePlus 13 Synaptics S3910 LBP"
	depends on SPI && OF && GPIOLIB && INPUT_TOUCHSCREEN
	depends on DRM_PANEL
	help
	  Isolated offline bring-up candidate, not hardware validated.
KCONFIG
  printf '\nobj-$(CONFIG_TOUCHSCREEN_DODGE_S3910) += synaptics-dodge/\n' >> "$src/drivers/input/touchscreen/Makefile"
fi
grep -q 'sm8750-oneplus-dodge.dtb' "$src/arch/arm64/boot/dts/qcom/Makefile" || \
  printf '\ndtb-$(CONFIG_ARCH_QCOM) += sm8750-oneplus-dodge.dtb\n' >> "$src/arch/arm64/boot/dts/qcom/Makefile"
grep -q 'sm8750-oneplus-dodge-touch.dtb' "$src/arch/arm64/boot/dts/qcom/Makefile" || \
  printf '\ndtb-$(CONFIG_ARCH_QCOM) += sm8750-oneplus-dodge-touch.dtb\n' >> "$src/arch/arm64/boot/dts/qcom/Makefile"
grep -q 'sm8750-oneplus-dodge-native.dtb' "$src/arch/arm64/boot/dts/qcom/Makefile" || \
  printf '\ndtb-$(CONFIG_ARCH_QCOM) += sm8750-oneplus-dodge-native.dtb\n' >> "$src/arch/arm64/boot/dts/qcom/Makefile"
grep -q 'sm8750-oneplus-dodge-wlan.dtb' "$src/arch/arm64/boot/dts/qcom/Makefile" || \
  printf '\ndtb-$(CONFIG_ARCH_QCOM) += sm8750-oneplus-dodge-wlan.dtb\n' >> "$src/arch/arm64/boot/dts/qcom/Makefile"
grep -q 'sm8750-oneplus-dodge-gpu.dtb' "$src/arch/arm64/boot/dts/qcom/Makefile" || \
  printf '\ndtb-$(CONFIG_ARCH_QCOM) += sm8750-oneplus-dodge-gpu.dtb\n' >> "$src/arch/arm64/boot/dts/qcom/Makefile"
git -C "$src" add --intent-to-add arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge*.dts \
  drivers/input/touchscreen/synaptics-dodge drivers/gpu/drm/panel/panel-aa569 \
  drivers/gpu/drm/msm/disp/dpu1/dpu_aa569_spr*.[ch]
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
cp "$kout/.config" "$dest/kernel.config"
config_id=$(sha256sum "$kout/.config" | cut -c1-12)
phone_id=$(sha256sum "$dest/phone-kernel.patch" | cut -c1-12)
args+=("LOCALVERSION=-g${pin[1]:0:12}-c$config_id-p$phone_id")
# DTB first: reject unresolved phandles before the expensive kernel build.
make "${args[@]}" -j"$jobs" qcom/sm8750-erhai.dtb 2>&1 | tee "$kout/reference-dtb.log"
make "${args[@]}" -j"$jobs" qcom/sm8750-oneplus-dodge.dtb 2>&1 | tee "$kout/dtb.log"
make "${args[@]}" -j"$jobs" qcom/sm8750-oneplus-dodge-touch.dtb 2>&1 | tee "$kout/touch-dtb.log"
make "${args[@]}" -j"$jobs" qcom/sm8750-oneplus-dodge-native.dtb 2>&1 | tee "$kout/native-dtb.log"
python3 tools/oneplus13/check-command-budget.py --kernel-source "$src" \
  --native-dtb "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge-native.dtb" \
  --output "$dest/command-budget-verification.json" --sanitize
python3 tools/oneplus13/check-native-dtb.py \
  --dtb "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge-native.dtb" \
  --output "$dest/native-dtb-verification.json" --negative-controls
make "${args[@]}" -j"$jobs" qcom/sm8750-oneplus-dodge-wlan.dtb 2>&1 | tee "$kout/wlan-dtb.log"
python3 tools/oneplus13/check-wlan-dtb.py \
  --dtb "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge-wlan.dtb" \
  --config "$kout/.config" --output "$dest/wlan-dtb-verification.json"
make "${args[@]}" -j"$jobs" qcom/sm8750-oneplus-dodge-gpu.dtb 2>&1 | tee "$kout/gpu-dtb.log"
python3 tools/oneplus13/check-gpu-dtb.py \
  --dtb "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge-gpu.dtb" \
  --config "$kout/.config" --kernel-source "$src" --output "$dest/gpu-dtb-verification.json"
# Fail API compilation of the isolated components before the full kernel build.
make "${args[@]}" -j"$jobs" drivers/gpu/drm/panel/panel-aa569/ \
  drivers/input/touchscreen/synaptics-dodge/ \
  drivers/gpu/drm/msm/disp/dpu1/dpu_aa569_spr.o \
  drivers/gpu/drm/msm/disp/dpu1/dpu_aa569_spr_runtime.o 2>&1 | tee "$kout/component-api.log"
time make "${args[@]}" -j"$jobs" Image Image.gz modules 2>&1 | tee "$kout/build.log"
make "${args[@]}" -j"$jobs" modules_install INSTALL_MOD_PATH="$dest/modules" INSTALL_MOD_STRIP=1 \
  2>&1 | tee "$kout/modules.log"
find "$dest/modules" -type l -name build -delete
find "$dest/modules" -type l -name source -delete
tar --sort=name --mtime="@$(( $(git -C "$repo" show -s --format=%ct HEAD) ))" \
  --owner=0 --group=0 --numeric-owner -C "$dest/modules" -czf "$dest/modules.tar.gz" .
rm -rf -- "$dest/modules"
cp "$kout/arch/arm64/boot/Image" "$kout/arch/arm64/boot/Image.gz" "$dest/"
cp "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dtb" "$dest/"
cp "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge-touch.dtb" "$dest/"
cp "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge-native.dtb" "$dest/"
cp "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge-wlan.dtb" "$dest/"
cp "$kout/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge-gpu.dtb" "$dest/"
cp "$kout/.config" "$dest/kernel.config"
cp "$kout/include/config/kernel.release" "$dest/kernel.release"
cp "$kout/System.map" "$dest/"
python3 tools/oneplus13/package.py --kernel-out "$kout" --output "$dest"
python3 tools/oneplus13/verify.py --artifacts "$dest"
ccache --show-stats
