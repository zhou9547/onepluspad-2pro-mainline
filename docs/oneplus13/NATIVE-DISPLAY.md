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
and selects 444 RC tables. A compatible string and enabled nodes are insufficient.

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

Native display remains 有源码线索. No placeholder panel driver was enabled to
make the feature table look complete. The diagnostic tree retains its unverified
inherited framebuffer; msm is a module for future controlled takeover.

Next: implement SPR configuration/lifecycle and native-422 DSC arithmetic,
compare generated PPS/topology with stock, then add the panel driver preserving
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
reserved-bit/profile/truncation checks (17 tests total). No kernel native-display
driver has been enabled by these host-tool changes.

## Remaining integration work

1. Carry the validated precomputed native422 DSC fields through the DSI host
   without its unconditional RGB/444 recomputation, retaining physical-pixel bpp
   for bandwidth and doubled group bpp only where required by the PPS/hardware.
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
