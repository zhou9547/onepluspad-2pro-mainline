# AA569 native display investigation

## Versioned evidence, 2026-10-23

The owner's Android selects AA569 P3 A0019 production at 1440x3168. Stock DSI
sysfs lists command-mode 120/60/90/120 Hz modes. Linux has not taken it over.

OnePlusOSS d50b305f7da9e14715a25120a4ac7b1a4b8b97c3 has a 1736-byte WQHD
SDC 120 Hz on-sequence (150 packets), SHA-256
304ebdaeab88eb5a3f62854816bf1354cde3b4505851a7bbdf4cb9922ce986e8.
It and the off-sequence match this phone's runtime FDT byte-for-byte.
tools/oneplus13/panel.py preserves packet type, channel, vendor flags, payload
and delay. Its generated JSON contains public commands, no serial/calibration.

DSC is 1.2, 10 bpc, native 4:2:2, 720x22 slices, two slices per packet. Vendor
PPS has convert_rgb=false and chunk_bytes=720. Its encoded group rate is 256 in
Q4 units (16 bits per two-pixel group), while DT specifies eight compressed bits
per physical pixel. Blindly passing either 8 or 16 through the entire upstream
pipeline changes PPS or lane rate. The baseline host overwrites convert_rgb=1
and selects 444 RC tables. The isolated patch below fixes native422 arithmetic;
a compatible string and enabled nodes are insufficient.

Stock topology index 1 is two mixers, two DSC encoders and one DSI interface.
Initialization selects application-processor SPR (panel page 0x14, register
0x82=1) and PenTile packing. The platform base lacks DPU SPR setup. Official
code programs it through DSPP/REGDMA: dspp_spr and
reg_dmav1_setup_spr_init_cfgv2. This processing cannot be silently omitted.

Supplies/reset: L12B VDDIO, L13B VCI, TLMM98 reset, TLMM86 TE, PM8550VE_F
GPIO7 VDDR enable. The platform F GPIO range is six pins, although the GPIO
driver supports eight; the phone node needs its actual eight-pin range.
Regulator values and sequencing must follow stock phone data.

## Implementation boundary

Current offline work package: use an explicitly advertised, characterized
`mipi_dsi_device.hs_rate` ceiling for native422 command transfers on a single
D-PHY link. Derive byte/pixel/PHY requests from that same ceiling, reject a
packet budget that cannot fit the nominal refresh period, and keep legacy,
video, C-PHY and bonded calculations unchanged. Acceptance is compilation of
the real changed functions with positive/negative and baseline controls plus
an ARM64 kernel build. This does not program the vendor's 6800-us DPU transfer
window, prove PLL rounding or establish usable display support. Panel/SPR
integration remains a separate work package.

Native display remains 有源码线索. No placeholder panel driver was enabled to
make the feature table look complete. The diagnostic tree retains its unverified
inherited framebuffer; msm is a module for future controlled takeover.

Next: implement SPR configuration/lifecycle, verify the native422 DSC patch and
topology, then add the panel driver preserving
command bytes and supply order. Test one 120 Hz mode first. Actual takeover and
power cycles require a separately authorized RAM test after transport/recovery.

Debugfs golden state is unavailable in the running Android namespace. No mount,
control write, register poke, display-memory read or test boot was used to bypass
that restriction. Ordinary display configuration searches did not yield a usable
SPR payload. Actual runtime evidence or a validated open configuration is still
required; guessed coefficients are not an acceptable replacement.

### Later finding: stock SPR configuration is available

A bounded read-only search of /vendor/etc found the panel-specific spr_cfg XML
outside the display/displayconfig directories searched earlier. It is 3234 bytes,
SHA-256 e258d5612a7c03f56d8cb8cebfd95105749eb9fae087eacd80d14fb88b77232d.
It has four modes with the same filter/phase settings. The original and the
display libraries are kept privately on the host, not uploaded or bundled.
The earlier lack-of-file observation applies only to the first two directories.

Further offline inspection locates SPRDriverIntfImpl::PrepareSPRInitCfg,
SPRDriverIntfImplV2::PrepareSPRInitCfg and floatToU1_10 in libsdmextension.so.
These convert semantic XML parameters and panel packing into the opaque kernel
cfg fields. The semantic conversion is now implemented and checked offline as
described below. REGDMA/lifecycle integration is still unimplemented; the mere
existence of the XML does not make the Android driver usable in mainline.

The actual stock SPR version is 2.0 and the register span is 0x200 bytes. Stock
SPR offsets are 0x15400/0x14400/0x13400/0x12400 relative to their DSPP blocks;
the DSPP bases are 0x55000/0x57000/0x59000/0x5b000. Keep DSPP/SPR selection
consistent with the two-mixer topology. No register access was performed.

## Implemented offline conversion, 2026-10-23

`tools/oneplus13/spr.py` strictly parses the private XML, supports only the
investigated PenTile / 2DAvg / YYGM profile and emits a private cfg payload plus
a relative register plan. It has no ADB, networking, MMIO or execution interface.
Unknown profiles, duplicate fields, out-of-range values, discarded fourth-colour
phase entries and nonzero uninvestigated legacy fields fail closed.

The original Android library was not loaded into the host process. A bounded
Unicorn ARM64 emulator mapped its ELF bytes into simulated memory and ran only
the parser's InitializeToDefaults and the base/V2 PrepareSPRInitCfg routines.
Immutable map initializers were reconstructed from that exact ELF. Semantic
fields were supplied at offsets established by exported setter/getter routines;
the entire XML parser and a live Android commit were not emulated. The prepared
payload matches the independent Python conversion. This checks translation,
not the actual Android feature-enable state or live register contents.

An independent host C harness compiled five unmodified packing functions from
the pinned public vendor source d50b305f7da9. Its seven operations / 33 words
match the generated relative register plan, excluding the separately owned
partial-update operation. Four XML modes produce the same payload. Originals,
emulator scripts, proprietary libraries and generated cfg data stay private.

Important details established by this check:

- 2DAvg maps to enum 4; SPR2 moves bit 2 of that enum to config bit 15. The
  legacy XML FilterWidth=0 must not replace the enum. YYGM maps to enum 0.
- Signed phase coefficients use five-bit fields; the last word keeps only ten
  bits. Filter coefficients use signed eleven-bit fields.
- PBA first three values retain their magnitude; trailing polarity values are
  remapped by the Android layer and again by the kernel packer.
- The pinned SPR2 common path does not write cfg14 / offset 0x54. No write is
  invented for it. The config update preserves bit 25 (UDC), so a native driver
  still needs explicit UDC ownership/handover rather than blindly copying it.
- PBA uses a direct write before the queued REGDMA kickoff. A flat list of
  guessed CPU MMIO writes is not an equivalent lifecycle implementation.

`tools/oneplus13/dsc.py` decodes every meaningful byte of the public 94-byte PPS
into a DRM configuration and round-trips it with 34 trailing zero bytes. It
retains physical bpp=128 in Q4 and produces PPS group bpp=256 only at packing.
It preserves stock RC ranges/delays/offsets instead of recomputing 444 defaults.
`check-display.py` compiles the pinned kernel's actual DRM DSC structure and PPS
packer, checks all 128 bytes and requires an incorrect-bpp negative control to
fail. Actions runs that C check with ASan/UBSan; public result files accompany
future compiled candidates. The source of the exact kernel blob is verified.

Local host tests now include enum/PBA/signed packing, unknown/unsafe XML and PPS
reserved-bit/profile/truncation checks (17 tests total). The panel and SPR are
not enabled by these changes.

### DSI native422 calculation patch

The existing DRM DSC1.2 422 table has the phone's RC ranges and initial values.
`kernel-patches/0001-dsi-native422-rc.patch` selects that table and keeps
convert_rgb=false. It computes RC in a temporary two-pixel-group configuration,
then restores physical-pixel bpp in the shared MSM/DPU configuration. The DPU
already doubles its native422 hardware field. Native420 is not added here.
Invalid version, odd/zero slice width, slice height below2 and simultaneous
native420/native422 are rejected before arithmetic.

The expanded C check compiles the actual patched DSI functions, original DRM RC
tables/arithmetic and original PPS packer. Starting with only the minimal panel
geometry/format, its computed complete128-byte PPS matches the original AA569
packet. The unmodified DSI baseline fails this same packet comparison; its RGB
path remains byte-identical after the patch. Four malformed native422 profiles
are rejected. This provides more evidence than copying precomputed PPS fields,
but still does not exercise hardware. Actions39910147687 validates the patch in the real ARM64 msm module; the
actual downloaded artifact and C ASan/UBSan report also passed. Diagnostic
DTBs still leave MDSS disabled.

## Remaining integration work

1. Handle command transfer timing/lane rate explicitly and ensure the panel sends the exact
   vendor PPS bytes with physical-pixel bpp in its shared configuration.
2. Add phone-specific SPR2 capability offsets and reserve DSPPs for SPR even
   without a user CTM/gamma LUT. The current CRTC requests DSPPs only for those
   user colour properties; setting SPR registers alone would miss ownership.
3. Implement SPR/UDC takeover, runtime-PM/clocks, REGDMA programming/disable and
   full-frame origin handling before the first frame. No lifecycle shortcut has
   been validated from the available live state.
4. Add the AA569 panel with public exact commands, actual supplies/GPIO range,
   TE and one 120 Hz mode, then connect the panel-following touch candidate.
5. Verify transport/recovery in a bounded RAM boot before physical native-display
   tests. These operations remain outside the read-only device authorization.

### Panel sequencing details for the next implementation

The production overlay selects Oplus custom power control, not the generic
DSI regulator loop. `oplus_display_power.c` at d50b305f7da9 uses the panel's
explicit string sequence and does not add the generic regulator-entry sleep
fields to it. The actual sequence is: wait 1 ms, VDDIO on, wait 3 ms, physical
GPIO7 high (VDDR), wait 3 ms, VCI on, wait 10 ms. Shutdown waits 1 ms, disables
VCI, waits 3 ms, lowers GPIO7, waits 3 ms, disables VDDIO, waits 1 ms. VDDIO is
1.8 V/load220000 uA, VCI 3.0 V/load10000 uA; off loads are8000/300 uA.
Reset position2 defers the physical high10ms/low5ms/high30ms sequence until
panel prepare. Preserve that ordering instead of bulk-enabling both supplies.

The stock ordinary-brightness range is1..4094 with normal maximum3515 and
default1433, HS DCS and inverted-DBV byte-order handling. The Oplus backlight
callback overrides the generic fallback; inspect that active implementation
before selecting a mainline brightness helper. Vendor command flag0x40 is
passed to msg.flags by dsi_panel.c; a native sender must account for its batch
transport semantics separately from the preserved panel payload bytes.

The stock command-mode transfer is6800 us at1363200000 bit/s/lane. The current
DSI host has no hs_rate handling. Using the stock porches as a naive120 Hz DRM
mode (htotal1562, vtotal3200, RGB101010, four D-PHY lanes) in its existing DSC
clock formula produces1457280000 bit/s/lane instead. CMD porches represent
transport overhead in that formula, as the host's own comment explains. Do not
claim physical transfer timing is solved by the now-matching DSC PPS.

### Reuse check and command-clock implementation

The source project was checked again before this implementation, per the
owner's instruction to consult it first. Integration upstream main is
88fd48f85dee54c482a98e55319b11d1739e8852 and its kernel erhai/v0.2 remains
7a81d184e3098624d4342d8f4eff5e23674bcc9f. Its NT36536 display is dual-DSI video
mode with external KTZ8868 backlights; it does not implement this phone's
AA569 SPR2/native422 command pipeline. Its platform/TE/resource helpers are
already reused in the pinned kernel. The current sm8750-mainline OnePlus-13-WIP
branch remains 1f2047e8663eda76c8b172fd3e040e3b3fa17950 and selects NT37801 plus
different touch parameters. Pagani reference c49d202f6c16 uses AA594 RGB DSC;
its explicit comments still list slice-per-packet as a TODO. Those sequences
must not replace the measured AA569 production profile.

Patch0002 chooses the explicit, characterized HS ceiling only on a native422
command-mode single D-PHY link. This use respects hs_rate as an upper bound;
it rounds down to whole byte clocks rather than interpreting the field as a
universal fixed rate. The phone profile requests1363200000bit/s/lane,
170400000Hz byte clock and181760000Hz pixel clock from the same source.
The PHY request consumes that exact byte clock. Missing rates and the video,
C-PHY, bonded, RGB and uncompressed paths retain their previous calculation.
Impossible geometry, packet grouping and payload budgets return errors;
mode_valid rejects a zero/error byte-clock request.

check-command-clock.py compiles those actual functions and the unchanged
baseline, including the PHY request. Local Windows checks pass: six baseline
controls, ten invalid controls, non-byte-aligned ceiling rounding, and the
existing full PPS check. ARM64/sanitizer Actions is still required before a
compiled result is claimed. The packet-only full-frame lower bound is6726us
(two slices/packet), below the stock6800us budget; PHY transitions, actual PLL
rounding, DPU fetch/bandwidth scheduling and scan/TE behavior remain unverified.
This patch is not a6800us DPU scheduler or an enabled panel.

Primary references:
- https://github.com/yzddmr6/onepluspad-2pro-mainline/tree/88fd48f85dee54c482a98e55319b11d1739e8852
- https://github.com/yzddmr6/linux-sm8750-erhai/blob/7a81d184e3098624d4342d8f4eff5e23674bcc9f/arch/arm64/boot/dts/qcom/sm8750-erhai.dts
- https://github.com/sm8750-mainline/linux/blob/1f2047e8663eda76c8b172fd3e040e3b3fa17950/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dts
- https://github.com/yzddmr6/linux-sm8750-erhai/blob/7a81d184e3098624d4342d8f4eff5e23674bcc9f/include/drm/drm_mipi_dsi.h

### AA569 component implementation (not connected to a DTB)

The next isolated component lives in devices/oneplus13/kernel/panel-aa569 and
is compiled as a module only. No current DTS contains its compatible string.
Its generated public header verifies the original command hashes and exact
DCS packet types; the full94-byte vendor PPS remains untouched in the payload.
Prepare sends149 LP packets; enable sends the final display-on packet in LP
and a fixed starting brightness in HS. Disable/unprepare split the stock off
sequence at display-off/sleep-in to allow a disable/enable without sleep-in.
Power order, loads and physical HIGH/LOW/HIGH reset match the custom vendor
sequence above. Error paths track regulator ownership and stop double-enables
after a failed disable instead of pretending that power has gone away.

Inspection of the actual oplus_display_bl.c callback at d50b305f confirms that
bl_inverted_dbv swaps the value before mipi_dsi_dcs_set_display_brightness.
The latter helper sends low byte first, so the resulting phone wire order is
MSB-first:DBV1433 is51 05 99. Only that fixed normal-range level is implemented;
PWM changes, low-DBV, HBM, AOD and adaptive brightness remain pending. No
backlight UI is exposed by the component. The init LP/off HS states come from
the production common.dtsi. Vendor0x40 is DMA grouping in dsi_panel.c and
dsi_ctrl.c; mainline serializes those packets and preserves bytes/type/order/
delays, but equivalent physical timing is not yet established.

check-panel.py compiles the real component's power/command/lifecycle callbacks
with host-only mocked I/O. The emitted150 on/3 off packets and LP/HS flags match
the independent public fixture; power/reset/waits match the stock plan. Every
one of149 prepare packet positions is fault-injected, short writes are rejected,
six supply/load/disable controls retain balanced ownership, and all three off
failure positions plus disable/enable are checked. Nineteen Python tests pass.
ARM64 module/API and sanitizer checks follow in Actions. None of these checks
is a live panel test or a substitute for the missing DPU SPR2 pipeline.
