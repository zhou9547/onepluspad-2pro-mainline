# Source-only adaptation batch, 2026-10-29

The owner paused compilation and every form of testing after r67 was submitted.
This batch contains source/configuration edits only. No new compiler invocation,
test suite, emulator run, phone command or workflow dispatch is authorized by it.
The accepted hardware baseline remains r64; a source commit is not a new image
acceptance. The existing r67 artifacts, if completed, are not tested by this batch.

## Phone C-PHY adapter

The optional camera component path now has `--phone-cphy` alongside `--cphy`.
It installs a separate patch over the hash-bound staged C-PHY framework and
copies the new `dodge-cphy-mmio.h` plus the generated public GPL register catalog.
The normal phone kernel and DT do not select this adapter.

The source implements an explicit experimental compatible, bounded MMIO window,
three-trio validation, a heap-owned sequence plan, refgen polling, default CDR,
two-byte settle programming and the source-derived reset assertion/release.
The 3048-us release delay is retained. A mandatory interrupt is requested with
NO_AUTOEN; the receiver's eleven status/clear banks are handled before clocks
are removed. Failed lane setup now calls lane teardown while registers remain
accessible. The generic core also rejects power-on without successful configure.

The phone adapter selects a fixed 400 MHz timer and checks the rounded and actual
clock rate. Its core-clock minimum follows the downstream dodge-ultrawide
divisor32 branch and the rounded vendor 2.28 bandwidth unit, including the
strict integer boundary used by the downstream vote selector. It does not
reuse the generic link-frequency/4 calculation for this receiver.

The three core/timer/AHB clocks, domains and supply API are inherited from the
staged SM8750 generic provider. Exact board regulator votes, interconnects and
enabled graph remain unresolved. The new compatible is experimental, not an
upstream DT ABI. IRQ behavior, clock votes, failure rollback and this candidate's
compilability have not been tested. Existing generic synthetic code has only
been adjusted for the new configure hook; it is not coverage of physical MMIO.

Camera capture still lacks a selected L/S supplier initialization, a qualified
19.2 MHz three-trio sensor mode/timing, the complete PHY/CSID/CAMSS resource graph
and real pixels. The matching L/S mode sequences do not resolve their different
initialization sequences. No private sensor tables are published here.

## Infrared candidate

`infrared-draft/ir-dodge-spi.c` supplies the standard rc-core/LIRC transmitter
interface with a bounded 5 MHz, MSB-first sampled waveform. Carrier is restricted
to the public driver's 20–60 kHz range; the initial duty is one third, configurable
duty is limited to 50%, total duration to 500 ms and edge count to 1024. The input
duration array is not modified. A single SPI transfer avoids inserted gaps, and
controller transfer/message limits are checked before the supply is enabled.
An idle tail returns MOSI low.

The driver requires an explicit regulator phandle, exact 3.056 V support and
active/sleep pin states. It checks the voltage after enable, sleeps the pin after
transmission and releases the power vote. A failed disable prevents subsequent
transmission and retains the vote for cleanup. It never widens provider limits.

The separate disabled DTS fragment maps SPI5/MOSI53, selects only that pin,
keeps the I2C5 sibling disabled and leaves both controller and emitter disabled.
It is not included in the delivered phone board. The existing L9B maximum of
3.008 V conflicts with the stock 3.056 V request; all shared consumers must be
resolved before an enabled candidate can exist. GPIO electrical behavior,
actual SPI clock, optical output and protocols remain unverified.

`infrared-draft/prepare-source.py` stages the driver and Kconfig/Makefile in an
isolated kernel tree with pinned base/source hashes. `--infrared` on the camera
component builder includes its object in a future explicit component build.
No object was built in this batch.

## Video error and cleanup paths

The GStreamer helper now preserves bus errors at PLAYING failure and final
timeout as well as during polling. It emits a bounded pipeline-stop receipt even
after failed decoding. Private error text remains private. The outer helper
records that receipt and observes runtime suspend on a failed framework path,
before unloading Iris. The suspend wait is performed at most once; the original
guard/deadline is not renewed. Failure still cannot qualify hardware decode.

The r66 framework error's root cause remains unconfirmed because that run omitted
its bus message/debug text. The existing parsed-input correction and these error
path edits require a later combined run. They are not proof of player playback,
VA-API, multiple codecs or sustained decoding.

## Source preparation and future build placement

`camera-draft/build-components.py --prepare-only` returns after source staging,
before compiler/configuration/test commands. The catalog's `--emit-only` performs
source generation without launching a compiler or test executable. These modes
write explicit uncompiled/untested reports and do not create a boot image.

Both image workflows now accept `all_on_server`. It routes kernel, Mesa, SSC,
rootfs and image assembly to the existing trusted ARM64 runner label. The mixed
and GitHub-hosted modes remain available. Concurrent package installation uses
the shared apt locks. Same-run/same-commit artifact assembly is retained. This
new placement option has not been exercised and no workflow was dispatched.

## Remaining difficulties

| Area | What still prevents completion |
| --- | --- |
| Camera | Supplier-specific initialization and sensor timings; complete receiver/resource graph; frame capture |
| Speakers | Long-duration amplifier protection and absolute loudness; default activation remains unqualified |
| Orientation | Visible transitions across physical poses on the current image; fixed-pose readings cannot replace them |
| GStreamer / video | Missing original bus details and a successful framework frame; real player and multi-frame/codec behavior |
| GNSS / modem | Product firmware/resource/transport integration and modem recovery; location service availability |
| NFC | SN220T NCI/secure-element power ownership and native transport; a stock compatible label is insufficient |
| IR | Shared L9B constraint, exact electrical waveform and independent optical observation |
| USB-C / OTG | Role-provider/PD behavior and recovery after loss of the existing USB transport; real external peripherals |
| Suspend / power | Independent idle/suspend recovery, wake and charging/thermal policy; elapsed idle counters remain unresolved |
| Other phone services | Exact drivers, board mappings and separation of native services from Android-only dependencies |

These are unresolved engineering dependencies, not completed adaptations. The
source-only instruction does not make them verifiable without later evidence.
