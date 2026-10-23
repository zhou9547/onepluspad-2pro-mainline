# Isolated phone kernel patches

Apply to the exact platform commit recorded in ../source.json, currently
7a81d184e3098624d4342d8f4eff5e23674bcc9f. build.sh checks/applies them and exports
the resulting real kernel diff in phone-kernel.patch with the phone sources.
Existing Pad builds never apply this directory.
The kernel release also carries the exported phone patch digest, so a changed
DSI/touch/board implementation cannot silently reuse the previous vermagic.

0001 selects the existing native422 DSC RC table, keeps RGB conversion disabled,
uses group bpp only for DRM RC arithmetic, and restores physical-pixel bpp for
MSM bandwidth/timing and the DPU API. The shared RGB route is unchanged. It does
not implement native420, a panel, SPR, REGDMA or physical display acceptance.

check-display.py compiles the real patched functions with the original DRM
helpers, tables and structure. It reconstructs the complete public AA569 PPS
from minimal geometry/format, compares all128 bytes, rejects the unmodified
baseline and wrong-bpp controls, preserves the RGB result and rejects invalid
native422 inputs. CI uses ASan/UBSan and builds the real ARM64 module afterward.

The patch modifies GPL-2.0-only Linux MSM DSI code from the pinned kernel;
original copyright and licensing remain with that file. Authorship of this
adaptation is Codex; there is no hardware Tested-by claim.

0002 uses an explicit panel HS ceiling for native422 command bursts on one
D-PHY link. Byte, pixel and PHY requests share the same source; rates round
down to whole byte clocks and over-budget modes are rejected in mode_valid.
Six legacy/video/C-PHY/bonded/RGB/uncompressed controls retain their original
results. check-command-clock.py compiles the real functions, including the PHY
request, and rejects ten invalid inputs. This is a clock request correction,
not a complete implementation of the vendor DPU transfer window or SPR.

0003 corrects native422 initial-line arithmetic (half-width containers and
128-bit output buffer), marks SM8750 full ICH precision capability, clears the
legacy wrapper bit only for modern native422 DSC and restores PPB FIFO sizes
on enable/runtime resume. Older wrapper ranges are not accessed out of bounds.
The physical-bpp API and existing hardware bpp conversion remain unchanged.
The existing DSI STREAM0_TOTAL matches the public vendor wide-bus arithmetic;
the unrelated community stream-width doubling is deliberately omitted.

References: EYC's GPLv2 TB323FU/kaanapali DSC fixes in
joonhoekim/tb323fu-linux at da44c8412fed3baa609a8084a214ae9b5c9f4311,
and OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750 at
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3, especially sde_encoder_dce.c,
sde_hw_dsc_1_2.c and sde_hw_pingpong.c. check-dpu.py compares real patched C
against an unmodified, attributed vendor initial-line function, checks 96 math
cases, captures register writes, preserves a legacy RGB control and checks PPB
replay and runtime-PM call integration. These are host checks, not register
readback or a physical display test. No SPR or board display node is added.


0004 connects the explicit static AA569 SPR backend to probe, atomic resource
checks/flush and PM restore/disable. It adds SM8750 SPR sub-blocks with correct
stock-to-upstream base conversion, preserves DSPP without color properties and
rejects unsupported display formats. All-pipe preflight, idle/clocks guards
and reset error propagation are tested in real C. CPU writes are restricted
to quiet probe/PM boundaries; this patch implements no REGDMA or dynamic UDC.
There is no private profile in Git/Actions. Default/touch DTBs have no opt-in.
Source/provenance, scope and removal conditions are recorded under spr-aa569
and docs/oneplus13/TECHNICAL-DEBT.md D10.

0005 adds qcom,sm8750-mdss to qcom_smmu_client_of_match's existing display
identity-domain list, preserving firmware scanout until explicit MSM takeover.
This follows the pinned driver's SM8250 and X1E client pattern; it does not
change the separate prefetch table (which already contains SM8750). GPL-2.0-only
pinned arm-smmu-qcom.c licensing remains intact. The native DTB is opt-in only;
default/touch DTBs keep MDSS disabled. Handoff is not hardware tested.

0006 conservatively budgets the isolated static AA569120Hz path for the stock
6800us burst instead of the whole frame interval. Existing plane/prefill votes
are multiplied by125/102 with ceiling rounding. New-state bandwidth and maximum
OPP are checked before generic old-state aggregation; overflowing requests fail.
Per-path ICC average rounds up, peak covers the aggregate average, missing paths
and ICC failures propagate. Non-opt-in results are compared with the original
three performance modes. The ratio comes from the pinned public AA569 mode and
vendor dsi_panel.c forwarding semantics, not an exact proprietary HAL formula.
TE/timer registers are unchanged and actual burst completion remains untested.
check-command-budget.py executes actual C arithmetic/check/ICC functions with
261 independently generated integer expectations, five overflow/limit controls,
fresh-enable negative baseline, two ICC failure positions and legacy controls.
