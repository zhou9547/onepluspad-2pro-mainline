# AA569 offline panel component

This module is compiled for API/ABI checking, but **no phone DTB instantiates
it**. The remaining DPU SPR2/resource/UDC/REGDMA integration must precede a
connected native-display candidate. Loading a module is not display acceptance.

The generated header is the exact public OnePlusOSS production WQHD120 sequence,
not AA594, an EVB/EVT variant or a private calibration dump. Regenerate with
tools/oneplus13/generate-panel.py and run check-panel.py against the pinned Linux
source. The generator verifies the original packet digest, type, channel and
transport flags; the real C sender is independently compared against the fixture.

One fixed120Hz mode is advertised:1440x3168,10bpc,native422DSC1.2,720x22 slices,
two slices per packet,four lanes,HS ceiling1363200000bit/s/lane. The full public
vendor PPS remains in the init payload. Physical8bpp stays in DRM/MSM config.
Prepare follows the phone's custom supply/reset sequence and LP command state.
The final display-on packet is deferred to enable. Disable sends display-off;
unprepare sends sleep-in and then the ordered rail teardown. Failed regulator
disable retains its enable ownership and blocks a second power-on until cleanup.

The component uses fixed DBV1433 (`51 05 99`) in HS mode. This matches the active
Oplus callback's inverted-DBV byte order without exposing unimplemented PWM,
low-DBV, HBM, AOD, temperature compensation or brightness-control UI. Mainline
sends the original batched commands synchronously one at a time; wire bytes,
packet types and explicit delays are preserved, but physical timing equivalence
is untested. See technical debtD07.

Future board wiring requires L12B fixed1.8V VDDIO, L13B fixed3.0V VCI, TLMM98
active-low reset, PM8550VE_F GPIO7 active-high VDDR, eight GPIOs on that PMIC,
and TLMM86 TE. This is a wiring requirement, not an enabled board description.

References are pinned in docs/oneplus13/NATIVE-DISPLAY.md. Packet provenance:
OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750 at
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3, production
dsi-panel-AA569-P-3-A0019-dsc-cmd.dtsi and its common.dtsi. Host fault-injection
tests do not access the phone or establish electrical correctness.
