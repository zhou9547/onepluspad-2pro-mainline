# Technical debt (single register for the phone)

New offline increment: patch0011 derives the clock floor from the actual two-LM
reservation and splits pipes against the inverse burst/inefficiency budget of
the real OPP before assignment. Aggregate bandwidth is unchanged. Actual compiled
DTB is mandatory, budget evidence version3 binds its hash, and private packaging
rejects older evidence. Ten local C checks and61 tooling tests pass (one Windows
flock skip); ARM64 sanitizers/full build and matching refreshed rootfs/QEMU are
pending. Source fixtures are not physical allocator/SSPP acceptance. See DPU-OPP.md.
No new phone operations; previous single-test authorization remains consumed.

Latest separate authorization: one native RAM boot and one explicit activation
completed. Real preflight passed; module load returned, but DPU atomic performance
check rejected with -7. Host requested early recovery and Android returned at
135.4s with sampled metadata matching. No flash/partition changes. The one-test
authorization is consumed; further phone operations require a new authorization.
The 1GHz success fixture missed the actual 575MHz MDP OPP, while the present
full-width budget requires 711529412Hz. Current candidate is ineligible for retry.
Bind compiled-DTB OPP, actual topology/plane splitting and performance checks;
review vendor/original processing before correcting the votes, never raise the
OPP just to suppress rejection. Physical display and all other acceptance gates
remain open. See FIXED-PHY.md for the separate hardware evidence.

Fixed-PHY increment: vendor V7.2 timing_val/enable/commit path confirms direct
14-register production values. Patch0009 selects them only for the attached
AA569/SM8750/DSI0 fixed-rate candidate and synchronizes shared host timing.
Patch0010 fixes ignored runtime-PM failures and PM/OPP cleanup on clock failure.
Ten real C ARM64 ASan/UBSan checks and kernel build40065006440 pass. Actual
CCF/TE callback fixtures and 61 ARM64 tooling tests pass in40065992683; matching
GNOME/QEMU40066356160 passes. These verify source calculations and guarded
interfaces, not physical clocks, TE, framebuffer takeover or panel output.
An explicit RAM-only one-shot preflight/loader is implemented, without an auto
service. Actual module loading is untested. QEMU mocks USB active and uses a
fixture observation clock; real deadline threshold tests remain independent.
Default native packaging remains closed; an explicit reviewed-evidence gate
permits host-only private candidate preparation. No phone operations or hardware
authorization; physical display/touch/WLAN/GPU acceptance still blocks a usable
combined port. See FIXED-PHY.md for the exact evidence and remaining gates.

2026-10-24 PLL/PHY audit: nominal 1.3632 GHz and valid 2x/3x VCO values are
exact in the 18-bit fractional arithmetic, but six of fourteen generic D-PHY
timing fields differ from the final AA569 production DTS override. Actual C
platform/vendor arithmetic checks added; ARM64 sanitizer audit40062728159 passed
66 PLL cases plus PHY checks. Downloaded artifact, nine public source blobs and
local/ARM64 C results match. Kernel job skipped; runtime artifacts unchanged.
Do not promote this to physical frequency/timing equivalence or patch the generic
PHY with board bytes. Trace vendor V7.2 timing commit/overrides and shared CCF
pixel/byte selection next. See PLL-PHY-AUDIT.md. No phone/kernel/image changes.

2026-10-24 D07 increment: explicit bounded whole-group DSI API and the AA569
13-group sender are implemented, with actual C packing/resource/failure tests.
No cross-call queue and no silent serial fallback. Nine local/ARM64 C checks
(Actions ASan/UBSan) and 53 tooling tests pass. Kernel/module build40058811743
and refreshed matching GNOME/rootfs/QEMU40059533734 pass; all artifacts have
been downloaded and checked against manifests, module release and group hashes.
Physical PLL/TE/burst timing, takeover and D16 activation are still open.
See DSI-BATCH.md. Zero phone operations; native desktop packaging stays disabled.

2026-10-24 follow-up: the private payload now has a versioned release/profile/
helper hash manifest and a data-only stage across switch_root. Old or partial
payloads fail closed, merged-/usr is handled explicitly, and the helper remains
non-executable in /run. Host and ARM64 Actions suites: 53 passed. The new QEMU
observer in 40056382745 verified copy/permissions/failure controls after
switch_root, handoff and 180-second expiry/reboot; downloaded evidence matches.
See NATIVE-HANDOFF.md. Additional pinned vendor review confirms deferred
kickoff/resource cleanup in FETCH_MEMORY, FIFO/non-embedded overrides and the
broadcast early-flush exception. Nominal single-link groups peak at 312 bytes;
wire timing equivalence and actual PLL behavior remain unproven.
D16 activation and D07/D10/D17 physical timing/resource work remain open;
native desktop packaging is still disabled. No hardware operations this round.

Current offline gate, 2026-10-24: see OFFLINE-NATIVE-GATE.md. No hardware work
in this phase. D15: native helper/SPR identity source fixed and host-checked,
new ARM64 build 40051765091 and eight C ASan/UBSan checks passed. D16: full
rootfs aliases bypassed diagnostic manual loading; the fail-closed kmod policy
now passes actual QEMU loading controls with the rebuilt kernel in 40054456226.
Native desktop packaging remains disabled until rebuilt policy, handoff and
explicit activation are validated. D07/D10 timing and physical acceptance stay
open; these new findings are not a proven cause of the default desktop black screen.

D17: the default simple-framebuffer node has no clock/power-domain/supply
references. Archived phone logs show simpledrm registration before unused
clock/domain cleanup. Review the pinned sysfb driver and actual display resource
ownership; this is a lifecycle gap and a black-screen hypothesis, not a proven
diagnosis. No blanket ignore-unused boot flags or speculative hardware trial.

Actions40051767501 validates the new kmod policy with the original pinned
kernel and refreshed rootfs. D16's explicit activation/cross-root path remains
open and native packaging remains disabled. The rebuilt identity-fixed kernel
combination 40054456226 passed independently using integration 2957513a and
kernel artifact d624154c. This closes the offline build/kmod/handoff portion,
not physical display acceptance or explicit native activation across switch_root.

| ID | Temporary choice / location | Reason and impact | Removal criterion |
| --- | --- | --- | --- |
| D01 | Community low-memory fallback in the default DTS | The owner-specific calibrated candidate now uses actual 15-bank runtime RAM and excludes every stock protected interval offline, but bootloader fixups and actual RAM use are untested | Verify memory/fixups through a bounded RAM boot before promoting the private calibration to the default board profile |
| D02 | Firmware framebuffer in phone DTS; native candidate identity-domain patch0005 | Enables testing inherited display without inventing a panel sequence; resource lifetime and pixel format are not hardware verified | Port and verify native phone panel/DSC/timings/power sequence |
| D03 | Pad-maintained SM8750 kernel as a pinned platform base | Reuses platform fixes only; its board support is not phone support | Track upstream and replace with a maintained phone kernel after equivalent validation |
| D04 | Sleep targets masked in GNOME staging rootfs | Avoid entering untested phone suspend/resume paths; ordinary standby is unavailable | Cold-boot and repeated suspend/resume tests on the phone with independent recovery |
| D05 | Phone-only MSM DSI native422 RC glue in kernel-patches/0001 | Selects existing 422 tables and adapts the DRM group-bpp arithmetic to MSM physical-bpp consumers; complete PPS/RGB controls pass offline, actual pipeline remains untested | Replace when upstream has equivalent format/rate semantics, preserving the byte-exact PPS and real-device regression results |
| D06 | Native422 command HS-ceiling selection0002 and fixed AA569 burst-budget patch0006 | Replaces synthetic CMD-porch clock selection only for an explicit characterized ceiling on a single D-PHY link; validates packet budget and conservatively scales DPU performance votes for6800us with new-state/OPP/ICC rejection; does not program a hardware transfer timer or prove PLL rounding; peak votes intentionally overestimate until measured | Replace with equivalent upstream command-transfer timing support and validate bandwidth, actual clocks, frame completion and power-cycle regression on hardware |
| D07 | AA569 fixed DBV1433 with bounded synchronous vendor-group submission in patch0008 | Exact production bytes, group boundaries, resource lifetime and error controls pass host C checks; only the experimental native DTB enables the component, no brightness UI is enabled; physical group/TE timing remains unverified | Validate actual PLL/SPR/transfer scheduling and physical init/power cycles, then add validated PWM/brightness behavior |
| D08 | SM8750 native422 DPU corrections in phone-only kernel patch0003 | Bridges vendor container/initial-line, full-ICH precision, modern-wrapper and PPB requirements while preserving physical-bpp semantics; actual output remains untested | Replace with equivalent upstream changes and preserve vendor/register-capture controls plus real-device regression |
| D09 | Private AA569 fixed-profile format in kernel/spr-aa569 and spr.py | Separates private coefficients from public sources and bounds the decoder/transaction planner before runtime integration; not a standard firmware ABI and not a working SPR pipeline | Replace with an upstream panel/DRM configuration interface when available; retain strict field checks, private-data isolation and vendor-equivalent packing |
| D10 | Opt-in fixed-profile SPR CPU startup/PM backend | Reuses community quiet-pipeline approach with private AA569 data, all-pipe UDC preflight, idle/clocks/reset guards and explicit display exclusivity; no DMA, live profiles, partial update or fingerprint/UDC functionality | Replace with reviewed upstream SPR/REGDMA integration after hardware timing/ownership/power-cycle validation; retain strict profile/geometry and no-private-data-in-Git controls |
| D11 | WLAN-only stock-minimum constraints, fixed IO system-load and reference PCIe PHY supplies | pwrseq only bulk-enables supplies; phone consumer requests differ from the base parent range/Pad minimums. PCIe PHY rails and RF clock are same-SoC reference candidates, not independent electrical proof. Exact OTA inputs now match owner hashes, but active BDF selection and SAR remain unverified | Verify exact phone PHY/shared-rail behavior, firmware/board/revision/SAR and replace fixed load with an upstream consumer request when available; do not promote this standalone tree before hardware acceptance |
| D12 | GPU-only tree uses pinned platform GMU/clock/OPP graph | Phone chip ID and microcode reserved memory match, and the correct signed ZAP now matches the owner hash; authentication, voltage/frequency behavior and hardware renderer remain unverified; headless mode needs explicit separate_gpu_kms=1 | Verify bounded isolated authentication/render/power tests, then replace with upstream board support and integrate only after real regression |
| D13 | Separate RAM desktop profile, fixed USB debug services and 900-second absolute deadline | Provides an observable reversible userspace handoff before storage installation; root shells are restricted to trusted USB, there is no persistence and no unattended permanent desktop | Validate phone USB/handoff/recovery and individual hardware first; replace with an explicitly chosen persistent layout/account policy and packaged optional debug support |


Unimplemented peripherals are tracked in STATUS.md, not represented as working.

## 2026-10-24 本地真机补充

D14：ABL改写根model/compatible，导致手机physical-platform误拒绝。已按原项目model＋chassis方式修复并通过正反例，真机已越过切根门槛并进入systemd/GDM。继续保留VMID3、Gunyah及无绑定驱动条件。保持900秒截止的真机会话已返回原Android，单次交接与返回验证完成；物理显示、触控、GPU及WLAN仍独立待验收。
