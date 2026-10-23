# Work log

## 2026-10-22

The user requested offline adaptation and successful Actions artifacts before
their hardware tests. The supplied link resolves to zhou9547's Pad integration
fork. Its base is 88fd48f85dee54c482a98e55319b11d1739e8852.

The Pad kernel is pinned at 7a81d184e3098624d4342d8f4eff5e23674bcc9f.
index986's OnePlus-13-WIP board at 1f2047e8663eda76c8b172fd3e040e3b3fa17950
provides phone-specific regulator, USB, storage and reserved memory clues.
The newer skb8 fork is research only: its README marks touchscreen support
despite stating that the driver is missing, and its DTS has duplicate properties.
It is not used as a hardware validation source.

Plan: build the pinned platform kernel with a separate phone DTB/config, a
read-only RAM diagnostics initramfs and a non-flashing boot image; run automated
artifact and QEMU userspace checks. Do not inherit the Pad partition/AVB values.

Added a separate native ARM64 Ubuntu 26.04.1 GNOME staging build. The official
base SHA256 was checked against Canonical's SHA256SUMS and package resolution
uses the 20261020T000000Z signed snapshot. No phone firmware, default password,
partition writer or automatic installer is included.

The first rootfs build failed before package installation because Ubuntu Base
does not include the CA bundle needed by HTTPS apt. The fix seeds the standard
host bundle until the signed target ca-certificates package installs it. TLS
and archive signatures remain enabled; apt update now fails on any index error.

Official OnePlus vendor sources were locally inspected at
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3. The dodge touch overlay confirms an
S3910 variant with SPI at 19 MHz, IRQ162/reset161, PM8550VS_J GPIO3 and L4B.
Multiple display/touch variants exist, so matching the user's actual panel is
still required. No guessed active driver node is added to the diagnostic DTB.

The TLS failure repeated with a copied bundle. Local HTTPS retrieval of the same
snapshot succeeded, narrowing this to Ubuntu Base's unconfigured trust lookup.
The next build diagnoses host HTTPS separately and explicitly configures apt's
CA file until target ca-certificates is installed; no third blind TLS bypass.
System QEMU installation is deferred until after compilation, and user-mode
QEMU uses the smaller dynamic host package instead of every static emulator.

Ubuntu GNOME staging build 39807949262 succeeded and produced a 419261065-byte
Actions artifact. The x86 runner remained in slow cross-toolchain downloads
even after changing the mirror, while the native ARM64 rootfs runner fetched
its dependencies quickly. Kernel CI therefore moves to the proven native
ARM64 runner and uses its native triplet-named GCC, avoiding that download.

Review found that --no-install-recommends omitted systemd-resolved while the
image's resolv.conf targets its stub. It is now an explicit package requirement
and asserted after installation. Root credential lock and empty machine-id are
also checked from the actual completed SquashFS, not just the staging tree.
Phone DTS static label inspection found a missing VPH fixed supply; the exact
provider from the attributed phone reference was restored before the next build.

First full native configuration passed all required built-in dependency checks.
The DT compiler rejected missing board-supplied bi_tcxo divide-by-two clocks,
alongside the already diagnosed VPH supply. The complete DTS + included DTSI
reference graph was inspected; both fixed-factor providers were restored from
the same phone source. No force-output flag or disabled compiler check is used.

## 2026-10-23

Native rootfs build 39809729390 succeeded after explicit DNS dependency checks.
Independent verification run 39812509439 downloaded that artifact on a fresh
runner and verified every checksum, all 782 package architectures, actual ARM64
GNOME/GDM/NetworkManager binaries, locked root and empty machine-id in SquashFS.
The image is GNOME Shell 50.1, 419479552 bytes, SHA256
97611cd24f0bc73c67a7393b9def55cbea3e952d26ca1ecfeb99b1d0b6e5ecef.
This does not establish phone hardware support.

Local artifact storage downloads were measured at only a few tens of KiB/s.
Bulk downloads were stopped; actual artifact re-download and verification uses
the fresh CI runner instead. Small verification reports will accompany delivery.
The BusyBox matching Ubuntu source archives are locked from its official .dsc
checksums and included with the diagnostic image, together with Linux source
identity and the generated phone patch.

Configuration review found that the initial fragment conversion dropped Kconfig
negative assignments (`# CONFIG_... is not set`) as if they were prose comments.
That unintentionally retained other vendors' default ARM64 platforms and
expanded the cold build. Restore the original platform exclusions, assert the
absence of unrelated platform families in the final .config, and add a failing
test for accidental ARCH_MEDIATEK enablement. Stop the superseded oversized
build; this is a recipe correction, not a hardware workaround.

Build 39813227953 compiled Image, phone/reference DTBs and the complete configured
module set successfully (C build: 22m29.933s). Packaging then correctly rejected a
duplicate bin/busybox entry: this pinned Ubuntu binary includes `busybox` in its
applet list. Preserve its real file and skip only that self-link. The exact
binary/appet/archive preflight now runs before source compilation. CI now saves
compiler cache immediately after the build attempt, including packaging failures.

Read-only collector review removed an assumption that dtbo is always unslotted.
It now discovers current-slot dtbo/vbmeta first, records the partition mapping,
and never substitutes an inactive boot slot. Empty/whitespace serials are
rejected. Eight host-side tests pass, including slotted/unslotted metadata and
inactive-slot rejection. This collection tool has not been run on a phone.

The pinned real AOSP mkbootimg also passed an independent local Android v2
section roundtrip test; the module archive prefix was checked against the pinned
kernel's actual MODLIB definition. No hardware result is inferred from these checks.

Build 39817564813 passed full kernel/module compilation, Android v2 section
checks, initramfs binary identity and module ABI checks. QEMU then failed before
starting the VM: the minimal qemu-system-arm install lacks efi-virtio.rom for
its default virtual NIC. The userspace smoke test does not exercise networking,
so explicitly omit the virtual NIC. This changes only the emulator invocation;
it does not change phone drivers or weaken the image checks. Compiler cache was
saved successfully before this environment failure.

Final candidate 44315dbe991d28d476bc1a9fca0da3ff2403b280 passed complete build
39821954442, including eight host checks, pinned input/source checks, reference
and phone DTBs, full modules, Android v2/CPIO/ELF/hash validation and QEMU.
Artifact 12444478734 is 60972932 bytes; its archive SHA256 is
1dafb99bb38b1ffc341edf3d5395afa67cc8f8971b2e11d78af8b069e5d8b2b3.

Independent run 39823094330 downloaded that actual artifact on a fresh runner,
repeated every artifact check and QEMU test, and passed. Its QEMU log reaches
ONEPLUS13_QEMU_INIT_OK then `reboot: Power down`, with no kernel panic.
Kernel release: 7.2.0-oneplus13-g7a81d184e309-cd25741ea7aea.
RAM boot image SHA256: 31a042d62726e825946e5cc595de73f872de3f67d8b6db81ff14786c79073f06.

Small independent reports were downloaded, their GitHub ZIP digests and CRCs
verified locally, and the actual startup/shutdown log inspected. The sole next
step and hardware evidence blockers are in STATUS.md. No phone was operated.

## 2026-10-23 — owner-authorized read-only calibration

The owner supplied a network ADB target with existing root and explicitly
prohibited every modification. An independent agent audited the collector before
device access; it never accessed the phone. The main agent read Android identity,
runtime FDT, current-slot boot/init_boot/vendor_boot/dtbo/vbmeta, ABL and the
relevant input/display evidence, saving originals privately on the host. FDT and
all five startup partition images match separate device-side SHA-256 reads.
No device file, setting, bootloader state or partition was changed. No reboot,
input injection, test kernel, mount or peripheral control command was issued.

Established actual PJZ110/24 GiB, current A slot, Android16 build
PJZ110_16.0.10.501(CN01), AA569 production and active S3910 HBP. The stock chain
uses Android v4 and capacities96/8/96 MiB. Base DTB2 and DTBO5 reproduce every
selected panel/touch property with Android libufdt. Root selection metadata is
verified separately against the selected overlay. The disabled overlay sink
accepts all six overlays without changing operational mainline nodes. Actual
15-bank RAM and all stock protected intervals pass the offline exclusion checks.

S3910 candidate reuses attributed TouchCom protocol code, negotiates fixed LBP
reports in RAM, checks descriptors/frames and uses asynchronous panel-following
work with explicit IRQ/power cleanup. Actions39888606647 exposed removed strncpy
in the imported compatibility layer; replaced it with bounded copy/padding.
Actions39889964952 then passed. The stock electrical audit corrected IRQ/reset
drive to8 mA, MOSI/CS to4 mA, disabled the invented IRQ pull-up and restored32 ms
key debounce. Actions39892106624 and39892351557 both passed after these changes.

Final compiled kernel input is d337d2f4bea9fae5e4ed0d87f8d97c2eff9c707b.
Actions39892351557 includes14 host tests, C ASan/UBSan vectors, module/DTB checks
and exact-image QEMU. Full artifact12474888299 was actually downloaded on the
host, ZIP digest b2b8691bd370704f16fc9844b67ea428014ef79e143d9e05520a006c97072237;
CRC, all20 manifest files, ARM64 module/vermagic and compiled electrical values
passed. S3910 module SHA256 is beda199198b6701b9fa54b3dcc55805d66f1babf7568f433cf90342310fdbafb.
Source changes following that build are host-only collector/packager checks and
documentation; they do not establish any additional hardware support.

The public AA569 on/off commands match runtime exactly (150 on-packets). The
SPR2/native422 path needs real implementation. Initial configuration-directory
searches missed the panel SPR XML; a bounded wider search found it in/vendor/etc.
It and the relevant Android libraries stay private. Offline symbol/disassembly
inspection identifies parameter conversion routines, but no native display
driver or working screen is claimed. Missing debugfs was not mounted/enabled.

Host packing produces an unsigned v4 diagnostic triplet and a single-image RAM
candidate with section readback checks. These are not installed GNOME images.
Physical boot, USB, touch and recovery tests are outside the current read-only
authorization. STATUS.md records the sole next hardware gate and device state.

## 2026-10-23 — SPR semantic translation and complete DSC PPS

Continued offline work without issuing further phone commands. Implemented a
strict private-XML SPR converter and relative register plan. It matches a bounded
host ARM64 emulation of the exact stock library's defaults/base/V2 conversion,
with semantic setter offsets independently inspected. A second host harness
compiled five unmodified public vendor C functions: seven operations / 33 words
match, excluding the separate partial-update path. Found and corrected an early
research assumption that FilterWidth was the filter enum: actual 2DAvg is 4 and
sets a different SPR2 register bit. That incorrect assumption never entered any
phone image or published implementation. No original XML/library/cfg is uploaded.

Implemented complete public 94-byte native422 DSC PPS decoding, DRM C initializer
generation and byte roundtrip, retaining physical 8 bpp separately from encoded
16 bpp groups. Added a check compiling the exact pinned kernel's real PPS packer
and structure, including the wrong-bpp negative control and CI ASan/UBSan. This
does not patch/enable a panel, DSI host native422 path or DPU SPR lifecycle.

Seventeen host tests pass locally, including negative inputs. Further checks and
Actions results are recorded after execution. Existing compiled kernel remains
d337d2f4bea9 until a new full build is completed; no extra hardware support is
inferred from host-tool changes. The original read-only authorization is intact.

### Native422 DSI calculation integration

The existing DRM1.2 422 RC table reproduces the AA569 ranges. Added an isolated
MSM DSI patch selecting it, disabling RGB conversion, using doubled bpp in a
temporary RC calculation and restoring physical bpp before bandwidth/DPU use.
The expanded real-C host check builds the patched functions and original DRM
helpers from minimal panel geometry: all128 PPS bytes match. The original
DSI baseline fails the same native422 control, its RGB packet stays identical,
and four malformed native422 inputs return EINVAL. Full ARM64 Actions is next.
No panel or SPR/UDC lifecycle is enabled; the phone was not accessed this turn.

### Verified native422 build

Actions39910147687, integration badf9ea99becb61b5e3b25fa9e6f5be2abd3c913, passed
all17 tests, real-C DSI/DRM ASan/UBSan controls, ARM64 msm/touch modules and QEMU.
Full artifact12482367366 (60188703 bytes) was actually downloaded with resumable
ranges and SHA2565dc070b4c0df13b544550cc2e69cf1b8575ef81fcb7be01a7d1239c660b27c59.
ZIP CRC/all23 manifest files, exact boot sections, matching ARM64 module release
and C reports pass locally. Both DTBs match d337 bytes; fresh owner-specific
libufdt controls, all6 overlays and15-bank protected-memory checks pass again.
Kernelrelease7.2.0-oneplus13-g7a81d184e309-c8c417595c712-p52f0efb312f3 now carries
the real phone patch digest. A new unsigned v4 triplet/RAM candidate was packed
and independently read back on the host. No device command was issued this turn.

The intermediate7dcfe7 build39908683996 also passed. Its small report was checked;
two whole-download strategies timed out before final archive validation and
were superseded, not represented as verified full downloads. The final badf9e
artifact used persistent range checkpoints and downloaded/verified completely.
Windows MinGW needed -mno-ms-bitfields to retain Linux packed PPS ABI; the
real128-byte kernel assertion stays enabled, and Linux ARM64 sanitizer CI passes.

Remaining: command-mode transfer/lane-rate handling, DSPP ownership/SPR/UDC
lifecycle, AA569 panel/brightness integration and actual physical acceptance.
Current minimal diagnostic DTBs do not enable MDSS. No working-display claim.

## 2026-10-23 — command-clock continuation and reuse-first instruction

Owner requests that future problems first be checked against the original
project and public solutions. Rechecked upstream integration88fd48f85dee,
kernel7a81d184e309, dodge WIP1f2047e8663e and prior Pagani reference. Their
different panel paths provide reusable framework code but no matching AA569
SPR2/native422 implementation. Recorded the exact distinction in NATIVE-DISPLAY.

Implemented isolated native422 CMD HS-ceiling selection with shared byte/pixel/
PHY requests, conservative full-frame packet budget validation and mode_valid
error propagation. No defaults/DTBs enable it. Real-function local C checks pass
six legacy-path controls and ten invalid inputs, plus the existing full PPS
check; all17 Python tests pass. Initial host harness compilation exposed one
missing WARN_ON_ONCE shim, which was fixed without changing kernel behavior.
Full kernel/ASan/UBSan Actions validation follows. No phone command was issued.

Clock build39930688258 at185b5de1af75 passed ARM64 kernel/modules, host sanitizer
checks and QEMU. It is an intermediate build; its full archive has not yet been
downloaded/inspected and is not substituted for the last verified delivery.

Added an isolated AA569 panel component, mechanically generated public command/
DSC header, fixed starting DBV1433 and real-callback host fault checks. Corrected
the lifecycle split so disable does not send sleep-in before a possible enable.
GPIO polarity is checked before setting output directions. Failed regulator
disable keeps ownership and rejects a second power-on until cleanup succeeds.
No DTS enables the module. SPR2 and full brightness/PWM remain pending.

Local real-C callback tests and19 Python tests pass. Initial C harness failed
on an unnecessary ssize_t typedef and misleading one-line mock indentation;
the host shims were corrected while retaining Wall/Wextra/Werror. No suppression
of driver warnings or hardware result was introduced. All149 init failure
positions,3 off failures,6 supply controls and short-write recovery pass.
The owner reports that the phone is currently unreachable and will provide a
future access method; continue offline only. No ADB command was attempted.
