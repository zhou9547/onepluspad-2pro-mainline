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
