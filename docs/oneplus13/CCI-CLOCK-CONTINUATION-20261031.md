# CCI clock and stretching backport, 2026-10-31

The r191 real-sensor attempt reported master 0 queue 0 timeout at ac7b000.cci,
followed by S5KJN5 register 0xfcfc write/init error -110. TPG data is not a
real sensor frame. This candidate addresses a supported CCI timing hypothesis;
it does not establish that the camera fault is resolved.

The pinned SM8750 CAMCC provides 37.5 MHz for CCI. Seven original upstream
changes are applied in order, retaining their authorship and review messages
in devices/oneplus13/kernel-patches/cci-upstream-source.json:

- d07c7775ca17: select v2 configuration for msm8953 (series prerequisite).
- e2ac856c7451: per-mode/per-rate timings.
- 04ec5e09518b: legacy 19.2 MHz v2 Standard/Fast timings.
- 826a1d134c3e: shared timing matrix.
- fa1eb3af12fa: enforce clock rate with OPP power votes.
- 0265dfc5d2a8: always enable SCL stretching (upstream S5KJN5 testing).
- ed404d9fd36b: reject rounded rates; explicitly covers SM8750.

The original Pad has no S5KJN5 integration. No other board calibration,
sensor register sequence, regulator, C-PHY or phone DT setting is substituted.
The patch changes only the CCI driver and its PM_OPP Kconfig dependency.
Full original messages and source/patch hashes are shipped as provenance.

check-cci.py compiles actual patched declarations, timing tables, cci_init,
cci_get_required_rate and cci_set_core_rate with GCC, ASan and UBSan. It exercises
SM8750's 37.5 MHz selection, rounded-19.2 rejection, all three bus modes,
SCL stretching MMIO, legacy 19.2 MHz timings, mixed-master rate selection,
unknown-rate failure and propagated OPP errors. This uses mocked clock/OPP/MMIO
interfaces and is offline C behavior evidence, not electrical validation.
Build failure is fatal. Packaging and verify.py bind the report to the kernel
pin, exact generated sources and upstream patch inventory. Regression tests
reject changed patch/source bytes and missing/stale artifact controls.

Next hardware round must combine camera with GNSS start/fix/stop, NFC controller
and USB observations plus preserved-feature regression. Human-dependent tag,
USB cable changes and orientation steps are skipped unattended, never passed.
Dual-band WiFi, including the historically accepted 5240 MHz link, remains a
preservation baseline. Exact-image runner review and the authorization window
remain prerequisites; compilation is OFFLINE_BUILD_ONLY.
