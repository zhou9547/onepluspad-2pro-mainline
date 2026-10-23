# S3910 LBP candidate

## Scope, 2026-10-23

Stock Android evidence confirms active synaptics,tcm-spi-hbp on SPI 0xa90000,
19 MHz, IRQ TLMM162, reset TLMM161, VDD L4B at 1.8 V, AVDD enable PM8550VS_J
GPIO3. Android exposes touchpanel on that SPI child. This establishes the stock
wiring and active driver, not Linux input support.

Official syna_tcm2.c provides DC_CONTROL_LBP_HBP=0x11, value 2 for standard
REPORT_TOUCH=0x11. This is the candidate route; do not assume the device's
firmware accepts it until a separately authorized RAM test proves that.

The driver is a module. The default diagnostic DTB has no touch node. The
separate sm8750-oneplus-dodge-touch.dtb changes only the touch subsystem.
There is no auto-loader or hardware experiment in this repository.

## Implementation and checks

Use the attributed TouchCom v1/v2 protocol core, with a separate SPI wrapper.
Drive MOSI=0xff while reading, as the official driver does. Preserve probe
deferral for required supplies; never silently discard a missing regulator.
Use stock 200 ms power settling and 10/80 ms reset timings. The legacy vendor
GPIO property marks AVDD active-low but its driver deliberately uses raw GPIO
physical HIGH for power on; the new binding explicitly describes active-high.

The deeper runtime pinctrl children, cross-checked against the official dodge
overlay, specify 8 mA/bias-disabled IRQ and reset (reset starts physically low),
6 mA MISO/clock and 4 mA MOSI/chip-select. The initial compiled candidate used
generic 6 mA settings and an IRQ pull-up; those were rejected in the evidence
review and corrected before the final candidate. The stock runtime SPI configs
contain both inherited pull-down and overlay bias-disable properties; the new
tree uses the official phone overlay's intended bias-disable setting and still
requires physical electrical validation. Short SPI transfers return EIO rather
than pretending that all requested bytes were transferred.

Negotiate a fixed byte-aligned all-object report in RAM and read the descriptor
back before parsing any frames. Validate payload length, unique bounded slots,
coordinate bounds and classification. Report only fingers/gloves as fingers;
palms, hover and styli are released. The protocol command path runs with IRQs
masked outside the IRQ thread. Reset reports schedule work; they do not issue
synchronous commands or disable their own IRQ from inside its handler.

Panel followers start work after panel_enabled and quiesce before disabling.
Input, work, IRQ and power are unwound before the protocol core is released.
No firmware download, controller flash, raw SPI debug or factory-test interface
is provided. Touch axes use firmware geometry and generic orientation helpers;
the display compositor performs its normal normalized coordinate mapping.

Host parser vectors cover valid reordered contacts, lift, truncations, duplicate
and out-of-range slots, object limits and coordinate bounds. Actions also runs
the C vectors with ASan/UBSan. These are offline protocol checks only.

## Acceptance and remaining work

Build and inspect the actual module and its separate DTB. Then a future RAM-only
experiment must verify SPI responses, firmware mode, descriptor round trip,
physical single/multitouch, corner/orientation mapping and stock recovery.
The native panel remains separate work; only after its power lifecycle works
can the follower path and repeated display cycles be hardware accepted.

No hardware experiment is authorized in the current read-only session.
