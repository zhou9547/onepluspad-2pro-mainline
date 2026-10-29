# Phone-specific C-PHY register catalog

An optional uncompiled phone MMIO adapter is now staged separately from this
previously checked catalog and planner. It adds fixed timer/core-clock selection,
IRQ handling and failed-start rollback; see
[source-only batch](SOURCE-ONLY-BATCH-20261029.md). The historical results below
apply to the original data/planner path, not the new adapter or camera capture.

The isolated `--cphy` component build now reviews the original public GPL-2.0-only
[dodge-ultrawide v2.3.0 table](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750/blob/d50b305f7da9e14715a25120a4ac7b1a4b8b97c3/vendor/qcom/opensource/camera-kernel/drivers/cam_sensor_module/cam_csiphy/include/cam_csiphy_2_3_0_hwreg_dodge_ultrawide.h).
The unmodified source retains Qualcomm's copyright/license; repository pin,
Git blob and SHA256 are recorded in `cphy/phone-tables-source.json`. This is
public driver data, not private module binaries or device calibration.

`cphy/review-phone-tables.py` verifies the exact source SHA256, parses only the
expected initializer grammar and checks29 increasing rate entries, eight equal
per-PHY references,36 registers per rate and the three-trio address layout.
Every rate has exactly three CDR, three settle-low and three settle-high entries.
Addresses must be aligned/in range, values fit8 bits and delays are bounded.
The common table has4 records and the three-phase base has72. The exact
three-phase reset release is0x1000=0x0e with3048us delay.

An important rate-unit difference must survive integration. Vendor thresholds
use symbol_rate*2.28, whereas the generic RFC uses the exact16/7 encoding ratio.
At every table's nominal upper boundary, comparing the exact converted rate
against the rounded vendor threshold would incorrectly advance a table, or
reject the final boundary. The catalog retains both values and selects by the
explicit symbol-rate upper bound instead. Sixty release and ASan/UBSan boundary
checks cover each exact upper limit, the next symbol, zero and maximum unsigned
input. An AArch64 object is compiled and its ELF machine checked.

A clean archive-based WSL component build with the catalog passes. Native
ARM64 [Actions40829917850](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40829917850)
also passed on3f2cdd5f with cphy=true. Generated headers,
object and verification report are saved with component artifacts. The catalog
is data only: no MMIO, compatible string, driver registration, phone DT change,
module installation or capture is added. The existing isolated framework still
rejects C-PHY configuration without a runtime SoC table.

Before using the data, reproduce the downstream common/rate/base/reset ordering,
reference-generator status polling, CDR/settle-high semantics and correct
interrupt offsets. Preserve the3048us reset delay and the phone's dedicated
common values. Do not substitute X1E or Kaanapali revision tables.

Separately reviewed GPL MediaTek S5KJN5 source declares three-trio C-PHY, but
its24MHz input and mode clocks differ from this phone's19.2MHz input. Its
0x011c value differs from the public D-PHY sensor mode. This is useful evidence
for further review, not permission to transplant another board's complete mode
or calibration. Sensor register/rate/prepare/preamble agreement and real pixels
remain required. Original proprietary C.93 sensor register tables stay private.

## Source-derived standalone sequence candidate

The isolated catalog now emits a reusable, bounded126-operation sequence plan.
It first polls0x1184 bit7 (500us interval,10ms timeout), updates the three-trio
lane mask0x2a at0x1014, then writes4 common,36 rate,72 base and11 interrupt
records. Reset release0x1000=0x0e is last and retains3048us delay. This order is
reviewed against the exact downstream START path and config helpers, recorded
with Git-blob/SHA256 provenance in `phone-sequence-sources.json`. The source
also places power/clock/CPAS work before this plan; those are not implemented
by the planner. Do not call the plan a complete power-on sequence.

The standalone C-PHY settle value is floor((prepare_ns + floor(preamble_ns/3))
*400MHz/1e9)-10, preserving the vendor's operation order. Both bytes are
substituted into each trio's rate settings. Zero/overflow, missing timings,
another timer, partial/combo trios and out-of-range symbol rates are rejected
before any callback. Normal CDR defaults and all per-register delays survive;
no sweep, auxiliary or diagnostic tuning is enabled.

The callback executor currently runs only on a fake register array. Tests
cover29 actual rate tables, settle790 with a nonzero high byte, default CDR,
lane-mask preservation,8 invalid inputs and injected failure at each of126
operations. Every error stops subsequent programming, including reset release.
Release and ASan/UBSan runs pass; the same code compiles into an AArch64 object.
No production MMIO callback, platform match, DT activation or camera capture
is added. Clock/rail ownership, full failure rollback, physical sensor timing,
CSID graph and real pixels remain required before runtime integration.
