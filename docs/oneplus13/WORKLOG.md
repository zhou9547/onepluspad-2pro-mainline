# Work log

## 2026-10-23 — fixed-profile runtime SPR continuation

Rechecked project status/debt and installed skill. The platform branch remains
7a81d184e309. Public vendor REGDMA3 and community CPU-write paths were compared;
this work uses a restricted static startup/PM backend with no DMA allocations.
Acceptance and alternatives are recorded in NATIVE-DISPLAY; debtD10 records
limits. Found and documented the0x1000 stock/upstream MDP base difference
before implementing register access. No phone query or modification this turn.

Real-C runtime checks now pass: all four physical addresses, last-pipe UDC
conflict with zero writes, clocks/busy/fault/profile/board guards, three PM
cycles, AA569 atomic format checks, flush bit8/bounds and propagated MDSS reset
errors. No SPR coefficient writes are added to live atomic_begin. Kernel
integration reserves DSPP without CTM/gamma and restores before encoders;
suspend refusal returns before clocks-off. Pending ARM64/ASan build results
are not hardware tests. Both prior diagnostic/touch DTS files are unchanged.

Actions39952445486 atfcafb8d passed the host C/sanitizer checks but failed the
early ARM64 object compile: mdp_common.xml.h was missing. The new object was
appended after Makefile's immediately expanded generated-header dependency
rule. Moved both SPR objects into the existing DPU object list in patch0004,
before header dependencies, and removed the late build.sh append. Also dropped
an unused dpu_crtc.h include. No generated file was fabricated or check removed.

Run39953182467 at66f28a3 compiled the new runtime object but failed the full
catalog build: Glymur/Eliza/Kaanapali also referenced the shared scalar
sm8750_dspp_sblk. Preserve that scalar unchanged and introduce a separately
named four-entry SM8750 AA569 array instead; do not change other SoC catalogs
or suppress incompatible-pointer warnings. The next full build checks them.

## 2026-10-23 — corrected SSH port and DPU/SPR continuation

Owner corrected the private SSH endpoint's port. An independent auditor reviewed
the single read-only 1KiB fingerprint query with a 45-second host deadline and
no forwarding/local commands. Connection and authentication succeeded. The
reported build fingerprint exactly matches the earlier private Android JSON.
No root command, device modification or phone/host file transfer occurred.

Before code changes rechecked original kernel upstream: erhai/v0.2 is still
7a81d184e309. Current work scope/acceptance is in NATIVE-DISPLAY. The vendor
widebus command-stream setup confirms mainline's bytes/6 total; the community
reference's extra factor2 must not be copied. Investigate whole pipeline and
preserve public PPS/RGB controls before enabling any independent native tree.

Patch0003 now passes 48 native422 cases against unmodified public vendor C,
48 RGB cases against vendor and the pinned baseline, register captures for
full ICH/wrapper/hardware-bpp, legacy register bounds and two noncontiguous
PPB slots with replay. AA569 initial lines now match vendor4 versus baseline3.
Actions39946199507 atdb3012e345f75da4b54ddab73765c4abaa7b5b02 subsequently
passed all19 Python checks, DSC/clock/panel/DPU C ASan/UBSan, complete ARM64
kernel/modules and QEMU init/shutdown. No panel node or SPR implementation is
enabled by this patch. Full artifact12497598833 was actually downloaded and
verified against GitHub's digest:60207128 bytes, SHA256
9c46428a25fa6d9a0e13e4d9d8a687f0da044c109cc53ddaa0ee79b16e2f23a9.
CRC,26 manifest files, CI checksums, Image/Android sections, module AArch64
identity/vermagic and all reports passed. The bounded downloader's first host
pass hit its105-second deadline with partial ranges retained; one suffix-only
resume completed and verified. Neither the signed URL nor credential was saved.

Both downloaded DTBs remain identical to the earlier diagnostics, MDSS disabled
and no AA569 node. Repeated private stock-positive/all-six-overlay/15-bank
calibration and host-only unsigned v4/RAM-format repacking/readback passed.
Release7.2.0-oneplus13-g7a81d184e309-c6c2e0d66c4eb-pb61f52cc6834.
Only the one bounded non-root SSH getprop ran on the phone; no transfers,
changes, reboot or test boot. Next: explicit SPR2 ownership/update/recovery
and DPU transfer window, then an isolated display tree. Native display,
physical touch and a normally flashable system are not completed.

### Next isolated component: SPR2 private profile and plan

Added a fixed176-byte private input decoder and typed transaction planner,
compiled as uncalled code in the phone's msm module. There are no MMIO,
REGDMA submission, firmware loading, resource reservation or runtime hooks.
CI uses nine synthetic profiles only. The owner's four identical XML modes
were also checked privately against the actual C output and the previously
validated vendor packing; the binary remains under private on the host.

C checks reject176 truncations, oversize,176 single-byte corruptions,34 invalid
reserved-word cases, five semantic/UDC/PBA errors; four unaligned addresses
and unchanged failure outputs pass. Python rejects differing stock modes
instead of guessing a fixed120Hz mapping. Pending Actions compilation and
sanitizers are not yet marked passed. This remains a prerequisite component,
not an enabled native display or implementation of REGDMA ownership/recovery.

Actions39948240876 at a27d8b9 failed in the host C harness before ARM64 SPR
compilation: the Linux errno shim recursively included glibc errno.h, whose
own Linux include then omitted EINVAL. Windows did not expose that include
cycle. Corrected only the host shim to explicit Linux EINVAL/EBADMSG values;
no driver code, compiler warning or check was removed. Failure log retained.

### Final verified profile/planner build and delivery

Corrected run39948575140 at363b605da6fee4922d995c8beaf5a3fe16528e2f passed
20 Python tests, all host C sanitizers, the real ARM64 kernel/modules and QEMU
init/shutdown. The downloaded12499740861 archive is60207655 bytes, SHA256
af7af14ca63880166846672649a3e207c8bab288781a741d0d70a5b2fb988216.
CRC,27 manifest files, CI checksums, image sections, module identities/vermagic,
DSC/clock/panel/DPU/SPR reports all pass. The ARM64 msm ELF contains nonempty
SPR decoder/planner FUNC symbols452/572 bytes. An initial host inspector
mistakenly required the magic string as literal data; GCC had compiled it
into instructions. Replaced that invalid assumption with actual ELF function
checks, retaining all hashes/source comparisons. No kernel change was needed.
The first bounded download retained partial ranges after its deadline; a
suffix-only resume completed and verified the final digest.

Fresh default/touch DTB stock-positive/all6-overlay/15-bank calibration and
host unsigned v4/RAM-format repack/readback passed again. Current release:
7.2.0-oneplus13-g7a81d184e309-c6c2e0d66c4eb-p096c27a2bf6a.
The preceding DPU-only delivery is retained intact as a rollback archive.
Only one non-root getprop fingerprint query ran on the phone this continuation;
its reported identifier matches the saved snapshot, but partitions/FDT were
not rehashed. No file transfer, write, reboot or test boot occurred. No phone
or build task remains running. Next work is the explicit SPR2 resource/UDC
and REGDMA execution/recovery contract before enabling any native panel tree.
All-peripheral adaptation and physical display/touch acceptance remain open.

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

Follow-up review found the DRM core keeps prepared/enabled state after a failed
callback. Fixed teardown to report successful physical rail shutdown after
logging old DSI errors, while failed rail disables still retain ownership and
return errors. Added off_sent state, brightness-enable retry and the framework-
state error control. Explicit supply phandles, supported voltages and exact
voltage requests prevent dummy supplies or the old community1.8V VCI constraint
from silently passing. Expanded supply controls from6 to8; all checks pass.

Actions39940988458 at19120b5235ab failed the real panel build: this pinned
kernel has removed drm_panel_init. Its actual NT36536 driver uses the refcounted
devm_drm_panel_alloc API. Converted AA569 to that exact allocation/lifetime API;
did not add a compatibility stub or suppress the compiler error. The downloaded
failure archive is retained as panel-19120-failure.zip. Added a component-only
API compilation step before the full kernel to catch future errors sooner.
The superseded2e79723 build has the same obsolete call and must not be treated
as a usable result. Rebuild and actual artifact inspection follow.

### Verified component build and actual local delivery

Actions39941841474 at2972866edf7d795160759a6ceb06ebcbd9cb8403 passed all19 Python
checks, real-C DSC/command-clock/panel ASan/UBSan, ARM64 kernel/full modules and
QEMU init/shutdown. Intermediate39930688258 succeeded;39940988458 failed the
obsolete panel API;39941420786 was explicitly cancelled after it was superseded.
The final refcounted allocation uses the pinned kernel's real NT36536 pattern.

Full artifact12496259085 was downloaded:60205125 bytes, SHA256
ef4229485c863f27080981d461882028c01451c80d539c6f77c7ba4ad7b7db18. Local ZIP CRC,
25 manifest files, CI checksums, Image/gzip/Android sections, public DSC header,
all3 relevant modules' AArch64 identity/vermagic and reports pass. Panel module
is18184 bytes, SHA256c975b95c5deb897cf305e21e7bb91a80c3403468b04b0180c5da4695741819b8.
Kernelrelease7.2.0-oneplus13-g7a81d184e309-c6c2e0d66c4eb-p0e592c9c3dcb includes
the actual phone patch hash. BothDTBs matchbadf9e and keepMDSS disabled; noAA569
node is present. Both underwent fresh stock-positive/all6-overlay/15-bank-memory
calibration. Unsignedv4/RAM-format diagnostic images were generated and read back
on the host only.

Node streaming downloads suffered host REPL resets, retaining partial ranges
on disk. A bounded independent host Python downloader finished only the missing
suffixes and verified the final GitHub digest. No signed URL or credential was
saved in a checkpoint. Failed/intermediate logs and archives are retained.

Reuse research found joonhoekim/tb323fu-linux atda44c8412fed with community SPR/
native422 work. Compared its actual patches and the pinned OnePlus vendor DCE
function offline; Erhai gives3 initial lines where the native422 vendor helper
gives4 (RGB control3/3), and10bpc FULL_ICH_PREC handling is absent in the current
mainline function. These are explicitly pending before any native panel node
can be enabled. Different panel coefficients/bpp/catalog offsets are not copied.

The user supplied a new slow SSH endpoint and prohibited bulk phone/host file
transfers. An independent reviewer checked a single build-fingerprint query,
no root, explicit endpoint, isolated host known-hosts, no config/forwarding/local
commands, hidden password prompt and45-second host deadline. The one attempt
returned connection-refused during SSH banner exchange, before authentication.
No password was submitted, no remote command ran, no file moved and no retry
was made. Existing stock evidence remains version-scoped; current phone firmware
is unconfirmed. No device task remains active. Next work is the DPU native422
differences and then SPR2 ownership/lifecycle, as in STATUS and NATIVE-DISPLAY.

### Static SPR runtime passed; native candidate work package

Actions39953880347/bbbc3fe passed the full build after two diagnosed integration
failures (Kbuild header dependency ordering, then a shared catalog scalar).
No phone command or transfer was executed during this continuation.
Next scope: independent AA569 DTB, identity-domain client entry, seven negative
DTB controls and private module/profile initramfs packing. Twenty-three Python
checks now pass locally, including dependency cycles/traversal, wrong module
identity and byte-exact diagnostic recovery preservation. Full CI and downloaded
artifact inspection must pass before promoting any new local delivery.

### Actual native artifact and private RAM readback

Actions39981240118/e6766eb passed. Downloaded12513218063 matches GitHub digest,
ZIP CRC,30 manifest files, CI hashes, modules and real runtime FUNC symbols.
Three fresh stock-positive/all6-overlay/15-bank calibrations and v4/RAM packing
pass. Private derived ramdisk preserves all original entries and includes the
matching9-module closure and176-byte owner profile. It is not hardware tested
and its derived image has not been run in QEMU. Host staging first used a six-
versus-seven-character directory tag; corrected that local helper and preserved
the incomplete calibration directory as failure evidence. No device access.
Added helper-input hash binding to the private packer; existing artifact's helper
hash matches. Next isolated work package is the static-mode burst performance
budget, as scoped in NATIVE-DISPLAY.

### Fixed AA569 command-burst resource budget

Implemented the scoped125/102 ceiling budget on existing plane/prefill votes,
only when the explicit static SPR path is enabled. Real C arithmetic/check/ICC
functions pass261 independent integer vectors, five overflow/limit controls,
new-state bandwidth and OPP rejection with empty old aggregate, two ICC failure
positions and three baseline performance-mode comparisons. Fixed current-state
limit checking rather than relying on generic aggregation of the previous state.
No clock maximum is raised, no TE/timer register is changed, and no phone command
is executed. ASan/ARM64/actual artifact checks are pending the next Actions run.

### Fresh-frame plane geometry follow-up, 2026-10-24

39983634509/cc88ea9 compiled successfully, but is not promoted: source review
found cached plane performance is assigned in atomic_update, later than the
atomic budget check. Added a restricted calculation from new assigned pipe
geometry with the original unmodified helpers. Host C checks split/new/invalid
geometry and source identity, in addition to the prior261 budget vectors and
ICC/OPP/legacy controls. Evidence report version is now2. No device access.

### Budget delivery verified; wireless evidence, 2026-10-24

39984526255/d67f564 passed and actual60243240-byte archive matches GitHub digest,
CRC,31 manifest files, source identities, modules, QEMU and image readback.
Recalibrated all three trees and rebuilt private display RAM image; hash is in
STATUS/NATIVE-DISPLAY. Old e6766eb delivery remains preserved.
Wireless review found this phone's876mV AON/DIG and1.312V RFA requests differ
from Pad minimums. Pinned vendor cnss-peach maps to110e/WCN7860, whose mainline
support requires major2; no live revision/board/firmware proof yet. One audited
non-root metadata query matches Android build but all three vendor paths are
unavailable; no inference of missing firmware and no retry. No binary transfer
or phone modification. Matching OTA catalog found; official links return2306.
Next independent work scope and acceptance are in NATIVE-WIRELESS.md.

### Independent WLAN wiring candidate

Added phone-only WCN7860 tree and source/config gates. Stock pin review found
WLAN16 uses16mA/pull-up rather than the Pad8mA/pull-down; PCIe102/103/104 use2mA,
and F/SID5 BT-enable3 uses power-source1. Six phone consumer voltage constraints
and IO30mA/HPM are isolated to this tree. ATH12K/WCN/pwrctrl become modules;
USB/init/recovery and the older DTBs remain unchanged. No WLAN firmware, BDF,
address, SAR limit or auto-loader is fabricated. Source review is in
NATIVE-WIRELESS, fixed-load/reference-PHY debt is D11. CI compilation and actual
artifact inspection are required next. No further phone query or retry.

### WLAN checker correction from actual CI DTB

39988586068/de616a5 compiled all four DTBs and passed preceding host C checks,
then failed a checker-only vendor-address assumption: pinned mainline TLMM is
pinctrl@f100000, while stock labels it@f000000. Check the actual SM8750 compatible
and GPIO references instead. The downloaded87230-byte review ZIP matches SHA256
1aec2e327d4f71471a7aa3fdeba10acdbd37b2d89f97eed42bc60af8838755a9.
Local actual-DTB review also found the bad-drive control selected an unrelated
SoC gpio16 state; target the PMU-referenced state instead. All six controls now
reject correctly. Local module flags used the source fragment, not an actual
resolved CI config: upload-artifact excludes hidden.config by default. Added an
early nonhidden kernel.config copy for future failure review, without changing
checks or enabling generic hidden-file upload. Next Actions must check resolved
module flags, full ARM64 modules and QEMU before promotion.

### WLAN artifact completed and remaining peripheral evidence

39989714579/7a8967831938 succeeds. Actual59776599-byte attachment matches GitHub
SHA256;33 files, seven actual ARM64 modules/vermagic, resolved modular RF config,
six WLAN controls, all display checks and QEMU pass. Four fresh calibrations
pass six overlays and15 RAM-bank exclusions. Private display package uses the
new release/modules and is independently read back. A host staging filename
error was corrected before promotion; completed calibration/package inputs were
hash-checked before resuming the copy. No additional phone query or change.

Offline public audio parsing resolves an AW88461 inner header, not a proven
hardware ID. Four CRC8/inner checksums and75-register section lengths pass;
owner firmware version remains unmatched. GPU stock chipid44050001 matches the
pinned catalog. Pinned render source requires explicit separate_gpu_kms=1 for
the isolated headless path; no modules load automatically. Next GPU scope and
acceptance were recorded in NATIVE-GPU before code changes. Audio evidence and
unresolved firmware/driver/graph choices are in NATIVE-AUDIO.
