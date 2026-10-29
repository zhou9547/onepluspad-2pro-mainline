# Isolated C-PHY framework candidate

The source-backed probe_intent match selects the phone's inferred L/S
three-trio C-PHY family; see [mode selection](CAMERA-MODE-SELECTION-20261029.md).
The existing four-lane D-PHY sensor mode cannot supply that stream.

The optional `camera-draft/build-components.py --cphy` now rebases Nihal Kumar
Gupta's six-message
[Qualcomm C-PHY RFC](https://lore.kernel.org/all/20261017-cphy_support-v1-0-8b0e1237ce95@oss.qualcomm.com/)
onto the existing exact kernel/component stack. Original messages, authors,
Signed-off-by lines and hashes remain in `camera-draft/cphy`; a separate
consolidated patch records the rebase. All eight pre/post source hashes are
checked before/after a zero-fuzz application. This is an independent component
build and is not applied by the normal phone kernel/image build.

The rebase adds C-PHY configuration options and CAMSS timing propagation,
endpoint mode/trio checks, generic PHY mode handling, trio lane masks and
rate-specific table selection. It preserves the staged Kaanapali/common-status
changes and the existing error propagation. Additional validation rejects
missing SoC tables before power-up, mode/lane mismatch, missing timing, rate
overflow, duplicated lanes, unsupported polarity, settle-register overflow and
rates above the last table. Legacy CAMSS remains D-PHY only. No X1E table is
assigned to the phone's C-PHY configuration.

`check-cphy-errors.py` extracts the actual staged CAMSS setup, PHY configure/
set-mode and settle functions into a hardware-free C harness. Its26 cases
cover D-PHY setup/errors, C-PHY timing propagation, missing tables, transmitter
errors, mode/count/rate/timing validation and arithmetic boundaries. Release
and ASan/UBSan executions pass. This tests the actual functions with synthetic
interfaces; it does not establish register programming or capture success.

A clean archive-based WSL AArch64 build with `W=1 KCFLAGS=-Werror` passed the
complete component builder, including CAMSS, PHY, CCI, S5KJN5, clock and amplifier
objects, disabled board DT and both synthetic suites. The full Linux offline
suite passes596 tests with5 environment skips. The manual **OnePlus13 camera
and speaker offline components** workflow now accepts boolean `cphy=true` for
the same native ARM64 build; new Actions verification is pending.

Remaining work is substantial: adapt the phone-specific public GPL CSIPHY
v2.3.0 dodge-ultrawide register sequences/rate tables, establish the sensor's
actual C-PHY mode and prepare/preamble timing, construct the exact disabled
board graph, and validate a real frame plus teardown and retained regressions.
The current framework deliberately has no phone C-PHY register table. It does
not install modules, add a capture pipeline, enable a device or request pixels.
