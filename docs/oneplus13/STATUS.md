# Fixed single-primary camera profile, 2026-10-31

r213 Actions 41193964798 passed all five jobs. Three archive digests, 66
runtime files, 120 firmware files, 18 native dependencies and the actual OTG
driver/header patch were independently read back. Native read-only lock and
AFW markers are present. This image has not been hardware tested; r211 remains
the last combined hardware record. GNSS fix and physical USB I/O remain open.

The camera helper now offers explicit single-primary capture: one fixed RDI0
stream, one bounded graph sweep, exact 15-module closure and policy binding,
no retry/bind/RDI/TPG alternatives or test-pattern change. Work/cleanup/output
alarms are separate 660/330/30-second ceilings. Cleanup expiry retains a failed
receipt, failed topology reads cannot prove removal, and occupied trace probes
refuse streaming. The default full diagnostic path remains available.
See CAMERA-SINGLE-PRIMARY-20261031.md. These are source/offline lifecycle fixes,
not real-frame acceptance. No phone operation or authorization renewal follows.

# r211 hardware result and OTG identity correction, 2026-10-31

r211 Actions 41191715898 passed all five hosted jobs and exact image readback.
The combined RAM round completed in 93.22 seconds, returned to Android with
seven baselines matching, and made zero partition writes. All executed private
command evidence verifies. Camera chip-ID, 5 GHz control and MPSS pass. GNSS
START remains GeneralError (46), but acknowledged STOP is now correctly clean
and the independent USB phase continued. Read-only LOC reports engine lock=all
and standalone mode; no lock/mode SET was attempted. NFC is owner-skipped.
See R211-HARDWARE-RESULT-20261031.json. GNSS fix, real frames and USB I/O remain open.

The optional OTG patch used only compiled oneplus,dodge compatibility, while
the existing physical-platform/SPR code documents ABL replacing it with the
exact physical dodge model and qcom,sun. The correction reuses the existing
strict SPR model/chassis/compatible predicate for visibility, reads and late
reply filtering. Generic Sun and other boards remain rejected. The USB helper
now separates absent device/attributes, read error, timeout and invalid values.
No setters or power policy changes are added. This source correction still
requires Actions and new hardware observation; it does not establish OTG I/O.

The same milestone adds a read-only native --get-engine-lock diagnostic for
the primary IDL engine state/client masks, with strict response/indication
validation and no SET. Missing native helper now fails closed; the obsolete
multi-process fallback with implicit unlock is removed. See
GNSS-ENGINE-LOCK-20261031.md. This diagnostic still needs hardware observation.

# r210 hardware and rejected-start cleanup correction, 2026-10-31

r210 Actions 41190113030 passed all five hosted jobs and exact archive/image
readback. Its combined RAM test returned to Android after 92.22 seconds with
seven baseline properties unchanged, one boot and zero partition writes.
Camera chip-ID, 5 GHz control and MPSS checks passed. AFW registration now
passes; LOC START returns GeneralError (46), followed by an acknowledged STOP.
No satellite fix or GNSS engine acceptance is claimed. The collector incorrectly
treated the native functional-failure exit code as failed cleanup and halted
before USB observation. The next candidate recognizes only this exact rejected
START plus one valid STOP acknowledgement as clean while preserving GNSS failure;
timeout, crash, conflicting markers and STOP errors remain unsafe. See
GNSS-START-STOP-RESULT-20261031.md. NFC is owner-skipped; real frames and USB
physical I/O remain open. The r210 ledger is consumed and must not be reused.

# OTG kernel API build correction, 2026-10-31

The r209 hosted kernel build exposed a missing linux/of.h include and use of
an unavailable plural devm_device_add_groups API. The read-only patch now
includes the OF declaration and registers its single attribute group with
devm_device_add_group. No firmware protocol, role policy or write capability
changes. r209 did not produce a qualified image or a new phone boot; the
corrected candidate must complete Actions and exact image readback first.

# LOC registration client identity candidate, 2026-10-31

The upstream libqmi client-identification addition matches the clean
pre-start InvalidArgument failure. The Linux system provider now registers
fixed AFW=1 and its own OP13 string through stable raw QmiMessage APIs,
preserving the installed library ABI, same client/endpoint, bounded fallback
and strict start/fix/stop acceptance. No privileged mode or identity scan is
used. See GNSS-CLIENT-IDENTITY-20261031.md. Combine this candidate with the
read-only USB gate observation after exact Actions/image qualification.
r208 Mesa compiled but artifact upload hit ECONNRESET; it is not a qualified
complete image and no phone boot uses it.

# r207b physical evidence and USB firmware reads, 2026-10-31

The r207b combined round completed in 288.55 seconds, returned to Android
with all seven baseline properties matching, and made zero partition writes.
5 GHz control, modem preservation and S5KJN5 chip-ID pass; real frames,
GNSS start/fix/stop and USB physical I/O remain open. NFC is owner-skipped.
USB xHCI/root hubs were confirmed before swapping, then UCSI reverted to
device/sink on detach and no OTG partner appeared. The next candidate adds
phone-only read-only firmware gate observation, without setters or blind
protocol fallback. See USB-OTG-FIRMWARE-READS-20261031.md. This candidate
requires its own Actions image qualification and reviewed joint RAM plan.

# CCI source-byte correction and camera deadline, 2026-10-31

r201 Actions rejected generated CCI reference hashes because Windows Git wrote
CRLF where Linux Git emits LF. Inventory now pins the actual Linux bytes and
checks reverse-patch/base-hash/forward-patch/generated-hash roundtrips. No hash
normalization or CCI logic change hides a mismatch.

Independent combined-runner review also found incomplete camera time accounting.
The installed helper now shares a 1500-second work deadline across discovery,
configuration and all fallbacks, with a separate 1150-second cleanup deadline
and 45-second output deadline. Media scans accept at most eight nodes; stream
termination is bounded and trace ownership survives asynchronous interruption.
The Linux full repository suite passes 775 tests with five skips. This is
offline qualification only; final Actions/image and exact-plan review are pending.
GNSS fix/start/stop, NFC tag, real frames and physical USB I/O remain open.

# CCI upstream clock and stretching candidate, 2026-10-31

The camera candidate backports seven upstream CCI clock/timing/stretching
changes, including exact-rate selection for SM8750's 37.5 MHz clock.
Actual patched C functions pass GCC ASan/UBSan offline controls, and image
verification binds their report to the patch, generated sources and kernel pin.
No real sensor-frame acceptance is claimed. See CCI-CLOCK-CONTINUATION-20261031.md.
GNSS/NFC/camera/USB remain joint targets; dual-band WiFi is a preserved baseline.
Current bounded Android preflight succeeds with seven baseline keys matched;
this is a read-only observation, not a new RAM test or hardware acceptance.

# Camera insertion cleanup ownership, 2026-10-31

A module insertion timeout or error may leave a registered camera module.
Capture now records ownership before insertion, so cleanup still attempts that
module; preexisting modules remain unowned. All 26 camera regressions pass.
The full Linux repository suite passes 759 tests with five skips.
No sensor registers, CCI timing, C-PHY settings or firmware were changed.
This does not resolve the observed CCI -110 or establish real-frame success.
USB and documented network ADB preflights were unavailable in the current
session; no new RAM boot occurred. Dual-band WiFi remains a preserved baseline.

# GNSS bounded stop lifecycle, 2026-10-31

The native LOC client now owns one stop request, removes its collection timer,
waits for a pending start response before cleanup, and attempts stop after lost
or failed start replies. Python reserves the full bounded cleanup time and
retains lifecycle markers across long NMEA streams. See GNSS-STOP-LIFECYCLE-20261031.md.
No new phone operation or hardware acceptance occurred; GNSS/NFC/camera/USB
remain open and dual-band WiFi remains a preservation baseline.

# Camera cleanup and sensor fallback correctness, 2026-10-31

The combined unattended audit reproduces unsafe global kprobe-table rewrites,
silent function-tracer restoration failures and rejection of validated RDI
sensor fallback frames. These paths now preserve probe ownership, report
cleanup failures, continue teardown after a module timeout, and accept a
validated real sensor fallback without ever counting TPG pixels as real.
The 23 camera tests pass on Linux. This does not resolve the r191 CCI -110
or establish hardware success. See CAMERA-CLEANUP-FALLBACK-20261031.md.
Dual-band WiFi remains a preservation baseline. No phone boot has started.

# Installed desktop regression helper, 2026-10-31

5 GHz WiFi is already accepted historically, including r191's 5240 MHz
control link. Both bands remain preservation/regression baselines; the open
joint hardware goals are GNSS fix/start/stop, NFC tag, real camera frames and
USB peripheral enumeration/read-only I/O.

r195 public commit e0bb84b331e8b33781236343cd2e8a7a8b725265 completed all
five Actions 41159270428 jobs. Three archive digests, 66 installed runtime
files and the native GNSS dependencies were independently read back. This
is offline image qualification, not new hardware acceptance.

Joint-runner review found that the installed desktop checker still resolved
the source filename automatic-wifi-check.py although image packaging installs
oneplus13-automatic-wifi-check.py. It now selects its exact sibling according
to its own packaged/source name and refuses an unprefixed overlay fallback
in the image. Three tests cover installed loading, missing installed helper
and source use. WSL full repository suite: 745 tests, five skips; phone suite:
587 tests, one skip. Windows cannot run the Linux-wide suite and is not used
as its acceptance environment. See DESKTOP-REGRESSION-CONTINUATION-20261031.md.

# Camera trace correction and completed NFC build, 2026-10-31

Actions 41158155405 completed all five jobs successfully for r194 public
commit ecb66a3655ed0d823cee09ce06d730992d2b45e2. NFC helper fixes are
offline-qualified only; no new physical round or RF acceptance occurred.

The camera trace start/stop test reproduces KeyError('mode') in the kprobe
branch, before the helper can save stream-attempt diagnostics or try RDI/TPG
fallback. The state now records its mode. Linux kprobe events are disabled
on creation, so the helper explicitly enables them, disables and selectively
deletes its own events, and reports cleanup failures. Existing reserved
camera probes are not taken over; unrelated probes are not rewritten.
Six new regression cases cover lifecycle, ownership, partial failure and
the function-tracer fallback. All 584 offline tests pass (one skip).
This fixes a diagnostic/control-flow defect, not the observed CCI -110.
See CAMERA-TRACE-CONTINUATION-20261031.md. Dual-band WiFi remains accepted
historically and is included only in preservation/regression.

# Accepted WiFi baseline and remaining joint targets, 2026-10-31

The owner clarifies that 5 GHz is already working: r191's 5240 MHz control
channel remains accepted. Both bands are preservation/regression targets.
Actions 41156920220 completed all five source/image jobs for public commit
9727c0c2204fa210a9aa8fe418b719f473a415d6. Its WiFi changes improve delivery
and isolate sensor failures; they do not reopen RF adaptation.

The next NFC candidate corrects the RF-wait timer and preserves multicast
events received alongside request replies. Cleanup now requires bounded
STOP/DOWN responses and power-off readback of the selected controller; failures
can no longer pass. The polling helper is delivered and source/hash-verified
in the complete image, without automatic RF polling. See
NFC-JOINT-CONTINUATION-20261031.md. No new hardware acceptance is claimed.

# WiFi delivery and joint continuation, 2026-10-31

The current owner request resumes adaptation/builds with 5 GHz priority and
combined hardware rounds. Historical 5240 MHz acceptance and the successful
Actions41100212379 baseline are retained. The new candidate removes the
accelerometer-service dependency from `qualified-bringup --wifi` while
preserving ADSP startup and keeping all sensor steps in `--all`. The installed
WiFi CLI now owns its kernel-history guard, and final SquashFS verification
binds all ten runtime files to current source. USB reads now exclude phone
UFS, bound entry count and bytes, reject links/FIFOs, and cannot mistake the
builtin touchscreen for tested USB HID I/O. Type-C/ADSP observations and the
GNSS duration correction are included in the same source milestone.
See WIFI-JOINT-CONTINUATION-20261031.md. No new phone round has started;
GNSS, physical NFC, real camera frames and USB peripheral I/O remain open.

# r191 hardware evidence and next GNSS candidate, 2026-10-31

Actions run 41094911835 built `ab41d005` successfully in all five jobs.
Independent readback verified three GitHub archive digests, 37 image files,
44 kernel files, 55 runtime files, 120 qualified firmware files, and the
native ARM64 LOC client's 18-library dependency closure. The owner approved
one combined RAM round with a real NFC tag and confirmed physical USB dock
attachment. It completed and returned Android with all seven baseline
properties matching, one boot, and zero partition writes.

The 5240 MHz Wi-Fi receipt/control channel, running MPSS and 48 firmware
files, RMTFS UIO, IR transmit syscall, one s2idle cycle and two deep cycles
passed. NFC event subscription is now true, confirming the userspace fix,
but no physical target was found. USB role and xHCI startup/restoration passed,
yet the attached dock/U disk produced no peripheral across 240 samples in
120 seconds. ADSP was offline in the initial inventory; Type-C/CC/VBUS
dependencies remain an investigation, not an established diagnosis.

The native GNSS client reached LOC but Set NMEA Types returned QMI error 94
NotSupported before start. The next source candidate tolerates only that
specific protocol error for this optional configuration and continues with
the modem's default sentences. Registration, start, real checked NMEA fix,
and stop are still required. Other protocol and transport errors remain fatal.
The same C source compiles with -Wall -Wextra -Werror on the Linux host;
four no-QRTR capability-policy checks and eleven Python GNSS tests pass.

Camera still received no real frame. The common TPG path produced a verified
15,728,640-byte varied frame, but the real sensor path also logged CCI queue
timeout, init-register error -110 and V4L2 stream warnings. The next camera
analysis must include sensor/CCI initialization rather than assuming a pure
C-PHY receive problem. Cleanup passed; no panic/IOMMU/CPU-stall health event
was recorded. Allowlisted evidence: `evidence/r191-runtime-20261031.json`.

The owner now requests finishing this source round, committing, compiling,
updating the complete private local archive, and shutting down the computer
once. No further phone test is requested before the next chat and approval.

# NFC multicast subscription correction, 2026-10-31

Resume review found an additional userspace fault behind r188's
`event_multicast_subscribed=false`: the generic-netlink controller serializes
both multicast-group containers with `nla_nest_start_noflag()`, while the poll
helper rejected containers without `NLA_F_NESTED`. It also referenced socket
option constants absent from the available Ubuntu Python build. The parser
now uses the known nlctrl schema for either flag encoding and supplies the
Linux UAPI values for subscription. Regression tests reproduce both failures
and pass after correction. A physical NFC target remains unqualified; the
previous event absence cannot by itself isolate an RF or power fault.

Primary source: Linux `net/netlink/genetlink.c`, `ctrl_fill_info()`:
https://github.com/torvalds/linux/blob/master/net/netlink/genetlink.c

# Native GNSS entry-point correction, 2026-10-31

Actions run 41090987923 built the single-client LOC candidate at `0477f68f`
successfully in all five jobs. Resume review found that the Python entry point
uses `os.access()` without importing `os`, then attempts to encode a Path
object into JSON, so that candidate must not be used for hardware acceptance.
A new entry-point test reproduces both failures; importing `os` and converting
the helper path to a string makes all ten GNSS tests pass. The test exercises native
client selection, checked NMEA, stop/cleanup, and the emitted result without
opening QRTR or touching the phone. A fresh source-bound image and explicit
owner start confirmation remain required before the next combined RAM round.

# r188 single-client LOC helper and physical USB evidence, 2026-10-31

The `4ad0ae4a` Actions image completed a combined RAM round and returned
Android with all seven baseline properties unchanged and zero partition
writes. Wi-Fi associated on channel 5240 MHz, the temporary Wi-Fi receipt
channel was independently challenged and acknowledged, MPSS retained all 48
reviewed files with IPCRTR, and the IR control path, one s2idle cycle, two RTC
woken deep cycles, and DWC3 host-role readback/restore all passed.

The physical USB-C dock and U disk were attached during the DWC3 host-role
test. The controller and xHCI host initialized, but no downstream peripheral
or storage/HID driver appeared during the complete 120-second bounded wait.
The role cleanup and device-role restore still passed. This is a real USB host
data-path failure, not a missing operator step.

The NFC controller bound, powered up, and returned to the down state, but the
presented tag produced no NCI target event. Camera capture forced the sensor's
`Solid Color` test pattern and read back value 1 successfully, yet real CSID
data still did not arrive; the same graph produced a complete varied TPG frame.
The remaining camera fault is therefore at the sensor/C-PHY transmit boundary.

QMI LOC operation mode was readable as `standalone`, but retaining a direct
QRTR client across separate qmicli processes failed with an unknown client,
and the qmi-proxy variant timed out on every subsequent request. Source now
contains a native libqmi client that configures GGA/RMC, registers NMEA,
starts, follows, stops, and tears down in one process. A real fix remains
required before GNSS is accepted.

# r184 LOC-session preparation and combined runtime evidence, 2026-10-30

Actions run 41068800412 built commit `c48a2648` successfully in all five
jobs. Independent download verification matched the three GitHub artifact
digests, all 37 complete-image checksums, all 44 kernel checksums, the kernel
module release, and the packaged GNSS helper provenance.

The combined RAM round completed every scheduled stage and returned Android
with all seven baseline properties matching and zero partition writes. Wi-Fi
associated on 5 GHz at 5240 MHz and -19 dBm. MPSS remained running with all
48 reviewed firmware files and the IPCRTR control plane, and the host helper
reused that live session without a remoteproc cycle. The IR LIRC transmit call,
one s2idle cycle, two RTC-woken deep cycles, and DWC3
`device -> host -> device` role restoration all passed.

The QRTR `loc` service answered and reported standalone operation mode, but
the first LOC start returned QMI `GeneralError`. The helper now keeps one
client across setup, NMEA configuration, engine-lock selection, start, follow
and stop, with bounded start retries. A valid NMEA fix and clean stop remain
required.

NFC binding and `nfc0` power transitions passed, but the physical tag was not
attached, so no target event occurred. The USB host controller role switched
and restored, but the cable remained connected to the computer and no U disk
or mouse was attached, so the empty inventory is not a USB-host failure. These
two items require the owner confirmation card at the corresponding physical
step.

The camera graph again produced a complete varied TPG frame, proving CSID and
VFE data capture, but the real S5KJN5 path produced no frame after the complete
vendor output-selector sequence. CSID1 recorded an interrupt while the capture
attempt timed out. Real varied RAW10 pixels and teardown remain open.

# r182 RMTFS udev binding and combined runtime evidence, 2026-10-30

Actions run 41050325340 built commit `6e9911d6` successfully in all five
jobs. Independent download verification matched all 37 runtime files, the
kernel module set, the four-cell RMTFS DTB resource, and the revised S5KJN5
source hash.

The combined RAM boot then reached `msm_sharedmem_probe: Device created for
client 'rmtfs'` and created `/sys/class/uio/uio0`. The udev symlink was absent
because the rule matched `ENV{UIO_NAME}` while the UIO class exposes the name
as the `name` attribute. The rule now matches `ATTR{name}`, and an rmtfs
drop-in waits up to 20 seconds for `/dev/qcom_rmtfs_uio1` before starting.

The same run reconfirmed 5 GHz at 5240 MHz and -17 dBm, MPSS startup with all
48 firmware files, clean MPSS stop, NFC controller binding, IR transmit
acceptance, and s2idle plus two deep suspend cycles with RTC wake. GNSS still
failed before a LOC session because the userspace RMTFS device was missing.
Camera still received no real CSID packets even after fixing the output
selector's register-page order; TPG again produced a complete varied frame.
The NFC tag poll returned `-121`, and the USB test was not valid because the
operator cable swap prompt was missed. Those three physical checks remain
open.

Offline decoding of the phone's L sensor-module blob resolved the complete
normal mode sequence as three entries under page `0x4000`:
`0x0b30 = 0x0102` and `0x0264 = 0x0606` in addition to the page selector.
The previous candidate supplied only the first output value. Source now adds
the full three-register sequence; it remains a candidate until real CSID
packets and varied RAW10 pixels arrive.

The live NFC poll reached the NCI start path but the controller's first read
returned `-121`. A stock-board comparison found that the candidate also
misconfigured the pinctrl state: the IRQ line was pulled up instead of down,
and GPIO35 was absent from both active and sleep states. The node also omitted
`clock-frequency`, so the GENI driver selected its 100 kHz default instead of
the vendor's 400 kHz bus rate. Source now matches the stock GPIO states and
sets 400 kHz explicitly. Tag discovery remains unqualified until the next
combined image receives an NCI target event.

# r181 RMTFS cell-layout repair, 2026-10-30

The exact `2b01837b` Actions image completed one temporary RAM boot. The
5 GHz path returned on 5240 MHz, MPSS reached running and verified all 48
installed firmware files. The first runtime GNSS candidate did not publish a
usable fix because `msm_sharedmem` loaded but did not create a UIO device.

Kernel evidence identifies the fault before SCM or LOC: the original
`qcom,sharedmem-uio` node used `<address size>` in a one-cell vendor parent,
while the merged `/soc@0` parent declares two address and two size cells.
Copying the two-cell property left the memory resource without a translated
size, so probe exited with `resource not found`. The DTB derivation now emits
the equivalent four-cell `<0 0 0 0x400000>` property, preserving address zero
and the reviewed 4 MiB dynamic allocation. Targeted modem, combined camera,
and IR/USB DTB tests pass.

The host orchestration stopped after the operator requested an interactive
checkpoint before physical actions. The guest worker had already entered its
hardware sequence and completed the remaining automatic probes before
rebooting to Android. Five GHz Wi-Fi, MPSS startup/stop, controller binding,
and three RTC-woken suspend cycles passed. GNSS, real camera pixels, NFC tag
discovery, and USB peripheral I/O did not. A new source-bound Actions image
and an operator-gated combined round remain required.

The same run showed that the sensor accepted initialization and stream
commands but produced no CSID packets; the previously verified TPG path still
reached the VFE. Vendor tracing shows `0x0b30 = 0x0102` is written after
entering register page `0x4000`. The candidate had been writing it before the
page switch, so it could not select the intended sensor output format. The
patched mode table now preserves the vendor order. This remains a candidate
until a varied real RAW10 frame arrives over CSIPHY1.

# r180 MPSS RMTFS shared-memory candidate, 2026-10-30

The previous GNSS result was not an NMEA failure: the QRTR registry had no LOC
service, so qmicli returned `Internal` before a session could start. The stock
vendor_boot DTBs contain `qcom,rmtfs_sharedmem@0`, while the manual MPSS trees
did not. The source now adds that exact node (`qcom,sharedmem-uio`, client 1,
4 MiB), the public LineageOS/OnePlusOSS `msm_sharedmem` driver, and the udev
link expected by `rmtfs` (`/dev/qcom_rmtfs_uio1`). No new reserved-memory region
or `/dev/mem` fallback is added.

The driver uses the current qcom_scm and UIO APIs, keeps the original CMA and
VMID assignments, restores HLOS permissions before teardown, and frees dynamic
CMA on remove and failed UIO registration. The ARM64 module compiles against
the exact kernel build on the trusted server. DTB and source tests cover the
new node, the public blob provenance and the device-link build inputs. This is
still a build-qualified candidate: LOC service publication, an actual NMEA fix
and complete MPSS/modem functionality require a later combined RAM test.

# r178/r179 camera receive follow-up, 2026-10-30

The stock normal-preview C-PHY table selects output selector `0x0b30 = 0x0102`;
the two-exposure variant uses `0x0103`. The source now carries the normal-preview
selector as a bounded candidate, with its generated sensor source and patch hash
updated. r178 retained NFC binding, infrared transmit, USB role switching and
one s2idle plus two RTC-woken deep-suspend cycles, and returned to Android with
all seven baseline properties unchanged. It still produced no real sensor frame,
so the selector is not presented as a camera fix.

A separate r179 diagnostic PHY attempted to sample 24 lane-status groups from
its IRQ handler. The node maps `0x2000` bytes, but indices six and above exceed
that mapping. The session stopped responding and the diagnostic candidate was
withdrawn. No such register-range expansion or IRQ sampling block is included
in the product source. Further receive work must use existing bounded logs or
explicitly reviewed address-range mappings before another combined RAM test.
Camera, physical NFC-tag detection, optical IR receipt, physical USB peripheral
I/O, GNSS fix and modem qualification remain open.

# r177 C-PHY receive boundary and live sensor frame proof, 2026-10-30

The current candidate was exercised in four bounded combined RAM sessions. Each
returned to Android with all seven baseline properties matching and no partition
writes. NFC controller binding, infrared LIRC transmit, DWC3
`device -> host -> device`, and one s2idle plus two RTC-woken deep-suspend cycles
were included in the same sessions.

Camera topology now reaches a single immutable path through
`S5KJN5 -> CSIPHY1 -> CSID1 -> VFE1/RDI0 -> video3`. The same CSID/VFE capture
node produced a complete 15,728,640-byte TPG frame, so camera negotiation, V4L2
buffers, CSID1, VFE1 and the downstream video path are functioning. The
400 MHz CSIPHY operating point was required before the generic PHY stream could
start.

The live S5KJN5 CCI initialization and mode write complete, and its frame-count
register advances while the PHY reports interrupts. This proves that the sensor
is producing internal frames. However, CSID1 receives no packet or frame
interrupt and VFE1 remains at zero, so real pixels are not yet qualified.

Stock C.93 camera logs and debugfs were compared at the same point:

- stock and mainline both select CPHY1, CSID1, lane assignment `0x210`,
  lane-enable `0x2a`, settle count 45, and the 6,384,000,000 bps PHY table;
- the mainline plan statically matches the stock v2.3.0 register image;
- the mainline lane-control value reads `0x1014 = 0x2a` after the plan, matching
  stock; and
- stock trios after streaming report `0x0, 0x5, 0x5`, while the current
  mainline capture reports `0x0, 0x10, 0x0`.

The remaining fault is therefore at the boundary between the sensor's selected
three-trio output format and CSID1 receive/decode. The helper now keeps the
sensor test pattern off by default, records controls and short summaries,
attempts RDI0/RDI1/RDI2 mappings, preserves a verified TPG fallback, and can
load exact-build diagnostic CAMSS, PHY and sensor modules only from the
session-local `/run/oneplus13/core` directory.

This is substantial runtime evidence but not camera acceptance. Camera remains
manual and default-off until a real frame is verified and the retained combined
hardware matrix still passes on the exact source-bound image.

# r81 bounded GNSS sessions and shared-module preservation, 2026-10-30

# r82 exact target runtime boundaries, 2026-10-30

The exact `49931bcc` image completed one bounded combined RAM boot and returned
to Android with all seven baseline properties matching and zero partition
writes. NFC controller binding and `nfc0` power-up/down passed; no physical tag
was present. The infrared module and rc-core device loaded, but the kernel had
`CONFIG_LIRC` disabled, so `/dev/lirc0` could not exist. The config now enables
the LIRC character-device layer before the next real transmission test.

The MPSS remained running and exposed the expected `IPCRTR` and rpmsg service
router endpoints. No GNSS attempt ran because the host verification command
imported the standalone helper as a Python module; the helper now has a
dedicated firmware and control-plane `verify` mode.

The DWC3 role helper searched only for `dwc3*` debugfs directories. The platform
device is named `a600000.usb`, so the attempted role switch stopped before
writing a role. The helper now searches the platform-specific and standard DWC3
locations and rejects ambiguous matches.

An RTC-woken deep suspend request returned to Android before the helper could
write a post-resume receipt. This is a failed deep-suspend acceptance, not a
source-test pass. A later round will select s2idle explicitly for a bounded
suspend check and preserve deep-suspend recovery work as an open item.

# r83 exact combined image runtime and suspend pass, 2026-10-30

The exact `84a75f4edb6e` Actions image completed a bounded combined RAM boot
and returned Android with all seven baseline properties matching and zero
partition writes. The MPSS reached running with verified firmware, GLINK
`IPCRTR` and the service-router endpoint, then stopped cleanly to offline.
NFC bound `1-0028` to `nxp-nci_i2c`; `nfc0` powered up and down, but no physical
tag event was available.

USB role control found `/sys/kernel/debug/usb/a600000.usb/mode`, read back
`host`, enumerated the host controller, restored `device`, and re-registered
the UDC. No physical USB-C peripheral was attached, so host I/O remains open.

One RTC-woken s2idle cycle entered suspend and resumed after 14.817 seconds of
actual suspend time (`BOOTTIME - MONOTONIC`), then disarmed the 32-second
Gunyah watchdog and cleared its wake alarm. This is a real s2idle pass.
That run also completed two repeated deep cycles of 12.721 and 12.700 seconds,
both with successful RTC wake and watchdog cleanup. Deep idle, long-term power
and charger policy remain open.

The camera helper loaded its bounded module closure and cleaned it up without
kernel-health faults, but CAMSS did not create a media device, so no sensor
frame was attempted. The IR driver and LIRC interface both appeared at
`/dev/lirc0`, but transmission was rejected because GPIO53 was requested by
both the SPI controller and child device. The child pinctrl duplication is now
removed. GNSS reached QRTR node requests but the `loc` service returned
`Internal` immediately after MPSS startup; the next helper waits for service
publication before classifying the result. The camera follow-up showed all six
CSI PHY drivers reporting `Missing port@0`; the graph endpoints now carry
endpoint IDs and reciprocal sensor links instead of relying on parser defaults.
A later exact-image run removed the PHY probe failures and exposed the remaining
parser mismatch: the sensor endpoint used media-bus value6 instead of the
firmware-property C-PHY value1. Source now uses value1, defers every camera
provider until the reviewed RAM loader has set up CAMCC, and enables the
Qualcomm `rmtfs` and `tqftpserv` userspace services for modem initialization.

Additional camera review against the pinned kernel's `camss-vfe.c` found that
the RDI subdevice is `msm_vfe1_rdi0` and its separate capture entity is
`msm_vfe1_video0`. The former `msm_vfe1` topology fixture was incorrect.
`vfe_formats_rdi_845` maps SGBRG10_1X10 to packed SGBRG10P (`pGAA`), requiring
15,728,640 bytes for 4096x3072 rather than the unpacked two-byte layout. The
helper now selects the actual entities, verifies the negotiated dimensions and
FourCC, and retains topology output when graph discovery fails. This is source
review and offline verification, not proof that the sensor produces a frame.

USB role-switch acceptance now requires a readback of `host` after the transition,
as well as restoring `device`. A write followed by device recovery alone cannot
pass. The infrared pattern follows ir-ctl's supported pulse/space syntax and
sets duty cycle only with the supported CLI option.

The QMI LOC helper previously combined two mutually exclusive actions in one
qmicli invocation. Upstream `src/qmicli/qmicli-loc.c` explicitly rejects that
combination. The helper now starts, follows NMEA, and stops separately while
retaining the client ID and session ID. NMEA acceptance checks the checksum,
coordinate bounds and fix quality; a failed start cannot qualify engine control,
and a successful test also requires LOC stop to succeed.

Camera and infrared teardown now removes only modules loaded by that probe,
preserving providers already loaded before it. RTC suspend no longer fsyncs a
sysfs attribute after resume; its permitted duration stays below the independent
32-second watchdog. Suspend evidence uses BOOTTIME minus MONOTONIC to distinguish
actual sleeping from time spent executing the suspend request.

These repairs passed targeted offline tests. They are not new hardware passes.
The host is preparing an incremental result receiver so a lost USB/WLAN control
connection cannot silently discard all completed probes. Physical tag, receiver
and attached USB-peripheral evidence remain required for their respective goals.

# r78 exact target image, NFC bind pass and camera dependency repair, 2026-10-30

The exact public commit `fbcfa258` built successfully in Actions run40936864371.
The complete image, kernel and SSC archives were downloaded independently,
their GitHub SHA-256 digests matched, and the actual SquashFS readback contains
the expected AArch64 `qmicli`, `media-ctl`, `v4l2-ctl` and ModemManager tools.

One bounded RAM boot of that exact image proved the NXP NCI controller bind:
I2C `1-0028` bound to `nxp-nci_i2c`, all four NCI modules loaded, `nfc0`
appeared, and GPIO75 was present as IRQ204. The before/after kernel-health
counters remained zero. The physical tag was not present, so tag discovery is
still unqualified and the retained single-use ledger stays failed.

The real S5KJN5 capture attempt reached CAMSS module loading but `qcom_camss`
dependency `mc` was blocked by the generic peripheral deny policy. The capture
helper now derives the exact camera module closure from `modules.dep`, removes
only matching deny pairs, caps the closure at64 entries, and restores the
original policy bytes after capture. The modem helper can likewise verify the
47 reviewed firmware files already installed in the SquashFS instead of
requiring the separate75 MB archive during the RAM session.

USB NCM/ACM and the Wi-Fi reverse-control path were not stable enough to keep a
live control channel through every long probe. Those failed attempts returned
Android with matching baselines and zero partition writes. They do not qualify
real frame pixels, a GNSS fix, tag I/O, infrared emission, USB-host I/O,
repeated suspend or the remaining peripherals.

## r80 infrared dependency closure and autonomous target execution, 2026-10-30

The infrared helper now resolves `ir_dodge_spi` dependencies from
`modules.dep`, removes only deny pairs in that bounded camera-style closure,
loads providers and transmitter in dependency order, emits the reviewed38 kHz
pattern through `/dev/lirc0`, unloads newly loaded modules in reverse order,
and restores the original module-policy bytes. A failed load still enters the
same cleanup path. The helper continues to report optical output separately,
because a successful write syscall is not proof that the emitter produced IR.

The RAM orchestration was also changed to a machine-local sequence so long
camera, MPSS/GNSS, NFC and suspend probes no longer depend on a host control
connection. Results are written in `/run`; Wi-Fi is brought up only after the
physical probes complete. These are candidate-testing changes and do not
upgrade any unobserved physical result.

## r79 combined IR and USB-role RAM candidate, 2026-10-30

The complete image now builds a separate `camera + MPSS/GNSS + infrared +
DWC3 role-switch` boot. Its DTB keeps the default USB role at `device` for
recovery while exposing the reviewed debugfs role path, and adds the exact
SPI5/GPIO53/L9B infrared node. The normal desktop tree is unchanged.

The image also installs the manual IR, USB-role and RTC-suspend helpers. Static
verification requires separate session identity and preserves explicit false
qualification for optical IR output and USB-host peripheral enumeration.
Offline tests pass519 cases with one environment skip. Hardware qualification
is still pending because the candidate has not completed an exact Actions
image on the phone.

## r77 phone C-PHY camera graph candidate, 2026-10-30

Android stock logs now establish the exact ultrawide route for the installed
S5KJN5: CCI0 address0x2d, CSIPHY1, CSID1 and IFE1 with three C-PHY trios,
4096x3072 at30fps, a logged data rate of6085485713 and settle count45. The
public Three-Phase PHY rate selection therefore uses a1.4GHz link frequency and
the2.8Gsps table, not the reference driver's four-lane1.248GHz D-PHY mode.

The source now stages the reviewed SM8750 CAMSS/CSID/VFE series, the public
phone C-PHY MMIO adapter, a three-trio S5KJN5 mode with an explicit
`get_mbus_config` callback and an isolated `CSIPHY1 -> CSID1 -> VFE1` device
tree. A clean fixed-pin component build passes with warnings treated as errors,
and the WSL offline suite passes510 tests with one environment skip. A separate
RAM boot candidate embeds the capture graph and a manual one-frame V4L2 helper;
the default desktop tree remains unchanged. A second isolated tree combines that
camera graph with the manual MPSS/GNSS node and firmware archive so one RAM test
can capture a frame and exercise QMI location. No real sensor pixel frame has
yet arrived, so camera capture is not qualified. See
[r77 camera C-PHY source](R77-CAMERA-CPHY-SOURCE-20261030.md).

## r75 modem/NFC/suspend source candidate, 2026-10-30

The quiet r74b RAM round passes strict S5KJN5 identity and cleanup, one native
Iris frame, NFC controller start/stop, the read-only peripheral matrix, Android
return and all baseline properties. NFC now binds11-0028,nxp-nci_i2c, GPIO75
IRQ212 and creates/powersnfc0; a physical tag remains to be presented.

The exact C.93 modem split set size74,867,650 bytes passes MDT/carveout review.
RAM MPSS reached running, exposed GLINK IPCRTR/SSM_RTR_MODEM_APPS and qrtr-tun,
then cleanly returned offline. One RTC wake completes a14.334s deep suspend
with0.103s monotonic time and a disarmed32s safety watchdog. The first
coordinator rejected only an immediate watchdog-state read; the corrected
helper waits for the transition and requires a repeat combined round.

Source now carries online-build firmware, NFC/MPSS services, qmicli/QRTR/v4l
userspace, reviewed IR and OTG trees, and RTC suspend tests. IR optical output,
GNSS location/QMI, USB host peripherals, repeated idle/suspend, full modem
services and supplier-specific camera capture remain open. See
[r75 peripheral progress](R75-PERIPHERAL-PROGRESS-20261030.md).

The full native Linux offline suite passes496 tests with one environment skip.

## r71 complete joint round and speaker-gain follow-up, 2026-10-29

The d872a04e update passed every automated combined check in647.5s and returned
Android with matching baselines and zero writes. The owner confirmed upright
portrait is now correct after the pitch-only mapping fix; left/right mapping and
Dock remain correct. Guarded GStreamer hardware decode, microphone, two-speaker
correlation and the 20/50/100/mute system-volume sequence all pass.

An identical-WAV Android comparison then showed Android maximum is much louder
than Linux. The former896 Linux ceiling deliberately retained11.921875dB of
profile attenuation. A1023 full-control-range RAM candidate is now prepared for
short physical validation. Stock dynamic protection/calibration remain open. See
[speaker comparison](R72-SPEAKER-VOLUME-20261029.md).

## r70 framework decode and pose mapping, 2026-10-29

Build40885554785 on83768fc passes and its complete image/SSC/kernel are
independently verified. Guarded GStreamer hardware decode now passes one fixed
AVC-to-NV12 frame, pixels/PTS/cleanup and Iris suspend/unload. The40-second
physical collection confirms upright falsely maps to bottom-up/transform2 while
left/right map1/3. A pitch-only udev candidate requires the next physical
retest. Microphone and two-speaker acoustic correlation pass after display.
The software-volume step was reached too late in the fixed600-second window and
did not run; Android returned with matching baselines and zero partition writes.
See [r70 evidence](R70-HARDWARE-AND-ORIENTATION-20261029.md).

## r69 combined diagnostic and source repairs, 2026-10-29

Hosted complete build40873139247 on16f96cab passes and returns Android in513.6s,
seven matching baselines and zero partition writes. Native Iris pixels/cleanup,
both WiFi bands, Docker, desktop/GPU, Chinese/SSH and Dock pass; WiFi SSH now
verifies the exact RAM identity with USB retained. Upright portrait remains
inverted; owner confirms no relogin and a visible Dock. Dynamic observation
missed its host go trigger. Audio checks refused the known post-display policy
before successful measurements. GStreamer still fails negotiation.

Candidates now complete the fixed AU's profile/level/colorimetry caps, accept
only the exact existing CEC/UBWC no-op policy transformation in native audio
helpers, and reuse bounded verified-download caches in SSC/kernel packaging.
They require a fresh combined round. No physical rotation/loudness/framework/
camera acceptance is implied. See [r69 results and repairs](JOINT-R69-20261029.md).

## Camera callbacks and diagnostic cleanup, 2026-10-29

Phone C-PHY compile-only Actions40869936054 passes. Downloaded archive digest
and11 uploaded AArch64 objects match; the missing twelfth audio-library object
is now added to the workflow upload list. A clean WSL phone-C-PHY/IR component
build passes with13 objects and45 actual callback host cases in release and
ASan/UBSan modes. Normal component builds now include these callback checks.
The GStreamer error collector's repeated-RESYNC loop is bounded/resynchronized;
nine focused tests pass. These changes do not establish camera pixels or fix
hardware video negotiation. See [evidence and remaining work](CAMERA-MMIO-CHECKS-20261029.md).

## Camera source build path, 2026-10-29

The camera component workflow now has an explicit compile-only path for the
source-derived phone C-PHY table and the CAMSS, sensor, CCI and phone PHY
objects. It records the phone C-PHY translation unit and skips synthetic and
unit checks in that mode. The candidate remains isolated: no camera node is
enabled or installed into the normal image. Full camera capture is still
incomplete because the C.93 L/S module initialization differs and the selected
supplier and mode have not been established. This compile path does not claim
a usable camera or qualify a physical frame.

## Orientation and audio follow-up, 2026-10-29

The owner now confirms autorotation is active but upright portrait is upside
down; maximum system volume rises with the slider but remains too quiet. The
next source image records SensorProxy posture and Mutter transform together so
the upright-versus-inverted mapping can be identified from one dynamic capture.
It also records bounded per-pad GStreamer current/query caps with private error
details when V4L2 negotiation fails. These are diagnostics, not fixes or new
hardware acceptance. Keep the AW88461 ceiling at896 until the phone's dynamic
speaker protection and calibration are understood; the current profile retains
11.921875dB attenuation. This turn must not claim rotation, loudness or framework
decoding resolved without subsequent owner-visible evidence.

## r68b compiled image and joint results, 2026-10-29

Complete mixed image Actions 40858720951 passes all five jobs. Optional phone
C-PHY and SPI IR components compile in 40858838126; downloaded artifact digest
and 12 AArch64 objects are verified. Native gates 40859294051 pass. The local
offline suite runs 615 tests with five environment skips. The framework selftest
parser now treats frame and teardown receipts separately. No experimental
camera PHY or IR board node is enabled.

The immutable 5120fbac image completes a 546.1-second combined RAM round and
returns Android with all seven baselines equal and zero partition writes.
Camera ID, native Iris pixels, decoder autosuspend/unload, clean guard disarm,
dual-band WiFi, Docker bridge/DNS/NAT/port, GNOME/Mesa/touch discovery, Chinese,
SSH, Dock, microphone, two-amplifier correlation and system volume response
pass. Full-history kernel health stays clean. GStreamer still fails caps
negotiation; private bus details are retained, but its precise cause is not yet
established. Failed framework decoding is not hardware framework acceptance.

The owner sees automatic rotation, but normal portrait is upside down. The
planned transition capture was skipped after its existing time cutoff; this
physical report exposes a gap in the earlier fixed-left-up-only acceptance.
The owner hears increasing system volume but says maximum remains too quiet.
The current896 hardware ceiling adds at least11.9219dB profile attenuation;
absolute loudness and dynamic protection remain unqualified. Do not raise
limits or apply a global rotation based only on fixed-pose agreement. Next:
correlate labeled upright/left/right physical poses with raw acceleration and
Mutter state, move the human phase earlier, review speaker protection/gain,
and retain bounded V4L2 negotiation traces in the next combined round.

An earlier r68 attempt stopped before feature activation when the USB network
disappeared; the owner reports manually rebooting then. Its halted ledger and
stop flag remain intact. No driver failure is inferred from that interruption.
See [r68b evidence](evidence/joint-gstreamer-r68b.sanitized.json).

## Compilation and joint validation resumed, 2026-10-29

The owner resumed compilation and joint testing. Build the current source with trusted-server kernel/Mesa/SSC and hosted rootfs/assembly, and compile optional phone C-PHY and infrared components separately. These disabled candidates have no new hardware acceptance; r64 remains the accepted combined baseline pending fresh evidence.

## Source-only owner request, 2026-10-29

Compilation and all testing are paused by the newest owner instruction. The
current batch adds an opt-in phone C-PHY MMIO/clock/IRQ/rollback candidate,
bounded rc-core SPI infrared source with a separate disabled board fragment,
GStreamer failure/teardown evidence and failed-path autosuspend observation,
source-preparation-only modes, and an all-on-server Actions placement option.
None of these changes has been compiled or tested. Publication does not dispatch
CI. r64 remains the last accepted combined hardware image.

See [the source-only batch](SOURCE-ONLY-BATCH-20261029.md) for exact code scope,
provenance and unresolved work. Camera supplier initialization, complete receiver
graph, IR shared-rail constraints, modem/GNSS/NFC, full USB roles and independent
idle/suspend recovery remain open. Do not describe the remaining adaptations as
complete, enable these candidates by default, or reuse earlier unattended
authorization to start testing while this newer pause remains in effect.

## r66 framework stream error; parsed-caps candidate

The exact54310783 image from Actions40847882940 and native gates40849346728
passes independent downloaded-byte verification. The combined phone round
passes camera ID and native Iris pixels again. Read-only factory selection now
succeeds, then GStreamer reports gst-stream-error-quark:1. Its old error handler
omits the message/debug text, so the exact framework failure is not established.
Iris unloads, nodes disappear and the guard acknowledges teardown and disarms.
Kernel health remains clean; Android returns after187.5s with seven matching
baselines and zero partition writes. The failed round's halted ledger and final
host transport flag are preserved. The recovery transcript has no complete RAM
identity receipt, so the socket reset remains fail-closed. Later mature
regressions are not reached. See [r66 evidence](evidence/joint-gstreamer-r66.sanitized.json).

Pinned GStreamer source requires parsed=true for encoded V4L2 input; the old
synthetic-AU caps omit it. The candidate adds that field only for the exact
hash-checked synthetic fixture. A real GI caps-subset test reproduces the old
mismatch and accepts the corrected caps. Bounded private bus message/debug text
is retained on failure while the public exception remains domain/code only.
All seven framework tests pass. These source-derived changes still need fresh
Actions/download verification and a combined phone run; they are not proof of
the r66 error's sole cause or of hardware framework decoding.

## r65 framework device-property failure and corrected selection

The exact38df6a13 image passes all five Actions40844694343 jobs and independent
download verification. The joint phone round repeats strict camera ID and the
native Iris AVC frame, but GStreamer fails before decoding because the helper
writes the dynamic mem2mem factory's read-only device property. The pinned
GStreamer1.28.2 source confirms the device is bound at factory registration.
Iris unloads, video nodes disappear and kernel health stays clean. Android
returns after248.4s with seven matching baselines and zero partition writes.
The consumed halted ledger is preserved; later mature regressions are not
reached. No framework or idle/suspend reset acceptance is claimed. See
[r65 evidence](evidence/joint-gstreamer-r65.sanitized.json).

The corrected helper selects an explicit video4linux2 H264 factory by reading
its exact registered device path, without setting the property. Tests exercise
the read-only property, other device, wrong plugin and software decoder cases;
all five framework tests, including real raw-GStreamer pixels/PTS/NULL, pass.
A fresh source image and complete combined phone round remain required.

## Explicit GStreamer path prepared after accepted r64 native frame

The next manual image adds a hash-bound GStreamer helper and the required GI
and diagnostic packages. It uses appsrc -> explicit video4linux2 H264 decoder
-> NV12 appsink; there is no decodebin or software decoder fallback. The
synthetic frame, timestamp, visible luma and real VideoMeta stride are checked,
then the pipeline must reach NULL. A fresh RAM plugin registry is built only
after guarded Iris activation. The optional --gstreamer flag requires both
the already accepted native frame and the framework frame, runtime suspend
and full module teardown under the same fixed awake guard. At least65s of
the original90s window must remain before activation; it cannot be extended.

The real raw-GStreamer selftest passes on WSL and checks timestamps, pixels
and NULL teardown without requesting decode. Bounds/corruption/guard tests
pass. The full offline suite passes611 tests with5 environment skips. This
is a candidate until fresh Actions/download verification and a combined phone
round pass. Do not upgrade raw-framework selftest to hardware playback.

## r64 real Iris frame and retained regressions pass, 2026-10-29

The exact ee214438 Actions40833999996 image passes all five source-build jobs,
independent downloaded-byte verification and the combined hardware round.
Iris decodes the synthetic320x240 AVC frame to linear NV12 with checked luma
and timestamp, without software fallback. Input size7077888 is confirmed by
S_FMT/QUERYBUF;16 capture buffers are147456 bytes each. Both streams stop,
runtime suspend passes, the module unloads and video nodes disappear. The
separate awake guard acknowledges cleanup and disarms before the host recovers.

Strict camera ID/teardown, ordinary sensor startup/left-up Mutter1, microphone,
both speaker correlations, actual20/50/100%+mute, Docker bridge/DNS/NAT/port,
both WiFi bands, GNOME/Mesa, Chinese/SSH/Dock and final kernel health pass.
Android returns after501.4s with seven matching baselines and zero partition
writes. [Sanitized evidence](evidence/joint-video-r64.sanitized.json) retains
an additional final host stop flag set after feature acceptance during the
recovery path; it is not cleared. No phase-stop event occurs and the saved
recovery transcript contains the correct RAM identity receipt. Review that
transport boundary before a new plan. Older failed-run flags also remain.

This accepts one bounded V4L2 frame and cleanup, not desktop playback, VA-API,
all codecs, long-duration decoding, idle/suspend recovery or camera capture.
A source-derived phone C-PHY sequence planner additionally passes29 rate-table,
126 abort-injection and8 invalid-input cases in release/sanitizer builds; it
has no production MMIO adapter or active camera graph.

## r63 Iris activation: input allocator limit, clean recovery

The exact b1cf1932 Actions40831129105 image passes independent downloaded-byte
verification. Its combined plan passes strict camera ID/teardown, then opens an
Iris firmware session under the bounded awake watchdog guard. The native client
stops at output-buffers with EOVERFLOW75 before any verified frame. The pinned
Iris input formula returns7077888 bytes even for320x240 H.264, above the client's
old2MiB bound. r63 did not log the returned size, so this cause is source-derived;
the retry must record actual queue sizes. Both streams stop, Iris unloads and
video nodes disappear. The guard verifies teardown and disarms. Kernel counters
remain zero; host recovery returns Android after192.1s with seven matching
baselines and zero partition writes. Later mature regressions were not reached.
[Sanitized evidence](evidence/joint-video-r63.sanitized.json) retains the failed
joint result and stop flag; no hardware decode acceptance is claimed.

The revised allocator accepts the negotiated input size up to8MiB, keeps a2MiB
capture bound and64MiB aggregate queue cap, and records granted counts/lengths.
Release and ASan/UBSan tests exercise the actual allocator with the7MiB driver
size, malformed returns, mapping/query errors and partial cleanup. Fresh Actions,
downloaded-byte verification and the full guarded combined round remain required.

## r62 independent awake recovery accepted; guarded video window prepared

r62 repeats every mature combined phase on the verified5f37a1da image with
published66756a58 host-served watchdog code and e65db825 receipt parsing.
The awake ioctl sequence12/10/12 passes, the host issues zero recovery/reboot
requests, and Android returns independently after490.2s with seven matching
baselines and clean pre-arm kernel health. This qualifies the explicit awake
CPU scope only. Historical r58/r59/r61 stop records remain unchanged; idle and
suspend recovery are not accepted.

The next source image requires a separate awake guard before opening Iris.
Its fixed90s window cannot be renewed, keeps one CPU runnable and pings every3s;
expiry/errors stop feeding while retaining a45s awake reset observation window.
An authenticated root-only RAM stop request is accepted only after the video
helper reports complete teardown and qcom_iris is absent. The video helper
requires an active guard unit, actual active Gunyah watchdog and more than45s
remaining before any module insertion. The full Linux offline suite passes607
tests with5 environment skips. No default watchdog/video policy changes.
Fresh Actions, downloaded-image verification and a combined hardware round are
required at that historical stage; r64 above records the later activation.

## Phone C-PHY data catalog prepared, 2026-10-29

The isolated --cphy component build now includes a hash-bound review of the
unmodified public GPL dodge-ultrawide v2.3.0 source:29 rate tables,36 registers
each, three-trio address/parameter checks,72 base and4 common records, and
the exact3048us reset-release delay. A symbol-rate selector avoids the mismatch
between the vendor's rounded2.28 rate thresholds and the generic exact16/7
formula. Sixty release/sanitizer boundary checks, AArch64 data-object compilation
and a clean full WSL component rebuild pass. Native ARM64 Actions40829917850
passed this addition and all component targets. No phone runtime table, MMIO or capture is enabled. See
[CAMERA-PHONE-PHY-CATALOG-20261029.md](CAMERA-PHONE-PHY-CATALOG-20261029.md).

## r61 countdown passes; host protocol error prevents reset acceptance

r61 on the retained5f37a1da Actions image with the separately published66756a58
host-served helper passes all mature combined phases and the actual awake
watchdog ioctl sequence12/10/12, with raw elapsed2000 across the busy2s interval.
The host's old receipt regex incorrectly required armed as the first JSON key;
the new active_wait_required field sorted first and caused premature recovery
handling. Android returned after488.7s with matching baselines and clean bounded
kernel evidence, but independent reset is not accepted. Preserve the stop flag.

The new host-only watchdog_receipt.py parses a unique JSON line independent of
key order, rejects ambiguous/duplicate/oversized receipts and rechecks all arm
gates without treating a receipt as observed reset. Four regression tests include
the new first-key ordering and journal-prefixed duplicate text. The complete
native ARM64 offline-gates workflow now runs both watchdog suites. Before a new
joint round, replay the actual r61 transcript and preserve the full independent
observation window after possible arming, including host parsing errors.

## r60 clock comparison and retained regressions, 2026-10-29

Actions40824286846 passed all five jobs on5f37a1da. Independent downloaded
image verification and r60 repeat all mature combined checks, including camera
chip-ID/teardown, fresh microphone/separate-speaker correlation, actual desktop
20/50/100% plus mute, both WiFi bands, Docker, ordinary left-up/Mutter1 and
GNOME/Chinese/SSH/Dock. Kernel-health gates are clean; Android returned after
473.9s with seven matching baselines and zero partition writes.

On CPU0 the six-second diagnostic reads raw elapsed0, then28 after idle2s,
2028 after busy2s, then83 after idle2s, and0 after the explicit final keepalive.
The busy interval used1.99875s process time. No explicit keepalive occurred
between the three intervals. The drop2028 to83 means simple paused cumulative
CPU time is not a sufficient explanation: an idle-related reset or another
feeding/control path remains possible. No independent reset was requested or
qualified. The next explicit reset candidate pins its own process and busy-waits
through the unchanged12s countdown/keepalive/20s expiry gates, records the awake
requirement, and excludes idle/suspend qualification. It still requires host
observation of Android return and baseline equality; no kernel timer semantics
or get_timeleft calculation changes.

## C-PHY framework compiles in isolation, 2026-10-29

An explicit --cphy component-build option now rebases the six-message public
Qualcomm PHY/CAMSS RFC onto the exact existing stack, with original authors/
messages and eight-file pre/post hashes. A clean archive-based AArch64 WSL
build passes all camera/clock/amplifier objects and disabled DT with W=1/-Werror.
The actual staged functions pass26 release and26 ASan/UBSan boundary cases;
the full Linux suite passes596 tests with5 environment skips. The component
Actions40826100382 passed the complete native ARM64 cphy=true build, including
both synthetic suites and all component/DT targets.
The candidate remains outside the normal phone kernel and has no phone C-PHY
register tables or capture qualification. See
[CAMERA-CPHY-FRAMEWORK-20261029.md](CAMERA-CPHY-FRAMEWORK-20261029.md).

## Ultrawide C-PHY template family resolved, 2026-10-29

The saved complete stock FDT supplies probe_intent0x30e0 for CCI0 sensor1.
The pinned vendor pre-match callback ORs this into the module ID: L/S0x805
becomes the observed0x38e5, while D0x30e0 remains a mismatch. This resolves
the prior ID ambiguity and points to the inferred L/S three-trio C-PHY modes;
supplier, timing and capture are still unqualified. The board review now
checks this property and emits the effective IDs, with negative tests for
missing/changed values. It passed against the saved full FDT. See
[the revised mode review](CAMERA-MODE-SELECTION-20261029.md).

## r59 joint regression and raw timer evidence, 2026-10-29

All five jobs in Actions40820121568 passed on da0f54cb. Independent downloaded
image verification and r59 repeat camera chip-ID/teardown, microphone, separate
speaker correlation, actual20/50/100% plus mute, both WiFi bands, Docker,
production left-up/Mutter1 and GNOME/Chinese/SSH/Dock. Kernel-health gates are
clean. Android returned after493.6s with seven matching baselines and zero
partition writes. Native video selftest passed without opening hardware.

The read-only Gunyah STATUS diagnostic now gives direct evidence: enabled0
before open, enabled1 after open, raw elapsed0 immediately after keepalive and44
after2.0004s, while GETTIMELEFT remains12. The ABI's bit31 is1 immediately after
open as well as later; its asserted state alone is not reset evidence. Units,
idle-time behavior and the meaning of that flag on this firmware remain open.
Cleanup disarmed the watchdog; host recovery, not independent expiry, returned
Android. Keep the historical stop flag and video/suspend recovery gates.

A separate --diagnose-clock mode samples idle2s/busy2s/idle2s on one allowed
CPU at the original32s timeout, records wall/process time and raw STATUS,
checks the final keepalive response and magic-closes. It does not infer units,
change the driver or relax the existing12s reset acceptance path. Its fresh
Actions/source-bound combined diagnostic remains pending. Camera template
selection is reviewed separately in
[CAMERA-MODE-SELECTION-20261029.md](CAMERA-MODE-SELECTION-20261029.md).

## r58 exact source image regression; Gunyah countdown diagnosis, 2026-10-29

All five jobs in Actions40816388596 passed on297a5a69. Independent downloaded
image verification and r58 completed the camera chip-ID/teardown, microphone,
separate-speaker correlation, actual20/50/100% and mute, dual-band WiFi,
Docker bridge/DNS/NAT, production left-up/Mutter1, GNOME/Chinese/SSH/Dock
regressions. The source-built AArch64 video client's selftest passed without
opening video hardware. Android returned after495.0s with seven matching
baseline fields, clean kernel-health gates and zero partition writes.

The final Gunyah experiment set/read12s successfully and passed capabilities
0x8180. GETTIMELEFT returned12 both immediately and after2s; it stopped at the
countdown gate and magic-close disarmed it. No independent reset was observed.
Retain the existing stop flag and keep Iris activation and suspend deferred.
The next kernel adds a root-only STATUS-read diagnostic for the hypervisor's
enabled/expired flags and raw elapsed value, with monotonic samples in the
manual helper. It issues no control/timeout/ping calls and changes no timer
semantics. AArch64 W=1/-Werror object compilation and the full Linux offline
suite (592 tests, 5 environment skips) pass; fresh Actions and
combined hardware evidence are still required to diagnose the underlying timer.

## r57 retained regressions passed; watchdog diagnostic stopped, 2026-10-29

The exact36f14243 Actions image completed camera chip-ID/runtime-suspend/teardown,
production sensors with left-up/Mutter1, microphone capture, separate speaker
correlation,20/50/100% plus mute acoustic measurements, Docker bridge/DNS/NAT,
both WiFi bands and GNOME/Chinese/SSH/Dock regressions. Kernel-health gates were
clean. Android returned after484.7s with matching baseline and zero writes.

The final independent watchdog experiment returned an unarmed, disarmed receipt
without countdown or keepalive qualification. Host recovery was used; independent
reset is not accepted. The old receipt omitted the failing ioctl/check and values.
The helper now records stage, timeout/capability/countdown readbacks and a bounded
failure reason before magic-close cleanup. Keep video activation deferred while
this recovery gate remains open. Completed feature phases do not establish
independent recovery acceptance.

## Source-built bounded video runtime prepared, 2026-10-29

All five source-image jobs in Actions40813654094 passed on36f14243. The host
downloaded and independently verified its boot sections, four alternative video
artifacts,72 firmware files and retained desktop/sensor/audio inputs. r57 is a
combined camera and retained-feature test on this exact image, ending with an
independent normal-running watchdog expiry experiment; its outcome is pending.

The next image adds a source-built static AArch64 stateful V4L2 client and a
manual RAM coordinator. One generated AVC color-bar frame must yield real linear
NV12 pixels with the correct timestamp, followed by stream stop, runtime suspend
and module teardown. The package binds runtime files, live DT resources and module
dependencies and requires native ARM64 plus sanitizer selftests. The full Linux
offline suite passes591 tests with5 environment skips. No video hardware has
been activated; decoding, firmware authentication and VA-API remain unqualified.

## Camera chip ID confirmed; separate Iris source-image preparation, 2026-10-29

Actions40807894969 completed all five source-image jobs on69f7fae0. Downloaded
artifacts passed independent boot-section/source/firmware verification. In r55,
S5KJN5 at the corrected7-bit0x2d bound successfully, reached runtime suspend,
and its sensor/controller modules and I2C target were removed. The kernel-health
checks stayed clean and Android baseline matched after166.2s. This establishes
the bounded chip-ID path only; no frames were requested. The joint coordinator
then stopped on an already-unloaded transient-unit cleanup status, so retained
regressions did not complete. r56 was interrupted on the host after RAM boot;
only subsequent Android recovery/baseline equality was observed. Neither round
is reported as a complete joint pass or independent watchdog qualification.

The phone-specific C.93 Iris firmware is now in the scrubbed data manifest
(72 firmware files). A fourth, separate manual video RAM image is built by the
normal source-image pipeline and independently rederived by the package verifier.
Its kernel/initramfs must match the default desktop; only the reviewed separate
DT and session identity differ. The default DT remains video-disabled and the
Iris module retains its manual-load policy. Firmware authentication, actual
decoding and VA-API support remain untested. Linux offline suite:588 tests pass,
5 environment skips. A fresh full Actions build/download and combined hardware
round are required before any new hardware claim.

## First camera probe isolated address error, 2026-10-29

All five jobs of Actions40803790845 and native camera components40804095331
passed. The downloaded b01bf7ce image passed independent hashes, boot-section
and camera-tree rederivation checks. In r54 the camera client at the unverified
reference address0x10 returned I2C ENXIO. Sensor/controller teardown passed,
kernel-health counters stayed zero, and Android returned in170.9s with matching
baselines and zero partition writes. No capture or successful chip ID is claimed.

Local C.93 D/L/S ultrawide module slaveInfo records all specify8-bit0x5a.
The separate camera tree/helper now consistently use Linux7-bit0x2d and retain
the strict0x38e5 hardware ID check. Proprietary raw module tables stay private.
This correction requires a fresh Actions image and joint hardware regression.

Read-only power readiness found RTC wake support and an inactive Gunyah watchdog,
timeout32s. The exposed deep sleep mode alone is not suspend acceptance. Verify
independent recovery before any unattended suspend. USB role/typec and video
class nodes remain absent in this early pre-platform observation. No USB role,
RTC alarm, charging policy or power state was changed.

## Separate camera chip-ID candidate prepared, 2026-10-29

A separate camera/microphone boot recipe now derives CCI0/master0, the phone's
ultrawide GPIO/clock/supply graph and a S5KJN5 client from the qualified tree.
It preserves every unrelated microphone/desktop property and all reserved
memory, checks3 existing-node changes and18 additional nodes, and remains a
manual alternative boot artifact. The source-built rootfs carries a default-off
chip-ID helper with live board/module/policy/RAM/watchdog checks and complete
controller/sensor teardown. It never requests a frame. The VDDM shared digital
vote remains an explicit inference rather than a schematic claim.

All584 offline tests pass with5 environment skips. S5KJN5/full kernel linking
passed the kernel job of Actions40801825269; its image assembly is still running.
The camera alternative and its new package verification require a fresh complete
Actions build. No physical camera power/probe has been attempted yet. See
[the chip-ID candidate](CAMERA-CHIP-ID-PROBE-20261029.md).

## Downloaded desktop image qualified; S5KJN5 driver staged, 2026-10-29

The exact e06f06bd Actions40798138265 image passed r53 in421.4s, then returned
to Android with matching baselines, zero writes and clean kernel-health gates.
It repeated fresh microphone capture, independent speaker correlation, actual
20/50/100% plus mute acoustic measurements, production sensor startup without
SSC warmup and left-up/Mutter1, together with dual-band WiFi, Docker, GNOME,
Chinese, SSH, Dock, Bluetooth and battery. Boot SHA256 is
e7b8b3926982e51437bbc538d0bf439e7ef2b0422b16822f1996be89564c6e3a;
rootfs SHA256 is88c80aee0ec9209f6a7f5268c5eb3f23f06c3b30ad606c29a822e81597a0310b.
Independent download verification includes all hashes/sections,71 firmware
files, SSC inputs and the new manual volume checker. No standalone digital-zero
experiment was repeated in r53; the one-shot native PCM test used the quiet
nonzero mode followed by the independent acoustic checks.

Native ARM64 camera/CCI component
[Actions40799459424](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40799459424)
passed. Wenmeng Liu's public S5KJN5 v6 driver now also compiles with the exact
phone kernel after a separate two-callback API compatibility patch. Both original
messages, unchanged register/mode tables and compatibility hashes are retained.
The normal phone kernel build stages this module with source/hash checks and
idempotent rerun validation; the media module policy keeps it manual, and no
camera node is added to the default phone DT. Fresh full Actions and native
sensor-component builds are required for this addition.

The phone ultrawide graph matches chip-ID0x38e5, CCI0/master0, PHY1, resetGPIO178
and19.2MHz MCLK0. Its explicit PM8010m supply rails and the vendor's custom PHY
must be mapped before any sensor power/probe. Android exposes no regulator_summary
at either usual read-only path; the saved FDT retains the regulator resources and
initial voltages. No camera was opened or powered by the inspection.

## Production sensor startup and disabled camera-resource build, 2026-10-29

r52 repeats the fixed left-up observation without the diagnostic SSC vector
warmup or restarting the sensor stack. The ordinary protected desktop startup
reports left-up/vertical with Mutter transform1. Dual-band WiFi, Docker, GNOME,
Chinese, SSH, Dock and silent current-audio setup passed together; r51's fresh
acoustic evidence is explicitly reused for the identical30908706 image. Android
returned in350.6s with matching baselines and zero partition writes. This closes
the startup-warmup dependency in the previous entry, while an attended physical
rotation transition and long-duration speaker protection remain open.

The current source image passed all five jobs in
[Actions40798138265](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40798138265)
on e06f06bdd3d852712ee3ea4770a0c1e6851d3cc5. Independent download verification
is in progress; this new artifact is not yet a hardware acceptance.

Camera preparation now adds disabled CCI/MCLK resources only inside the isolated
component build. The28 original/rebase/compiler patches preserve provenance;
the original CCI v2 context depended on an unstaged old CAMSS node, so a separate
reviewed rebase carries only the disabled CCI and pinctrl additions onto the exact
kernel pin. WSL AArch64 cross compilation passes W=1/-Werror, synthetic PHY and
amplifier checks, and an actual phone base-DTB check for3 disabled controllers
and6 I2C hosts. This does not install or activate camera hardware. Front-camera
sensor mode tables, the new PHY graph, phone power sequencing and libcamera/RDI
capture remain the next implementation work. The maintainer rejected the resource
series pending driver dependencies; it is not represented as merged support.

## Exact Actions image: left-up and real desktop-volume response, 2026-10-29

The unattended r51 joint RAM boot used the exact downloaded boot/rootfs from
Actions40764560596, source30908706429e0aeb154b8b3a57f911cd5b3080f1, with
source-bound diagnostic helpers. It returned to Android in440.1s with matching
baselines, zero partition writes and clean kernel-health gates. Both WiFi bands,
Docker IPv4 bridge/DNS/NAT/published ports, GNOME/Mesa, Chinese, SSH, Dock,
Bluetooth and battery checks passed together.

The owner placed the phone left-side-up. Thirty-two live samples reported
`left-up / vertical`, and Mutter reported transform1, matching upstream's exact
left-up mapping. Static observations now use `static_pose_pass` and never claim
a multi-pose automatic-rotation transition. Flat poses cannot satisfy an explicit
upright expectation; right-up requires3 rather than either landscape transform.
The current combined test still used the SSC vector warmup before this check;
ordinary startup without that diagnostic warmup remains to be checked.

Fresh microphone capture and independent top/bottom speaker correlation passed.
The new bounded desktop test recorded the same1000/1500Hz fixture through
PipeWire at20%,50%,100% and mute. Both measured components increased strictly
with system volume; full-volume/mute ratios were17518x and20336x, with zero
clipped samples. Both amplifiers stopped cleanly, capture controls were restored,
and raw recordings were deleted. Prior night tests deliberately used1%,2%,5%;
they were not ordinary-volume qualification. The fixed896 hardware ceiling is
unchanged. This validates actual software-volume effects, not calibrated SPL,
long-duration dynamic protection or default speaker autostart.

The r50 digital-zero pass is reused only for the identical Actions image.
The native PCM helper permits one experiment per boot, so r51 reserved it for
the nonzero check rather than attempting both modes with the same one-shot marker.
The new acoustic volume checker is packaged explicitly and remains default-off.
The full Linux offline suite passes580 tests with5 environment skips.

See [scrubbed evidence](evidence/UNATTENDED-LEFT-UP-VOLUME-20261029.json).
Camera is the next peripheral priority. The phone's four stock sensor graphs
and OTA front-module inputs were re-inspected locally; no camera capture has
been accepted and private OTA inputs have not been published.

## Unattended joint pass and final SensorProxy repair, 2026-10-29

The r49 single RAM round on source candidate `da91d97a` passed every combined
target. It used the final reviewed root SensorProxy configuration, an SSC
three-vector warmup, the same desktop-user D-Bus connection for claim and
orientation reads, and the current PipeWire/Pulse fallback helper. Android
returned with matching baselines, zero physical writes and zero recorded
kernel-health faults.

The phone was physically stable at `AccelerometerOrientation=undefined` and
`AccelerometerTilt=face-down`. The desktop acceptance now treats
`face-down`/`face-up` with Mutter transform `0` and `normal` with transform
`0` as correct static states, while `right-up` still requires transform `1`
or `3`. The same round recorded `face-down + transform 0` for 32 bounded
samples. The historical 60-sample owner posture run already established real
`bottom-up`, `left-up` and `right-up` sensor transitions; a new upright
Mutter transition remains desirable after the final image is available.

The joint boot passed directed 5GHz association at 5240MHz and 2.4GHz
association at 2437MHz, DHCP/default-route/private-LAN HTTP200, real Docker
bridge/DNS/NAT/published-port traffic, GNOME/Mesa, touch discovery, Chinese
locale and input source, SSH password login, visible-left Dock settings,
battery, Bluetooth and the persistent sensor services. Current speaker
configuration loaded with the fixed 896 ceiling, then was muted and set to
0 percent before clean teardown; the already accepted r18/r29 microphone,
two-speaker acoustic and software-volume evidence was reused to avoid a
night-time audible sweep. The complete offline suite passes 575 tests with
five environment-dependent skips.

The final source changes make SensorProxy run as a restricted root service so
the proxy may perform its own Polkit authorization, allow only desktop account
`a` and root to claim sensors, and keep the reverse file server at UID/GID
65534 with its device policy. Ordinary loudness, dynamic speaker protection,
overlay2/IPv6 Docker modes, physical axes calibration, suspend and long-term
stability remain outside this acceptance.

GitHub Actions run
[40764560596](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40764560596)
completed all five jobs on published source
`30908706429e0aeb154b8b3a57f911cd5b3080f1`. The downloaded artifact was
independently verified: boot SHA256
`53593732ea5003643cdbae3baed8d7e4eead913f51a64a88d49c17ca90209796`
and rootfs SHA256
`1288689f4e75915ce1a99785d5b811bfa25bedc7be3628e642a940fae013e44b`.
The final ZIP SHA256 is
`99ba72524a593c38111ea0bc16e26da16e17c8ba2d946e14ac5560be6b1f5ead`.
Boot-section, SHA256SUMS, qualified firmware, SSC, sensor runtime, desktop
sensor service, Docker, timezone, 896 speaker and native `pactl` checks all
match the reviewed source.

## Final hybrid build and pending owner rotation acceptance, 2026-10-29

Commit `da91d97a7eddd411437cb8582430ea484a79f10f` completed the full mixed
Actions run [40719703246 attempt 2](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40719703246/attempts/2).
Kernel, Mesa and SSC built on the owner's self-hosted ARM64 runners; the
GitHub ARM64 runner built rootfs and performed final image assembly. A transient
self-hosted Mesa source-download failure was retried without changing code or
the successful kernel, SSC and rootfs products.

The downloaded boot image SHA256 is
`3644d5189047d6952e14c7c8b29a78dab29e7601c74015e836986aa50aeed3e2`;
the rootfs SHA256 is
`aea746eb428e63dfb3d964a53b2a01b4828b50269177ad43e22c2c8072ce8941`.
Independent host verification passed all boot sections and SHA256SUMS, 71
qualified firmware files, 4 SSC probe inputs, 3 SSC sample inputs, 9 sensor
runtime inputs, 10 desktop sensor integration files, 4 Docker files, 896
desktop speaker configuration and a native ARM64 `pactl`.

The native PipeWire sink factory and destruction path were exercised against a
real PipeWire 1.6.2 instance. The final helper creates
`api.alsa.pcm.sink` through `spa-node-factory`, quotes `hw:<card>,0` for
`pw-cli` parsing, requires six seconds of node persistence, and falls back to a
temporary Pulse ALSA module through the explicit user Pulse socket. The last
single-device run reached the owner audio window but failed before playback
because WirePlumber did not expose a default sink. The final code now targets
the explicit node for volume and playback. The 569-test offline suite passes.

The current phone-test authorization expired before the final joint boot. The
next single RAM boot will test both speakers with 20/50/100 percent PipeWire
volume and mute, three owner orientations with Mutter transform changes, and
the retained dual-band WiFi, Docker, GNOME, Dock, Chinese and SSH checks.

## Sensor-first posture pass and desktop runtime candidate, 2026-10-28

The owner-assisted posture window on image
`17ecf5425ad3b07aff53c3e328b5838a0ae20a12` completed with 60 accelerometer
samples and actual `bottom-up`, `left-up` and `right-up` transitions on one
claim/release. The screen had not started, so this proves physical data delivery
but not automatic display rotation.

The same boot's independent two-amplifier microphone correlation passed for
both Amp0 and Amp1 without clipping or fault. Owner listening had already
identified Amp0 as top and Amp1 as bottom; ordinary desktop loudness remained
too low at the 768 fixed ceiling.

The next candidate installs the reviewed sensor runtime only during protected
RAM bring-up, starts the restricted file service before SensorProxy after ADSP,
and disables GNOME orientation lock. A new bounded desktop check requires three
accelerometer orientations and multiple Mutter monitor transforms. It also
raises only the RAM desktop amplifier ceiling to 896, retaining 11.921875 dB
of attenuation beyond the signed profile and leaving GNOME/PipeWire as the
user volume control. The fixed 640 acoustic precheck and all cleanup gates are
unchanged. Desktop audio first creates the reviewed ALSA PCM through
`spa-node-factory`, with the card path quoted for `pw-cli` property parsing,
and requires it to remain for six seconds. If WirePlumber still removes it, a
temporary `module-alsa-sink` is loaded through the explicit user Pulse socket;
the image pins `pulseaudio-utils` so this path is self-contained.

Both WiFi stages pass through an explicit band profile, DHCPv4, default route
and LAN HTTP, then verify the actual nl80211 frequency. Cached BSSIDs are not
pinned: repeated tests showed a stale cached BSSID caused association timeouts
even while the live target remained present.

Fresh Actions and one combined RAM test are required. See
SENSOR-DESKTOP-AUDIO-20261028.md.

## Desktop volume candidate held after joint regression, 2026-10-28

The first follow-up build atb4f423de failed while downloading BusyBox and
the RPC source archive: both reported TLS unexpected EOF before the affected
compile stages. Pinned downloads now retry transport failures at most three
times and use a persistent SHA256-addressed cache. Cache bytes are rehashed,
downloads and destination replacement are atomic, and a checksum mismatch
does not replace the prior destination. TLS and archive checks remain enabled.
404 local checks completed without failures (one environment skip). A fresh
complete Actions run is required for this build-transport change.

Actions40685517582 at13bfebfe passed all five jobs. The single RAM round
returned to Android in444.3s with seven matching baselines, no physical writes
and clean full-history kernel gates. Microphone, quiet PCM, Docker, both WiFi
bands, project Mesa/GNOME, Dock, Chinese/SSH, Bluetooth and battery checks passed.
However the initial default accelerometer lookup returned zero UIDs, so no
sample stream or owner posture window started. Its cause is not established.
The quiet1kHz muted baseline was about ten times the earlier ambient level;
Amp0's active response stayed similar but failed8x contrast. Amp1 passed and
there was no clipping, fault or cleanup failure. The PipeWire window was
therefore skipped. This candidate does not replace the accepted2457ac35 image.
See evidence/DESKTOP-VOLUME-HOLD-20261028.json.

The follow-up permits one empty-default-UID recheck only after a normal exit
with exact three zero-enable/zero-disable/zero-count receipts and clean local
stop, within the original16s total process budget and the same reverse attach.
The first failure is retained privately; any partial stream, crash, malformed
receipt or unrelated failure remains ineligible. The acoustic fixture changes
from-18 to-6dBFS at the unchanged640 test level, still at least42dB below a
full-scale stock-profile signal and quieter than the owner-confirmed0dBFS
fixture. The8x contrast and clipping gates are retained. Fresh build and joint
testing are required; no old failure is reclassified as success.

## Owner-assisted speaker, rotation and desktop acceptance, 2026-10-28

The owner tested the unchanged2457ac35 microphone boot in one20-minute RAM
session. Three rotation cycles and maximized windows retained the Dock and
login; GNOME Shell kept the same PID and GDM had zero restarts. Chinese UI and
physical touch were confirmed. At the earlier640 amplifier level the-18dBFS
fixture was inaudible. Raising only the PCM fixture to near0dBFS established
audible but very quiet output. Three isolated4s/3s/4s rounds let the owner
confirm Amp0 is the top speaker and Amp1 the bottom. This accepts both physical
outputs at that test level, not normal desktop loudness or speaker protection.
Android returned with seven matching baselines and zero physical writes.
See evidence/OWNER-MANUAL-20261028.json. The earlier acoustic evidence now names
the actual microphone alternative boot and its hash, separately from default boot.

The owner posture attempt stopped before sensor activation because wireless
and audio were already active. The reported lack of autorotation is therefore
not an axes test. The next joint order puts sensors first. An explicit
`ONEPLUS13_OWNER_POSTURE_SECONDS=12` adds a same-connection posture observation
within the existing30s proxy cap; default behavior and cleanup remain intact.
Physical axes, compass calibration and continuous integration remain unaccepted.

A new desktop speaker candidate reuses the original project's UCM/PipeWire
approach with this phone's Secondary MI2S SD1 and two amps. The unchanged256/640
checks remain; a768 ceiling retains23.986dB attenuation beyond the stock profile,
about12dB louder than640. UCM applies that fixed ceiling and PipeWire software
volume attenuates beneath unity, so GNOME's volume and mute control output.
The candidate is default-off, explicitly enabled only after independent native
capture/acoustic checks, with reversible WirePlumber configuration. It still
requires fresh Actions and joint owner validation. No dynamic protection or
normal desktop audio qualification is implied. Shanghai timezone is now staged;
the existing explicit RAM clock bridge passed without any RTC write.

## Microphone, two-amplifier acoustics, Dock and sensor joint pass, 2026-10-28

Complete Actions40677232016 at source2457ac35 passed all five jobs. One RAM
boot then passed native WCD capture: both48kHz S24_LE channels delivered96,000
frames without clipping, with route, gain and capture controls restored and raw
audio deleted. ABL's exact C.93 Sun MTP,dodge identity and live1.2V PX,2.7V
microphone bias, GPIO101 reset and TX3 wiring all validated before activation.

The bounded acoustic test uses the unchanged640 ceiling and a fixed-18dBFS
1kHz/1.5kHz stereo fixture. Independent captures prove Amp0 and Amp1 each
produce a correlated response above the8x muted threshold: Amp0 reached
77.4x/9.27x across the two microphones; Amp1 reached94.9x/6.86x with at least
one valid near-field microphone. Both simultaneous-response frequencies also
passed. Amplifier state sampling showed no faults, controls returned to mute,
transports stopped, and no raw audio was retained. Human listening, ordinary
desktop playback and dynamic protection remain unaccepted.

SensorProxy passed the image's922 reviewed text inputs and10 native files,
three-vector sampling, three D-Bus claims/releases and live updates (102 gyro,
two accelerometer posture and nine compass). Docker passed real isolated bridge,
DNS, NAT and published-port traffic; both WiFi bands completed DHCP, default
route and HTTP200 (5240MHz and2437MHz). Project Mesa/GNOME, touch discovery,
Bluetooth/OBEX, battery, Chinese/SSH and the visible-left Ubuntu Dock contract
were retained. Android returned in435.4s with seven matching baselines, zero
physical writes and all13 kernel-health phase gates passing. See
evidence/MICROPHONE-AMPLIFIER-DOCK-20261028.json.

## Prior self-contained sensor samples and D-Bus joint pass, 2026-10-28

The d353ba17 joint round validates native WCD capture: both48kHz S24_LE
channels delivered96,000 frames with no clipping, and every control restored.
Both WCD SoundWire components bind and the corrected live power/reset/port
properties match. The same-PCM muted/live test at640 produced a12.1x/67.6x
880Hz microphone response for channel1; channel0's440Hz result failed the8x
gate. This is not two-speaker acoustic acceptance. The next test retains the
gain and threshold, changes to1kHz/1.5kHz voice-band tones and records bounded
time/frequency summaries before deleting raw audio. All retained targets passed,
including SensorProxy, quiet PCM, Docker, both WiFi bands, desktop/Chinese/SSH
and the live Ubuntu Dock gate. Android returned in424.5s, baselines matched and
physical writes remained zero. Normal desktop audio is still disabled.

The owner-reported missing side taskbar is now addressed explicitly. Live
inspection found `ubuntu-dock@ubuntu.com` enabled/running without an error, but
the distribution defaults retain `intellihide=true`; focused/maximized windows
and rotation can therefore make the dock appear absent. Session bring-up now
enables the extension, sets `dock-fixed=true`,
`autohide=false`, `intellihide=false`, left position and extended height, and
the desktop checker reads all four keys back exactly before accepting the
session. The contract is tested in source; physical post-rotation appearance
still needs the next RAM boot.

The b2669d87 joint round passed SensorProxy, native microphone capture, quiet
PCM, Docker, both WiFi bands, desktop/Chinese/SSH and the new Dock gate. Its
acoustic checker did not play at the higher test level: the9-second default
`arecord` buffer did not expose initial frames within the3-second startup
wait. The next candidate uses1024-frame periods with a4096-frame buffer and a
6-second readiness bound, and retains the capture stderr in RAM for diagnosis.
Android returned in422.8s with matching baselines and no physical writes.

The firstf37017bc microphone-alternative round stopped before loading the WCD
drivers: ABL rewrites the root compatible/model to the exact C.93 Sun MTP,dodge
pair, whereas the new check expected the source DT's OnePlus identity. A guarded
live read confirms the alternate sound-card model is correct. The check now
accepts these two exact identity pairs and independently validates live1.2V PX,
2.7V biases, GPIO101 reset/provider and TX3 port before driver activation.
Negative controls reject the Pad identity and altered power/reset/port wiring.
The round retained sensors/D-Bus, Docker, both WiFi bands, desktop/Chinese/SSH;
Ubuntu Dock is running/enabled with no extension error. Android returned in
405.3s with matching baselines and zero physical writes. This was not a microphone
or acoustic pass;81262980 remains the fully accepted joint image.

Complete Actions40650704909 at source81262980 passed all five jobs, then one
joint RAM boot passed the image's own922 reviewed text inputs and fresh native
runtime, three-vector samples, and actual SensorProxy D-Bus claims, updates
and releases. The connection observed101 gyro updates, two accelerometer
posture updates and nine compass updates. Both services stopped cleanly and
temporary integration was removed. No private host sensor archive was used.

The same boot retained quiet nonzero PCM/amp switching, delivered Docker VFS
defaults with real bridge/DNS/NAT/published-port traffic, both WiFi bands,
project Mesa/GNOME, touch discovery, Bluetooth/OBEX, battery, Chinese and SSH.
Android returned in382.9s with seven matching baselines, no physical writes
and all13 kernel-health phase gates passing. This is the latest fully accepted
joint image. See evidence/PUBLIC-SENSOR-PROXY-20261028.json. Continuous sensor
autostart, physical axes and human acoustic acceptance remain separate work.

## Separate microphone and acoustic candidate, 2026-10-28

The complete build now additionally produces a manual microphone boot image
with the same fresh kernel, initramfs and rootfs as its default speaker image.
Only the audio DT changes: correct1.2V WCD PX, owner2.7V microphone biases,
AMIC1/5 routes and S24_LE TX3 capture. A combined topology preserves S16_LE
Secondary MI2S playback. New bounded checks restore controls and delete raw
RAM audio. The acoustic checker requires successful independent capture, then
compares left440Hz/right880Hz PCM with volume0 versus640; the -18dBFS stimulus
retains at least54dB attenuation relative to the profile's full-scale signal.
The existing256-level regression and default mute remain. Dynamic protection
and ordinary desktop playback remain unaccepted. Full Actions and one combined
microphone/acoustic/sensor/container/radio/desktop boot are required. See
MICROPHONE-20261028.md.

## Historical self-contained runtime regression, 2026-10-28

Complete Actions40646323627 built source941d4eb7 successfully, but its joint
RAM test rejected the sensor file server: it exited4 before a reverse attach.
The new runtime builder had omitted all ten phone-only RPC patches, including
the required default-off -W RAM backend. Replaying the delivered daemon's CLI
on the build host reproduces invalid option W and exit4 without any device.
The builder now reuses build-phone-rpc.py, requires its15-patch provenance and
all14 release plus14 sanitized wire/storage tests, and checks the delivered
-W parser against an absent path before exporting the runtime. A new complete
Actions build and joint hardware regression are required.

The failed sensor round still passed Docker's delivered VFS defaults and real
bridge/DNS/NAT/published-port tests, bounded quiet PCM, both WiFi bands and the
retained desktop/Chinese/SSH targets. Android returned in323.1s with matching
seven-key baselines, zero physical writes and passing kernel-health gates.
Source46f34674 remains the last fully accepted joint image;941d4eb7 is not a
replacement for its accepted sensor capability.

## Docker bridge and quiet nonzero PCM qualified, 2026-10-28

Image source46f34674, complete Actions40641271075, passed one combined RAM
boot and returned to Android in349.6s with seven matching baseline properties
and zero partition writes. Real Docker containers passed bridge HTTP,
embedded DNS, off-bridge masqueraded HTTP and a peer's published-port HTTP
with userland-proxy disabled. Both legacy tables and the distribution's nft
backend worked. VFS/IPv4 is qualified; overlay2 and IPv6 traffic are not.

Both AW88461 amplifiers switched during a fixed two-second -18dBFS PCM within
the existing256 ceiling, then returned to volume0 and powered off. This
qualifies bounded nonzero transport, not audible output or dynamic protection.
Three-vector samples, both WiFi bands, project Mesa/GNOME, touch discovery,
Bluetooth/OBEX, battery, Chinese/input-source defaults and actual SSH login
were retained. Every full-history health gate passed. See
evidence/CONTAINERS-QUIET-PCM-20261028.json.

## Self-contained sensor runtime and D-Bus candidate, 2026-10-28

New Actions steps build the original hexagonrpcd and SSC-enabled SensorProxy
with corrected phone libssc, plus a bounded persistent-connection D-Bus client.
Native and sanitized fake-bus tests exercise actual GIO requests, streaming
properties and three matching releases, including a stationary face-up phone
and malformed vectors. No metadata executable gains a stream capability.

An explicitly reviewed922-file text dataset excludes the import ledger and
serial records. The complete image now carries the fresh native runtime,
data, tracer and bound helper inputs; image-sensors-check.py can select
metadata, samples or a bounded proxy test without a private host archive.
The proxy leaves autostart off, uses temporary RAM integration and requires
real hardware validation. Docker also receives explicit VFS defaults for the
RAM root. A new complete Actions build and joint boot remain required.

## Container dependency closure and quiet PCM candidate, 2026-10-28

The actual previous kernel lacks NF_NAT, NF_TABLES and the new legacy evaluator
switch. The phone fragment now enables both legacy and nft-based IPv4/IPv6
Docker bridge dependency paths. Resolved Kconfig and delivery checks are added,
along with the real engine and an isolated RAM bridge/DNS/NAT/port-mapping test.
The speaker checker can additionally generate a fixed two-second -18dBFS tone
within the existing quiet256 ceiling and restores both amplifier volumes.
No audible-output or dynamic-protection acceptance is claimed. The original
Pad feature comparison and pending phone-specific steps are recorded in
CONTAINERS-20261028.md. Full Actions and a combined phone boot are pending.

## Joint speaker, sensor, WiFi, desktop, and localization pass, 2026-10-28

One RAM boot at image source54fdf46f completed every requested target and
returned to Android in336.8s with matching baselines and zero physical partition
writes. Both AW88461 amplifiers stayed active during a maximum-attenuation
Secondary MI2S SD1 S16_LE 48kHz stereo digital-zero PCM, then stopped and
restored the route. Five-Hz bounded samples completed for accel, gyro and mag,
with every amplifier/sensor unit disabled afterward.

The same boot passed 5GHz association at5240MHz and2.4GHz association at2437MHz,
both with DHCP, default IPv4 route and owner-LAN HTTP200. Adreno830 renderback,
ordinary-user Wayland GNOME, project Mesa, touch-device discovery, powered
Bluetooth with OBEX sender and battery telemetry were retained. Chinese session
locale, exactly one libpinyin source plus US keyboard, sshd and a real
password-authenticated Chinese SSH login passed. Every recorded kernel health
count remained zero. See evidence/JOINT-ACCEPTANCE-20261028.json.

This accepts the silent speaker transport and bounded sample diagnostics. It
does not accept audible playback, dynamic speaker protection, physical sensor
axes/calibration, ambient light, physical touch response or Bluetooth peer
receipt. The tested image itself was produced by the five-job GitHub-hosted
ARM64 Actions run and its boot image and rootfs hashes are recorded in the
evidence file.

## Native amplifier inventory and exact I2S mapping, 2026-10-28

Complete Actions40615700391 passes at e539f11e. One RAM boot confirms both
native AW88461 devices (PID0x2308), profile binding, channel0/1, power-off,
volume0 and attenuation1023. No PCM or gain change occurred. Android returned
in168.4s, seven baselines matched and physical partition writes remained zero.
All recorded kernel health counts are zero. A host cleanup bug treated the
successful transient audio unit's automatic collection as failure; later
WiFi/GPU/desktop/Chinese/SSH regressions were therefore not executed.

SSC numeric evidence now confirms default ambient_light UID count0 and the
single non-default query count0. Accel/gyro/mag each have an available sensor
with a mount matrix. This closes the discovery-stage ambiguity; it does not
establish an ambient-light replacement or accept any samples.

Host-only parsing of the exact C.93 ODM ACDB with Qualcomm's published table
layout identifies Secondary playback SD1(enum2) and feedback SD0(enum1).
The inherited speaker draft's zero selector was invalid. Both phone speaker
graphs now use SD1; their decoded hardware tuples are checked. Separate5Hz,
3-second three-vector diagnostic, guarded actual-send/decoder tests and image
packaging are added. A new complete Actions build and combined PCM/sample/
preserved-feature RAM boot are required. Ordinary playback, protection and
ambient light remain unaccepted. See evidence/AUDIO-SSC-INVENTORY-20261028.json
and evidence/AUDIO-I2S-OTA-20261028.json.

## Speaker and sensor joint candidate, 2026-10-28

Both stock amplifier IDs are now observed as0x2308. The owner C.93 full-package
payload is verified and identical to the previous extraction. The new manually
gated AW88461/Secondary-MI2S candidate includes matched generic ACF and a bounded
maximum-attenuation digital-zero checker, with nonaudio DT properties preserved.
Sensor lookup counts and per-candidate availability now have explicit numeric
diagnostics and a16-UID bound. The phone fallback no longer alters the shared
Pad recipe. Offline checks pass; full Actions and joint hardware are pending.
See `AUDIO-SENSOR-RAM-20261028.md`. Audible playback and sensor streams remain
unaccepted.

## Joint WiFi, desktop, and fused ambient-light boundary, 2026-10-28

Source `5d1fa4f8254870c59858225c3b1f9da98b8058a8`, complete Actions
[40558128204](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40558128204).
The single joint RAM boot returned to Android in 225.1 seconds with matching
baseline metadata and zero partition writes. The complete kernel history had
zero IOMMU faults, panics, OOMs, GPU faults, WLAN restarts, ath12k failures,
invalid runtime IDs and VDEV failures.

5 GHz passed a directed scan, association at 5240 MHz, IPv4 addressing, default
route and interface-bound owner LAN HTTP 200. 2.4 GHz passed the same pipeline
at 2437 MHz. The read-only cache simultaneously contained both targets. The
project Mesa 26.2.3 renderer, ordinary user Wayland GNOME session, settings
process/bus, touch-device discovery, Bluetooth power and OBEX sender, battery
telemetry and regulatory facts were retained.

The saved SSC output establishes ambient_light unavailable, while accel, gyro
and mag are available. It does not retain default/non-default UID counts or
per-candidate attributes. The earlier claim of a nonempty non-default response
and exhaustive unavailable candidates exceeded that evidence and is corrected
here and in `evidence/SENSOR-AMBIENT-20261028.json`. Android independently calls
its active light `OPLUS Fusion Light Sensor Next Gen`; this is not proof of the
SSC flags or that a separate fusion implementation is necessary. Add numeric
discovery-stage diagnostics before choosing that implementation. Overall joint
acceptance remains false and no sensor samples were obtained.

## Chinese desktop and SSH defaults, 2026-10-27

The image now pins Ubuntu's Simplified Chinese language packs, GNOME Chinese
translations, Noto CJK fonts, IBus and libpinyin. System and user-session locale
defaults are `zh_CN.UTF-8`; the qualified RAM user receives a Chinese
AccountsService locale and an XKB US plus `libpinyin` input-source pair. The
input method libraries and environment are installed by default rather than
requiring a post-install download.

OpenSSH Server is installed and enabled at boot. Password and public-key login
remain available to the ordinary test user, while root login is prohibited.
Host keys are removed from the image and generated again at runtime before sshd
starts, so the public artifact carries no shared SSH identity. Verification
requires the actual built package set, locale generation, service configuration,
live service readiness and host input before acceptance.

## GNOME rotation re-login root cause, 2026-10-27

Owner rotation testing exposed two reproducible GNOME Shell exits. The GDM
journal identifies a fatal Mesa 26.2.3 release-build assertion:
`src/compiler/glsl/ir.cpp`, `ir_constant::is_value(float, int)`, followed by
signal6. Autologin itself was configured correctly. GDM therefore recovered to
a greeter, which looked like a re-login rather than a compositor crash.

Disabling Ubuntu Dock and animations did not stop the crash. A RAM-only control
using the distribution's Mesa 26.0.8 kept the Wayland user session active after
another owner rotation. The temporary control disabled Ubuntu Dock so its
temporarily absent sidebar was expected and is not part of the fix.

Installed desktop Mesa builds now use `b_ndebug=true`, matching Mesa's normal
production release semantics: the existing unsupported-constant fallback
returns false instead of aborting the graphical session. Probe and GPU diagnosis
profiles remain assertion-enabled. The Freedreno A830 device support and the
project Mesa payload remain present. Packaging rejects a desktop build without
the release flag. A new exact image and repeated owner rotation are still
required before accepting this fix.

## Dual-band WiFi and joint hardware regression, 2026-10-27

Source `976718cb9ef7007235d161f7deaaec5cbf55a258`, complete Actions
[40510928607](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40510928607).
The single joint RAM boot returned to Android in 276.7s, with all seven baseline
properties equal and zero partition writes. All recorded phase health checks
contained zero IOMMU, panic, OOM, firmware crash, WLAN restart, invalid runtime
ID, VDEV and ath12k failure counts.

The pre-PHY hold preserved the USB exclusion, kept all WiFi unmanaged until the
PHY appeared, and prevented the earlier automatic-scan race. Only then did the
helper apply the fresh stock CN observation; the selected self-managed PHY
acknowledged CN, the hold was released, and no SAR/channel override occurred.
The received source-current scan-priority serialization remained active.

5 GHz passed a real directed scan, association at 5240 MHz, IPv4 address,
default route and interface-bound owner LAN HTTP 200. 2.4 GHz passed the same
pipeline at 2437 MHz. The read-only cached list concurrently contained both
targets and 44/45 AP rows across 2.4 and 5 GHz. This establishes the two bands
for this image and test location; it does not claim every band, DFS channel,
rate or regulatory domain.

The same boot passed Adreno 830 render/readback with project Mesa, an ordinary
user Wayland GNOME session with repeated settings-process/bus samples, touch
input device discovery, powered Bluetooth with address and OBEX sender,
regulatory channel enumeration, and valid battery level/temperature. Physical
pixels and touch response were not observed remotely; Bluetooth peer receipt was
also not exercised. Those remain explicit hardware acceptance gaps.

SSC again enumerated accel, gyro and magnetometer, while ambient_light remained
unavailable; all four metadata operations completed, no samples were requested,
and both units stopped. Therefore `joint_acceptance_pass` remains false even
though `wifi_dualband_pass` is true. Do not rewrite the older failed runs: they
remain the evidence history for the scan timeout and host-clock correction.

## Host-clock freshness correction after first combined round, 2026-10-27

The current `1dd42257...` image completed a RAM boot and returned to Android in
199.8s with matched baseline metadata and zero partition writes. The 600-second
timer was verified at runtime. SSC metadata and cleanup completed. Before WLAN
PHY creation, the quiescent helper installed and reloaded the strict hold; the
kernel remained free of DMA, panic, WCN7860 failure and restart signatures.

The stage stopped because the RAM guest's wall clock is not synchronized. Its
local `time.time()` compared the new Android observation with the wrong epoch
and called it stale. The country hint and every manual WiFi command still did
not run. Bind observation freshness to the validated host epoch already used by
the ordinary WiFi checker, require that clock explicitly, and add a regression
that rejects missing, future and over-one-hour-old host clocks. The failed trace
also confirms the hold exists before the PHY and that both USB and all WiFi are
excluded from NetworkManager while the PHY appears.

The next single joint plan uses a separate evidence directory so the consumed
single-use ledger remains immutable. Preserve the first round's clean kernel
and hold evidence. Rebuild from the corrected source so the installed helper
matches online Actions before retrying the combined WiFi/SSC/desktop round.

## Scan priority serialization and exact event meaning, 2026-10-27

The pinned wmi.h defines event16 as DEQUEUED and reason1 as CANCELLED.
The third round therefore observed a firmware queue cancellation followed by
the driver's start wait timeout, not event64 START_FAILED / reason4 INTERNAL_FAILURE.
Do not infer firmware crash or a regulatory root cause from those numbers.

Inspecting the actual scan-start function exposed a separate concrete bug:
it computes LOW/MEDIUM priority but never assigns cmd->scan_priority. The
one-line fix from [ROCKNIX PR3189](https://github.com/ROCKNIX/distribution/pull/3189),
head `8638e1d190de05ec0fd518b7cb9a886aa77dbd20`, applies unchanged.
Preserve Edouard Durand's original attribution and sign-off. This sends the
existing driver policy; it does not raise priorities beyond that policy or
disable 11d. The primary WCN7860 issue398 reports that this fix alone did not
eliminate early missing 5 GHz, so it is not a complete solution claim.

A host test compiles the actual scan-start header block and actual enum
definitions, preserving header IDs/flags and checking LOW/MEDIUM little-endian
values. Release and ASan/UBSan pass. Removing the actual assignment reproduces
SIGABRT in a required negative control. This compiles a block, not the entire
function or a firmware scheduler. Full ARM64 compilation remains mandatory.
A second phone-only diagnostic shares the existing 32-row numeric budget and
records the serialized header priority and 11d state for the joint boot.
Combine this with the default-off quiescent initialization, SSC metadata and
all preserved-feature regressions; no isolated priority-only phone test.

## Measured transport speed and complete server integration, 2026-10-27

Actions [40500971360](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40500971360)
at `e3c4c8369fef4d71b2234db2632fcd2cc700ecf8` built kernel, rootfs,
Mesa and SSC. The cold parallel prefetch downloaded 364427236 bytes / 727 debs
in 108.8s, with zero cache hits, compared with 38m23s in the earlier APT log.
Installation took 70.217s and compression 29.532s; the public cache saved.

Assembly exposed a server environment dependency: `make modules_install`
only warned that depmod was absent, returned success and omitted module indexes.
The server kernel archive was therefore unusable and no phone boot was made.
All phone kernel workflows now explicitly install kmod, the builder requires
depmod before compiling and passes its exact path, and artifact verification
requires text/binary dependency and alias indexes plus a complete in-payload
dependency graph. The actual failed server archive is rejected; native depmod
regeneration on those actual ARM64 modules passes the corrected verifier.
Three regression tests cover missing indexes and invalid/incomplete graphs.
The corrected complete Actions build remains required before a new phone boot.

The owner suggested a longer live diagnostic window. The next single-use
combined RAM plan has a fixed 600-second cap, with explicit clearing of inherited
timer triggers and D-Bus readback of the actual merged timer. It never renews
the deadline. Kernel/network/desktop evidence is read while Linux is running;
critical DMA/panic/restart faults require early recovery. Only the volatile
test override changes: the delivered image's default remains 300 seconds.

## Full snapshot URI compatibility, 2026-10-27

The first accelerated CI trial rejected APT's legitimate percent-escaped `+`
and `~` in package versions before downloads. It did not weaken package hashes.
Decode paths for validation while still rejecting traversal, encoded separators,
foreign origins and unsupported hashes. A metadata-only isolated APT resolution
using all twelve SHA256-verified indexes from three GPG-verified InRelease files
now accepts all 727 resolved package rows, including 86 escaped URLs. No packages
were installed. Eight prefetch tests and a new actual-health-classifier control
pass. CI retains its public URI plan and timing report even when the job fails.
Full rootfs performance remains pending the corrected Actions run.

## Rootfs transport and third joint round, 2026-10-27

Full Actions [40491459981](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40491459981)
at `2218dcaaf2f55c4a5505f54e5c63d2f3a41f7e1b` passed all jobs.
Its rootfs log records 364 MB downloaded in 38m23s (158 kB/s), about 72s
installation and 30s compression. Transport dominated the 41m18s job.
The fixed, signed Ubuntu snapshot and all package choices remain unchanged.
An APT SHA256 URI plan now drives eight bounded concurrent HTTPS downloads;
only verified bytes enter the archive directory, followed by APT --no-download.
Public deb caches survive transient failures and are rehashed against each
fresh signed plan. Logs emit bounded progress every ten seconds. A real
snapshot package, cache reuse and native APT archive-filename acceptance pass;
seven host checks cover malformed plans, bad bytes and links. Full CI timing
at the new implementation remains to be measured.

Same-commit build steps measured hosted/server: kernel 625/367s, Mesa 172/43s,
SSC 29/6s. The complete workflow now has an opt-in `use_server` input for
kernel/Mesa/SSC. Rootfs and final assembly remain on hosted native ARM64.
Shared APT locks, four kernel jobs and a job-local SSC venv avoid conflicts.
All image dependencies remain same-workflow and same-commit artifacts.

The third joint RAM boot returned to Android in 225.1s, with seven baseline
properties equal and zero partition writes. SSC again found accel/gyro/mag,
but not ambient_light; no measurements were requested. During qualified
feature startup, NetworkManager's automatic scan triggered the health gate
before any manual WiFi connection. Retained numeric trace shows successful
2.4 GHz completion, then a 5180--5320 MHz request, firmware event type16
reason1 and next-range start timeout -110 (three failures in the retained
tail). No IOMMU fault or hardware restart appears in that tail. Hold this
candidate; mutex and matrix corrections do not establish 5 GHz acceptance.
Desktop/touch/Bluetooth regression was not completed; do not promote it.

A default-off, explicitly invoked RAM helper now prepares NetworkManager
before any WLAN PHY exists. It appends a strict WiFi unmanaged rule while
preserving the USB exclusion, checks effective config, binds a fresh exact
stock 5 GHz/country observation, checks disconnected state before a single
normal country hint, and requires acknowledgment from the selected self-managed
PHY. Each command is health-gated; any failure requires recovery. It does not
override channel flags, firmware, SAR or calibration and never retries/reset.
Six source tests and the real native NetworkManager config parser pass. This
is a hypothesis for the next combined test, not a working 5 GHz claim. The
ordinary WiFi checker continues to refuse country transitions; no autostart
or previously qualified default behavior is changed by this opt-in tool.

## Scan timeout lifecycle follow-up

The community range fix was subsequently reconciled with an upstream v4 scan
timeout correction in [Armada PR 736](https://github.com/armada-os/armada/pull/736),
head `21316f049f1424f621a79d08981af831f8339588`. Its prerequisite is
[PR 601](https://github.com/armada-os/armada/pull/601), head
`163886ffbe1cc44f400540d1ffd0b8d235a03f6f`: synchronous cancellation while
holding the wiphy mutex can wait for a timeout worker blocked on that mutex.
Preserve Runyu Xiao's patch attribution and use the reconciled range/TX patches.
All three primary-source patches apply cleanly to the pinned ath12k files;
the numeric diagnostic patch needs only a context refresh in core.h.

The source check now compiles nine actual helpers, including completion and
abort. Intermediate range completion retains the overall timeout; final queued
completion suppresses a racing abort. Release and ASan/UBSan pass, and removing
the actual finish guard reproduces the failure in a negative control. Native
kernel compilation and a joint phone test remain required. This is a real
lock-lifecycle correction, not proof of the cause of the observed start timeout.

The owner's ARM64 server handoff has been read. Its trusted self-hosted
component workflow is retained and runs at the same branch commits. It builds
kernel/Mesa/SSC, while mount-dependent GNOME and final image jobs remain on
hosted native ARM64 runners. Use measured warm-cache timings when choosing;
the earlier cold-build comparison does not guarantee every rebuild is faster.
Server addresses, passwords, proxies and private handoff text are not published.

## Complete Actions image and second joint round, 2026-10-27

Source `18f59c902bb3912dbd1912ece99a03fe4f4e9884`, Actions
[40467791503](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40467791503)
built all kernel/GNOME/Mesa/SSC/image jobs successfully. Downloaded final bytes,
all 71 firmware files, module release, qualified DTB and full native helper
were independently read back and verified. Actions is the faster current path.

Its single joint RAM boot returned to Android in 258.1s, with seven baseline
properties equal and zero partition writes. 5 GHz target remained absent.
2.4 GHz associated at 2437 MHz and obtained IPv4/default route. LAN HTTP timed
out; post-return host preflight found the owner's host endpoint was not running.
That is a missing test prerequisite, not evidence that RF data transport failed.
The next runner must establish and self-check a bounded host LAN HTTP fixture.

SSC directly captured accel/gyro/mag available, ambient_light unavailable, all
four completed, and both units stopped. No samples. Hardware Adreno 830 render
readback passed; the ordinary user Wayland/settings session exited during its
stability check. Do not inherit historical full desktop acceptance for this image.

No IOMMU faults or hardware restart signatures were found in full-history
checks, but retained logs show repeated `failed to start next scan range: -110`.
The previous health classifier missed this new scan error; its zero counts do
not qualify the scan. Hold this candidate. Generic ath12k failure and OOM gates
now supplement the earlier signatures. Keep firmware/regulatory/DTB inputs fixed.
The next phone-only patch retains at most 32 numeric scan request/event rows
per radio to establish the first failing range and firmware event sequence.

An independent SSC draft demonstrated another actual bug: integer accumulation
misclassifies valid floating mount matrices as all zero. A regression injects
synthetic protobuf attributes into the real receive callback. The old code fails;
the correction preserves nonzero matrices and retains the genuine zero fallback.
Release and ASan/UBSan pass. This neither establishes phone axes nor enables streams.

## Continuation: scan recovery and SSC metadata, 2026-10-27

First joint RAM round returned to Android in 268.1s; seven baseline keys
matched and no partition writes occurred. 5 GHz target absent, 2.4 GHz
activation timed out. Full retained-log audit found IOMMU faults and WLAN
restarts missed by the initial narrow signature screen. Candidate held;
country-transition experiment withdrawn. Two attributed WCN7860 firmware-range
scan/TX patches are now a build candidate with actual-helper host checks.
No 5 GHz acceptance or clean hardware result is claimed.

SSC property fix exposed accel/gyro/mag metadata; ambient_light remains
unavailable, based on an exact saved-stdout SHA256/public-template match.
No sensor streams. Failure summaries now preserve only exact public type
results. Full-source kernel/Mesa/SSC Actions builds passed; GNOME snapshot
provider failures still prevent a fresh complete image. See
DUALBAND-SSC-20261027.md for evidence limits and combined acceptance.
Display/GPU/touch/GNOME/Bluetooth/battery inputs remain regression requirements.

## Previous: complete CI image data included, 2026-10-27

Run90 passed actual RAM WiFi scan/authentication/DHCP/default-route and
interface-bound LAN HTTP 200. It automatically returned to Android in 109.2s;
seven baseline properties matched, with zero partition writes. The 316 Linux
unit checks pass (one root-only case skipped in the non-root invocation).

The owner now explicitly authorizes publishing firmware and calibration, while
excluding credentials, keys, personal data and device identifiers. The reviewed
74-file qualified-data set is included in Git; old DTB boot arguments were
removed, and hashes and identifier exclusions were checked. Actions builds the
kernel, GNOME and Mesa at one commit, packages all hardware data, and emits the
complete RAM boot image plus matching rootfs. No local owner data or secrets
are needed for the build. Firmware remains proprietary prebuilt data.

By owner request, QEMU is optional and disabled by default. Static image,
firmware, module, profile and boot-section checks remain required. The new CI
run is pending; compilation is never relabeled as a new phone test. See
SOURCE-IMAGE-20261027.md for the artifact, exact variant and runtime procedure.

Display, GPU, touch, GNOME/settings/keyboard, Bluetooth/OBEX and battery support
are retained. Audio/camera/sensor streams, suspend and new SAR transport remain
unqualified. No flashing, partition changes or persistent install are involved.

### Archived earlier records

The entries below describe historical intermediate states and their previous
privacy boundary. The current publication scope and WiFi result are above.

## Full native entry restored before any new phone boot

The first fresh private package still inherited the obsolete shell diagnostics
entry. It was detected offline: no phone reboot or RAM boot was sent. Run89's
unused ledger is explicitly halted and preserved. The public entry now uses
the complete Python native-desktop implementation plus its kernel-release
stamp, matching the run88 helper body. Packaging rejects a diagnostic stub.
The identity fixture matrix now exercises this actual Python entry point.
A new complete candidate and exact private QEMU check are prepared as run90;
hardware WiFi/HTTP acceptance still requires the registered USB phone to appear.

## Fresh source build qualified, 2026-10-27

Actions 40428687718 at 06fcb43fcaac24a932b9880b5df3097a2d37f686 passed
fresh kernel, GNOME, Mesa, matching-image assembly and complete rootfs QEMU
handoff/deadline. Kernel configuration, full patch and native DTB match run88.
The complete locally packaged private image also passed its actual data
handoff and deadline in QEMU (123.6s). All 311 Linux unit checks passed.
Linux filesystem staging uses native temporary storage so case-distinct
paths are preserved when output is on Windows/DrvFS.

Hardware acceptance of the newly compiled image is pending: the registered
phone is absent from both ADB and Fastboot, and host PnP shows no matching USB
root. No reboot or RAM boot was sent. The prepared unattended acceptance checks
WiFi association, DHCP/route and private HTTP 200 only. Previous run88 hardware
results are preserved, not relabeled as tests of this source-built image.

The source builds every system software component; proprietary firmware and
calibration are mandatory local data inputs. This is not a claim that Linux
source can reproduce those binaries or that private data was published.

## Fresh source build replaces historical artifact retrieval

The source-image workflow builds the kernel, GNOME and Mesa at one commit.
The qualified touch SPI handling and both ADSP patches have been restored.
No source-image hardware acceptance is claimed until its own RAM WiFi/HTTP test.
See SOURCE-IMAGE-20261027.md for public/private input boundaries.

<!-- CURRENT-IMAGE-BRANCH-20261026 -->
## Current image branch qualification

Branch `oneplus13-run88-current-image-v2-20261026` is derived from the public
platform handoff tip. It pins the current kernel integration, Ubuntu GNOME
rootfs and ARM64 Mesa artifacts used by the owner-tested RAM image.

The WiFi acceptance path now checks the owner-supplied private LAN over HTTP
and records external HTTPS and clock delta as diagnostics. On-device run88
passed 2.4 GHz scan, authentication, DHCP, private HTTP 200, external HTTPS
200 with certificate verification, desktop stability, display, GPU, touch,
settings and Bluetooth file transfer. The phone returned to Android with all
seven baseline properties unchanged and zero partition writes.

No LAN address, SSID, password, device serial, private firmware, calibration,
partition image or per-run private evidence is stored on this branch.

<!-- END-CURRENT-IMAGE-BRANCH-20261026 -->

# 一加13适配状态

## Latest: preserve the working features; no full-network delivery yet

The owner requires subsequent images to retain every previously tested feature.
The prior isolated image is a diagnostic draft, not a feature-complete upgrade.
Run82/83 restored the fixed previously tested WLAN/` software/firmware bytes
while replacing reference ADSP/GPU with independently verified phone inputs.
Display, hardware GPU readback, ordinary-user desktop, powered Bluetooth
controller/sender/OBEX, touch-device inventory, battery and read-only platform
regressions passed. They returned automatically to Android in132.1/135.9s with
seven matching baseline properties, zero partition writes and no selected
severe signatures in saved tails. Old stop and firmware-hold records remain.

Run83's one owner-SSID scan and bounded cache observations saw50 AP rows,
39 visible SSID rows and38 unique visible SSIDs. The specified target was not
observed; no authentication/DHCP/HTTPS acceptance is claimed. Raw identifiers,
credentials and scan lists stay private. Complete-network delivery is blocked.
verify-preserved-features.py enforces joint current-artifact evidence rather
than merging historical passes from different candidates. It rejects run83.
Physical touch/visual and peer receipt were not retested unattended.

Full kernel Actions40320714130 passed Image/modules build and exact-image
QEMU smoke checks. Its pinned base/overlay, archive CRC and extracted hashes
were verified locally. It remains offline-only and was not substituted into
the feature regression without a matching prepared desktop image.

## WiFi current result: prepared, not restored

Latest WiFi source4786b1195330f8823c95574cac67ed481b3ae639 passed native ARM64
Actions40319212570:15 codec and29 actual-driver groups in release/sanitized
configurations, plus complete common/WiFi7 family recompilation and both
relocatable composite links with warnings as errors. A separately selected
full-kernel build input now includes this dormant transport in real phone
Image/modules output; it adds no firmware, RF policy or automatic SAR command.

Five exact-phone WLAN files were staged on the host, unmodified and inactive.
The current isolated candidate has no WCN7860 firmware in either rootfs or
initramfs, and its radio nodes/modules remain disabled. No new RAM boot or
current WiFi acceptance occurred. Historical networking results do not cover it.

Bounded Android GET219/GET164 queries reported QCA capability5 (documented TAS),
NONE/empty legacy limits and unresolved CTL grouping, with seven baseline
properties matching and no SET/scan/file write/reboot. Pinned firmware and host
SAR version names/numbering are not fully consistent; do not infer a raw WMI
version or substitute USER/V2 policy. The decoder now retains an OFF/empty
observation while SET-to-NONE is still refused. Effective phone TAS/SmartTx
policy/lifecycle and current-image network acceptance remain open. See
WIFI-DRIVER-DELIVERY-20261026.md. Earlier sections below are historical.

## 2026-10-26 WiFi priority and SAR protocol implementation

Owner has made WiFi the immediate priority. Run66 previously completed scan,
authentication, DHCP and certificate-verified HTTPS using reference inputs;
the current isolated candidate disables radios and has no current WiFi acceptance.
Do not describe the historical network pass as a current usable WiFi result.

New wifi-draft/sar-wire.c implements explicit QCA-to-WMI selection translation,
SET/GET encoding, strict complete readback decoding, unmodified capabilities and
separate SAR2 firmware results. Fourteen real C test groups pass release and
ASan/UBSan/LSan on WSL; encoded SET bytes match the actual extracted pinned
vendor sender. Native ARM64 verification is pending. No transport or power
policy is attached, and no phone RF was enabled. Driver integration, exact
phone firmware delivery and effective policy remain before WiFi RAM acceptance.
See tools/oneplus13/wifi-draft/PROVENANCE.md.

Run81 returned to Android automatically in116.2s with seven matching baseline
properties and zero partition writes. Display/GPU/desktop and two synthetic RPC
checks passed; SSC exited1, raw diagnostics were saved privately, and both units
were inactive with no PID. No sensor stream, camera activation, audio or RF.
The run81 stop and all historical ledgers remain intact.


Actions 40294047744 已成功验证相机/功放联合构建及 7 项相机板级映射契约测试。
原厂 FDT 只读复核结果保留在本地私有输出；私有 FDT、传感器身份和 EEPROM 内容
没有进入公开提交。

## 2026-10-26 相机板级媒体图只读复核

新增 `review-camera-board-map.py`，只读取本地保存的原厂 FDT，不上传传感器
身份、寄存器表或 EEPROM 内容。复核确认四个启用节点的 PHY 顺序为
`[5,1,3,4]`，总线为 `CCI0/CCI0/CCI1/I²C`，供电、时钟、GPIO、姿态字段和
EEPROM phandle 链接均完整。测试覆盖重复索引、错误 PHY/总线、缺电源字段、
未解析 EEPROM、姿态缺失和前置 I²C 地址缺失等拒绝路径。

这只证明板级连接图输入可被安全映射，不证明传感器型号、寄存器初始化、超广角
自定义 PHY、电源时序、ISP/libcamera 或真实拍摄已完成。

## 2026-10-26 联合离线门禁 Actions 结果

公开 follow-up 提交 `b9b2b0687387ffeed8187aeb0b5d65d9e310b72a` 已在独立分支完成。
Actions 40291375012 的 ARM64 SSC/联合控制检查成功，40291375256 的 ARM64
麦克风与扬声器拓扑编译/解码成功；两个运行均为离线构建，未上传私有输入。
新的精确 rootfs QEMU 组合验证尚未重跑，因此不创建新的真机 RAM 启动计划。

## 2026-10-26 联合目标离线门禁继续收紧

新增联合传感器发现运行器：在同一次受控文件服务窗口内仅做一次
UID65534 metadata-only SSC 查询，查询和 systemd 清理均有界；覆盖重复附着、
trace 未就绪/超限、启动/停止超时、非零退出、残留活动和四类元数据不完整。
16 项联合 Python 检查通过，既有文件服务 79 项检查和 SSC 13 项检查也通过。
dummy-virt 组合自测入口已加入精确 rootfs QEMU 组装流程，但尚未重跑新的完整 VM，
因此没有新增真机资格，也没有启用样本流、音频、相机或 RF。

麦克风 TX3 与扬声器 Secondary MI2S 图草案的解码检查现严格核对单一 PCM 能力块：
S24_LE、48kHz、双声道。新增 ARM64 Actions 工作流只编译/解码草案，不安装 UCM、
服务、功放校准或保护逻辑；扬声器仍不能宣称 PCM open 或实际放音通过。

## 2026-10-26 相机/扬声器组件与SSC完整VM通过

Actions40285807929通过10个ARM64组件编译、实际相机PHY函数7类release/ASan+UBSan故障检查及功放实际函数检查。Actions40285807884通过SSC三项release/三项sanitizer及13项运行器检查；完整精确rootfs VM的低权限沙箱、真实超时、交接及自动截止通过，修正此前主机库回退误判。另已按手机OTA独立构建麦克风TX3和扬声器Secondary MI2S图草案，编译/解码通过；未交付手机或开流。详见[本批实际范围与剩余缺口](AV-SSC-OFFLINE-20261026.md)。当前真机仍run79自动回Android，尚无run80计划或资格。

## 2026-10-26 完整VM纠正SSC依赖门禁；相机错误路径修复

完整精确rootfs VM拒绝SSC程序：libprotobuf-c/qmi/qrtr/mbim运行库不在目标镜像，早先QEMU-user的-L检查回退读取了主机ARM64库，不能计精确rootfs通过。旧结果保留并标为被纠正；门禁继续关闭，无新手机操作。独立探测包现显式交付四个通用运行库，记录发行包/源码版本与版权，放在独立probe目录，不替换系统库；等待原生构建及完整VM重新验证。13项运行器控制/故障检查通过。

相机前置代码的-Werror门槛发现两个遗留局部变量，独立修正保持原23补丁不变；进一步修复PHY时序/模式设置失败仍继续配置/上电的路径。提取实际修订函数的7类合成成功/故障在release和ASan/UBSan通过。联合组件构建保留-Werror并一次汇总其他编译失败，同时编译实际手机MCLK依赖CAMBIST。仍不属于相机或扬声器硬件验收。

## 2026-10-26 相机/扬声器组件联合离线构建

相机已找到公开SM8750 RDI实现及其独立PHY、CAMSS外部PHY和Kaanapali前置链，共23个原作者补丁；在实际手机内核pin对应的全新受影响源码上全部fuzz=0应用通过，未改手机DTS。新增隔离构建一次编译CAMSS/CSID980/VFE980/CSI PHY/CCI/CAMCC及现有AW88461功放组件并运行真实功放函数合成故障检查；原生编译尚待结果。手机传感器驱动/供电与媒体图、自定义超广角PHY差异、ISP/用户态及扬声器校准/动态保护仍须完成。入口为tools/oneplus13/camera-draft，未生成或替换启动镜像。

独立SSC发现入口已通过Actions40281827817的3项release/3项ASan+UBSan及精确rootfs中的隔离库链接、锁验证、策略和实际send拒绝测试。未执行QRTR查询；GLib测试只读随机种子/输出终端查询不属于设备激活。原生源范围仍非真实样本验收，服务硬截止/退出门禁待完成。

## 2026-10-26 原项目顺序复核与独立传感器发现入口

已固定原项目227条公开提交，区分麦克风优先、加速度计再扩展其他基本传感器的集成顺序；相机在参考项目未实现，手机扬声器也不能复制Pad六功放/TDM。详见[顺序与当前对照](UPSTREAM-ORDER-COMPARISON-20261026.md)。新增独立metadata-only SSC探测入口，在实际发送边界拒绝测量/订阅，仅容纳严格SUID/属性查询。fresh-tar WSL各3项release/ASan+UBSan及无QRTR锁验证通过，原生ARM64和精确rootfs门禁待完成；尚未交付手机。详见[发现入口范围](SSC-METADATA-PROBE-20261026.md)。传感器样本、麦克风、扬声器、RF和相机仍未完成功能验收，多个合格新目标合并后才审查RAM测试。

## 2026-10-26 run79联合RAM验收完成

三个新目标合并通过：两个原生ARM64合成RAM/wire故障用例在UID65534/设备隔离下运行并退出、相机元数据固定路径实际只读打开、反向文件服务2594次成功调用且无写拒绝/unsupported并干净停止。显示/GPU/普通用户桌面/只读存储/平台健康一起通过，131.7秒自动返回Android且七项基线一致。925个私有数据文件与模块策略未变；缺失31降至30，全部已知。没有刷写、持久安装或人工恢复，历史停止记录和run79单次封存保留。详见[JOINT-RAM-RUN79-20261026.md](JOINT-RAM-RUN79-20261026.md)。下方等待资格/尚未交付均为此前阶段快照；本次并未验收完整传感器、相机、RF或音频功能。

## 2026-10-26 后续联合验收：合成用户态检查与实际只读输入

按机主再次明确的多目标要求，为下一次具体审查准备：将两个已存在的真实C测试单独导出，验证过的FastRPC mock遇调用立即失败；不把测试文件装入生产runtime包。新增有界低权限systemd沙箱运行器，只使用/run合成fixture，隐藏/拒绝设备、无网络、12秒硬截止，异常也请求停止。11项归档/退出控制检查和原6项构建、2项QEMU截止检查已在WSL通过；等待新的原生14项C构建及精确rootfs完整QEMU沙箱/恢复验证，尚无新启动资格。计划合并合成故障用例、实际只读相机输入、服务退出取证及桌面/GPU/平台回归；无线、音频和传感器流仍禁用。

最新离线联合准备已通过：Actions40270669480验证14项release、14项ASan/UBSan C、6项构建和36项服务检查；精确rootfs loader/CLI、私有交付普通UID读取和933个目的路径检查通过。见[BATCHED-RPC-PREPARATION-20261026.md](BATCHED-RPC-PREPARATION-20261026.md)。没有新增RAM启动或run78资格；下方“14项待完成”是此前提交时的状态，现由本条更新。

## 2026-10-26 联合验收准备增加只读相机输入

0009与退出取证修订已由原生ARM64 Actions40269798259验证：13项release、13项ASan/UBSan、36项服务及6项构建检查通过；产物校验和精确rootfs QEMU-user RPATH/loader/CLI通过。另沿本机已保存库实际dispatch核对method33和method9共35条指令，确认重命名三输入/无输出、字符串长度与终止检查，以及seek偏移符号扩展；未执行库。

已有归档找不到的相机输入已在原8h授权内以一次有界Android只读方式复制，186字节且匹配之前的原机元数据哈希，前后七项基线一致；未重启、启动相机、写手机或改变历史锁存。数据和哈希保持本地私有。新增0010仅映射固定虚拟文件名到可选的暂存文件，缺失保持ENOENT，不透传camera目录，且不属于RAM可写命名空间。合成二进制VFS和真实apps_std wire检查读回、NUL、EOF/seek、相邻名/越界拒绝及写入拒绝，fresh-tar WSL 14项release/14项ASan/UBSan通过；新14项ARM64复验待完成。此准备不构成相机或传感器流验收。

27个缺失配置名全部逐字出现在保存的原厂json.lst，其中20个带字面#；对应文件均不存在。原厂DSP解析器的注释语义尚未核实，不改名单、不去#或造文件。Qualcomm参考实现单独容纳oemconfig.so的ENOENT告警，不能据此证明本机可选或传感器成功；两个动态库仍有明确原厂JSON注册，执行/映射继续拒绝。多个目标与回归合并后才审查下一次RAM启动。

## 2026-10-26 多目标离线修订：RAM命名空间、协议、退出取证

按机主最新要求，后续先合并多个已审查目标，再做一次联合RAM验收；不为单个修复重启。新增0009保持此前八个补丁原样：离线真实C测试复现rename后快照复活、缺失源rename耗尽名称表，修复为有界tombstone及提交前检查；同时修复追加创建缺失文件的未初始化索引、失败seed回收、负errno映射和IDL有符号seek。fresh-tar WSL通过13项release与13项ASan/UBSan；完整套件未声明泄漏检查。服务包装器新增非零is-active、停止前查询失败、启动超时仍停止及新版模式拒绝日志检查，36项Python服务检查和6项构建检查通过。原生ARM64复验待完成，尚无新增硬件资格。

run77已自动恢复Android、七项基线一致，服务诊断成功但私有运行器旧文件数断言失败；历史停止锁存保留。31个缺失请求已分类，完整文件服务、传感器流和DSP释放确认仍未通过。现有三个私有归档共17098个索引项未找到相机输入文件的精确文件名；未补造数据或执行动态DSP库。

## 2026-10-26 RPC序列与精确rootfs链接：离线门槛通过

保留原项目已有TYPE_SEQ测试，修复序列首参/独立索引/元数据游标/空序列，并在分配前检查八位buffer数量；未验收输出序列在ioctl前拒绝。10项C release和10项ASan/UBSan、6项Python在native ARM64 Actions40252529300通过。产物CRC/哈希/2个AArch64 ELF复验通过，在精确Ubuntu26.04 rootfs新提取目录中QEMU-user验证正常RPATH、帮助和加载器解析，无设备打开或ioctl。没有替换基准库或手机候选，run73停止状态保留。下面08:50的原9项记录是历史阶段；OEM库、写registry ABI与实际传感器仍未完成，见PHONE-PCB-MAPPING-20261026.md。

## 2026-10-26 手机PCB只读映射及RPC对齐问题：仅离线

按run73真实请求和已保存的本机scalar，新增手机专用虚拟PCB版本只读映射；公共补丁不含值，缺文件仍ENOENT，不透传主机/proc。原五个patch与Pad配方不变。真实C合成输入覆盖精确字节、缺失、EOF/seek、相邻名与越界路径拒绝。

完整ASan/UBSan进一步在原有测试中复现wire-size未对齐存储和packed参数原生指针未对齐读取，并发现测试double的零长度NULL比较/复制。已用保留原布局的memcpy修复运行时代码，并只跳过测试中零字节内存访问，不关sanitizer。九项C检查的release与ASan/UBSan均通过，六项Python配方/归档/环境检查通过，尚待专用native ARM64构建和精确rootfs链接。没有再操作手机，run73停止标记保留。详见PHONE-PCB-MAPPING-20261026.md；这些离线发现不能认作历史真机故障原因或完整传感器通过。

## 2026-10-26 run73：原厂配置实际反向读取，完整文件服务门槛仍拒绝

新的150项ARM64和精确rootfs/umask/真实UID sandbox/300s VM自动截止全部通过后，在原8h授权内经源码绑定的软件故障恢复审查执行一次run73；run72与run69父账本继续halted，没有抹除失败。目录权限问题实机消失，原厂ODM配置通过真实reverse RPC打开读取，保存尾部有37个成功invoke，服务干净停止。完整文件服务仍因缺失lookup与两个写请求被拒绝，134.0秒自动返回Android，七项基线一致，桌面/GPU/平台通过，无流/刷写/人工恢复。run73单次子账本也halted，不直接重试。

保存日志请求27个原厂vendor索引中本就不存在的名字，其中20个含字面#前缀；另有11次OEM/板级数据缺口和两次registry/camera-dump写入拒绝。不可通过去掉#、伪造文件、忽略错误或打开写入权限宣称传感器通过。有限尾日志未包含首次attach/registry的完整trace，不能补推成功。已仅做14个Android只读路径元数据查询：4个存在、10个缺失，基线一致；原始数据私有，未执行库或修改手机。

下一步先离线核对原项目只读文件系统、OEM DSP库/板级映射和写接口ABI；加强失败时完整trace的有界派生事实与退出后保护/字节检查。写请求仍拒绝，缺失/拒绝不计通过；新增诊断不赋予下一轮资格。源码复核同时发现原builder的registry路径带尾斜杠，已按真实路径修正只读trace匹配并补邻近名字拒绝测试，不在真机排查这种格式问题。

离线补充：修订权限版Actions40246612604的148项ARM64和普通rootfs交接通过，但扩大的组装rootfs观察器在native handoff检查180.290秒之后，于180.806秒触发原180秒VM截止，未到新增sandbox成功标志。该门槛仍失败，没有再次上机。仅为dummy-virt专用HTTP观察器预留300秒，手机/rootfs/恢复参数不变，新增两项只允许精确QEMU fixture的检查；等待重跑实际sandbox和自动截止。

## 2026-10-26 run72：文件服务包装目录权限拒绝，自动恢复

run72 桌面/GPU/普通用户/平台回归通过，但低权限strace在启动hexagonrpcd前的stat得到Permission denied，文件服务未通过；101.9秒自动返回Android，七项基线一致，无刷写或人工恢复。已停止该版本硬件重试并保留新窗口停止锁存。

确切执行版在主机复现：交付shell使用umask077，新目录未显式chmod，成为root的0700；此前安装单测的默认umask与QEMU合成sandbox没有覆盖安装目录，留下了这个缺口。修订只为新目录显式设置0755，不放宽任何现存目录，现存不可遍历目录直接拒绝。新增两项Linux场景；QEMU在同样umask077下调用真实安装函数，再由真实UID65534读取公开合成binary路径和0640 registry样本。必须重新通过ARM64与QEMU后才可审查后续资格，不能把上一版sandbox通过当作修订版或文件服务通过。

## 2026-10-26 run70/71：人工桌面与单次传感器域附着通过

run70 在新的单次授权下完成 90 秒人工窗口；用户对显示/颜色/缩放、触摸与四角、设置操作、屏幕键盘输入回复“均正常”。记录到78次触摸按下，GPU、普通用户桌面、存储只读与健康检查通过，189.9秒自动恢复 Android，七项基线一致。未测试按键、新显示模式或任何无线/音频/传感器功能。

随后用户新授权八小时无人操作 RAM 测试。run71 沿用已验证的隔离候选，修正后的设备门禁通过，一次 INIT_ATTACH_SNS 实际返回0，约0.001秒后本地句柄关闭；桌面/GPU/平台与最终健康通过，104.6秒自动恢复 Android，七项基线一致。未启动监听器、registry服务或传感器流；没有DSP端释放确认，不能声称传感器适配完成。run69 原记录及历史停止账本均保留，没有改写历史或自动清除旧锁存。

下一步的 `ram-sensor-fileserver.py` 仅准备私有手机数据与有限时的反向文件服务，禁止 SSC/iio 客户端、动态PD/库、ADSP重启和无线/音频激活。新增19项Linux拒绝/控制测试已通过；真实ARM64与精确rootfs的合成sandbox/QEMU截止检查待通过后才具备下一轮资格。详见 SENSOR-REVERSE-FILESERVER-20261026.md。下方“未再次上机”均为run71之前的历史快照。

## 2026-10-26 run69：联合回归通过，传感器设备门禁拒绝后自动恢复

修订源码574f1d5026f96b4c7312776aa6ce88ae9f972a64的 Actions40230509511 已全部通过：原生 ARM64、精确 rootfs 交接、实际组装 rootfs/自动截止均成功。本地主机整套188项Linux检查通过，私有联合运行器13项检查通过。没有换入新 rootfs 或再次启动手机；真机停止锁存保留。保存的 Android 输入清单另确认 PMIH010x HV haptics 与 ToF8801 软件注册，不能以参考包 AW86927 替代手机振动路径，见 SAVED-PERIPHERAL-INPUTS-20261026.md。

run69 显示、GPU、普通用户桌面及平台检查通过，FastRPC 模块与六组上下文注册；附着前设备门禁错误要求 misc/device/of_node，但固定源码没有设置 miscdev.parent，因而拒绝，未执行 attach ioctl。103.1秒自动返回 Android，七项基线一致，无刷写/人工恢复。未见严重内核故障，仍按显式失败策略保留真机停止标记，不自动解除或重试。

已离线改用唯一绑定 RPMSG 通道的 DT 祖先、ADSP label、唯一 secure 字符节点和设备号，并补真实无 misc 父节点形态及拒绝测试。22项新增 Linux 检查和实际 rootfs Python/fcntl/模块哈希检查已准备；修订版未再上机。传感器反向RPC、registry、数据和轴向仍未通过。详见 SENSOR-FIRST-ATTACH-20261026.md。以下 run68 是当前最近完整隔离平台通过记录。

## 2026-10-26 run68：手机专用固件与新桌面联合通过

共享 CEC/UBWC 修复通过 Actions40226313784 的 ARM64 和实际 rootfs QEMU/自动截止，并经下载摘要、ZIP CRC、候选 rootfs 哈希独立绑定。run68 单次显示激活、Adreno GPU 像素读回、普通用户 Wayland/项目 Mesa/Settings、CPU/输入/电池/温度清单和最终内核健康全部通过，93.6 秒自动返回 Android，七项基线一致；不刷写、无人工恢复、无无线/音频/传感器流。仅软件桌面通过，不把 WiFi combined=false 误记为整轮失败，也不声称肉眼画面/真实触摸通过。

手机传感器的 5 个通用 ELF 与 923 个手机纯数据文件现可生成无自动服务、无 udev、无平板轴向矩阵的独立私有 RAM 交付包；精确 rootfs QEMU 运行时链接检查及 5 项打包拒绝检查通过，尚未交付/attach。实际 HAL 登记已区分 BMI26x、AK0991x、TCS3720 及 Oplus 融合光感。无线实际 BDF/regdb 选择已确认；原厂 SAR 脚本/命令定义已提取，运行时策略与单位仍未验收。后续人工项目统一列入集中验收表。以下旧段落保留历史，完整适配仍未完成。

## 2026-10-26 run67 与共享显示依赖修复

run40223386011 的隔离 rootfs 已通过完整下载、模块策略字节及 QEMU 交接/自动恢复核验。run67 使用手机专用 ADSP/GPU 固件启动新系统，原厂 ADSP 单次启动成功；显示激活被共享 CEC/UBWC 依赖拒绝，70.9 秒自动恢复 Android，七项基线一致。没有刷写或人工恢复。已在主机复现依赖链并按固定源码实现显式共享核心门禁；Actions40226313784 正在验证，离线通过前不再启动手机。详见 SHARED-DISPLAY-CORES-20261026.md。

手机传感器两份 ABI 参考库与原项目固定哈希一致，923 个纯数据文件已用原 importer 私有打包并核验，尚未交付/attach/开流。Android 原厂日志已确认 peach BDF/regdb 实际选用文件，同时发现独立 wifisar 路径；SAR/功率策略未通过前不再开启无线。详见 PHONE-SENSOR-DATA-20261026.md、PHONE-RADIO-SELECTION-20261026.md。完整适配仍未完成；以下旧段落中的 pending/run66 快照不得覆盖本段。

## 2026-10-26 固件来源复核：旧包停止上机，新系统隔离验证中

旧包 ADSP 的 58 个文件来自平板参考下载，仅 6 个与原机一致；已从校验通过的手机 OTA modem 镜像提取 58 个文件，并逐一匹配原机只读哈希，完成 PIL 结构及保留内存检查。旧包无线固件/BDF/regdb 同样不能代表本机 board/SAR 通过，历史扫描和 HTTPS 仅保留为实际行为证据。已设置强制来源门禁，禁止旧包再次试机。详见 FIRMWARE-PROVENANCE-20261026.md。

新 rootfs 的同内核 QEMU 交接/截止 run40219868062 与初次模块/Mesa 组装 run40221133412 已通过；初次组装因缺少完整模块隔离不具备上机资格。新策略包含 373 个模块及依赖的拒绝规则；run40223386011 正在完成最终 QEMU。接下来只验证手机原厂 ADSP/GPU、桌面、CPU、输入及电池清单，无线/音频节点隔离，不开启声音、传感器流、休眠或 USB role 切换。当前最近一次真机仍为 run66，Android 基线一致。

原机 sensor registry 744 个文件经两次读取一致和原项目 importer 离线验证；两路原厂 aw882xx 的 PID2308 专用回调提供间接家族证据。DSP ABI、传感器 attach/流、功放原始 ID/独立校准/动态保护和 MI2S 仍未通过。完整适配未完成；下文历史“当前”描述不能覆盖本次来源纠正。

## 2026-10-26 run66：SCMI 调频策略及 CPU 散热设备出现

run66 在 148.6 秒自动返回 Android，七项基线一致。原交付包中的 CPUCP mailbox 与 socinfo 模块经过实际 archive/ELF/vermagic/依赖/哈希核对后限时加载；出现两组 schedutil SCMI policy 和对应 CPU cooling devices。同轮桌面/GPU/新网络 HTTPS/蓝牙组件/输入/电池联合回归通过，无刷写，无人工恢复。run64 的同镜像只读定位及联合回归在 151.6 秒恢复；run65 因过早要求 ADSP 电池温度而在模块加载前拒绝，73.4 秒恢复且基线一致，实际温度门禁已补五种离线场景。详见 PLATFORM-MODULES-20261026.md；不代表压力温控、频率切换、长期功耗或 USB role 已验收。

run63 的被动清单已实际执行：48 个温度区可读，56 个硬件块设备全部只读，按键能力存在，RTC 原始计数无当前日期偏移证据；CPU policy 和 Type-C 原来为空。SCMI 调频缺口已如上修复，USB 固定 peripheral/role-switch 依赖留作独立问题，不在无人场景切换 USB role。124 项本地离线检查通过，50 项 ARM64 Actions40216514281 已成功。

音频证据追加纠正：现存 ACF 与原机保存的长度/哈希一致，且实际文件通过草稿 C 解析器 ASan/UBSan；此前 owner_version_matched=false 为旧标志。实际 PID、独立校准、动态保护和完整 secondary MI2S 路径仍未通过，不加载 AW 草稿或播放，见 OWNER-ACF-BINDING-20261026.md。新 rootfs 正在准备同内核 QEMU 的实际交接/截止验证，尚未替换硬件候选。完整适配仍未完成，人工项目留待集中验收；以下为历史快照。

## 2026-10-26 run62：关闭无原厂启用依据的 WSA 分支后联合通过

run62 在141.8秒自动返回 Android，七项基线一致，无刷写、记录中零分区写入、无人工恢复。
候选只修改已审查的 WSA 分支状态并删除其播放 link，保留原 kernel/ramdisk/rootfs/恢复保护。
新 WiFi 的完成扫描、认证、IPv4/路由及 HTTPS，与普通用户 Wayland/项目 Mesa/网络设置应用和
三次短时 HTTPS 联合通过，均为 HTTP200、证书结果0。没有人工屏幕或触摸验收窗口。
run59/60/61 分别128.7/117.3/134.7秒恢复且基线一致：前两轮暴露扫描及 DHCP 异步等待缺口；
run61完整联网通过但可选 getent 超时误触发提前恢复。对应门禁已在离线检查后修正。
run63准备增加被动平台状态清单，不激活新外设、音频/传感器流或休眠。

Actions40212524437 的完整 rootfs 构建已通过，完整下载及主机独立复核完成；新 rootfs
SHA256 f9140e5c98d70bca6a04b8934dc9b1937bbf28b1eb0218411eaa0a9939a6cced，
没有替换至旧哈希绑定镜像。Actions40213811895 的音频拓扑合成检查通过；
Actions40214539084 的 AW88461 草稿 ARM64 对象编译、1023个畸形输入与19个I/O故障注入通过，
产物已下载校验。均不代表真实功放或声学安全通过，未加入真机 DT/镜像。

原厂 phandle 复核确认 secondary MI2S 及其四个 TLMM pinctrl，不能默认 primary。
原厂 raw GPIO 复位低有效，新草稿使用逻辑 descriptor，必须显式转换极性，不能照抄旧 flags。
手机 sensor 配置文本与原项目一致，可以复用窄 property shim/目录映射；registry、校准、
DSP ABI和轴向仍开放。完整功能远未全部验收，见 COMPLETE-FEATURE-MATRIX-20261026.md、
AUDIO-MI2S-RESET-REVIEW-20261026.md 和 SENSOR-LOADER-CONTRACT-20261026.md。
下文“当前”段落保留为历史快照。

## 2026-10-26 run58：普通用户桌面与短时联网联合通过

run58 在 144.8 秒返回 Android，七项抽查一致，未刷写、无记录分区写入、无人工恢复。
确认 a 的活动 Wayland 普通用户会话，区别于同 UID 的 manager；该用户 GNOME Shell
映射项目 Mesa，网络设置应用启动并响应 D-Bus，三次采样保持同一 compositor、
保护/恢复/GDM/蓝牙健康，三次绑定 WiFi 的 HTTPS 均为 HTTP200、证书结果0。
此为短时软件会话验收，未声称肉眼屏幕、真实触摸或长期稳定性。run56/57 均已恢复；
run56 错将可为空的 logind Desktop 当作强制品牌字段，run57 修正后到达应用检查，
但一次后续 HTTPS 失败，未获联合通过。详见 RAM-AUTOMATIC-ACCEPTANCE-20261026.md。

音频离线复核有重大纠正：原厂 runtime FDT 的 WSA macro 及 WSA884x/WSA883x
扬声器均被自身或祖先禁用，启用的是两颗 AWINIC smartpa。run42 设备树却开启
WSA884x 播放分支；run47 的 PCM 进展不能作为原厂扬声器路径适配进展。旧镜像
已加入硬件复用阻止清单。先按完整祖先状态修正音频路径，禁止继续 WSA 流实验。
这不撤销本轮显示/GPU/网络/软件会话结果；音频和传感器仍未验收。

## 2026-10-26 run55：自动无线 HTTPS 通过（当前）

run55 在 129.3 秒返回 Android，七项抽查一致，无刷写、无人工恢复，主机规则已清理。
RAM 系统时间校准后，恢复定时器的单调截止值保持不变；扫描、密码认证、IPv4/路由、DNS
及绑定无线接口的 HTTPS 全部通过，HTTP 200、证书验证码 0。未禁用证书验证。
同轮 GPU 像素读回、GNOME 项目 Mesa 映射及联合设备/遥测和服务健康通过。
这只接受自动联网与所列软件/设备检查；没有机主窗口，不代表可见桌面/触摸/UI 验收。

run54 的 118.4 秒恢复和 TCP 建连已确认，但证书校验失败；旧日志时间为 9 月 16 日。
当前时间桥仅处理 RAM staging 会话，独立启动的 RTC/网络时间策略仍开放。
机主已直接授权未来五小时自动实测、不参与操作，窗口截至北京时间 2026-10-26 04:55:14，
仍不刷写或改分区，恢复/内核健康异常即停，过期不得启动。后续优先不需人工的项目。
下文 run54 之前的“当前”“待授权”均为历史快照。

## 2026-10-25 run53：DNS 通过，HTTPS 超时（当前）

128.6 秒确认返回 Android，七项抽查一致，零分区写入，无人工恢复，主机临时规则已清理。
WiFi 扫描、密码认证、活动 UUID、IPv4/默认路由及 DNS 命令通过；缺少 ping 正确跳过，
HTTPS 返回 curl 28，完整联网不通过，未开放机主窗口。机主确认其他设备使用同一网络可上网。
具体超时阶段未记录，不能据此断定驱动故障、IPv6 故障或目标站点不可达。
GPU 4×4 读回和 GNOME 项目 Mesa 映射继续通过，联合设备/遥测阶段完成；音频和传感器只读。

随后仅主机离线增加 IPv4 HTTPS 分阶段数字计时，保留接口绑定、证书验证、禁代理和原有限时。
18 项 Linux 检查和候选 rootfs 实际 ARM64 curl 的三个回环 TLS 检查通过，
run54 的 14 个构造阶段及完整离线交付检查通过。这些不证明真实无线传输通过。
run53 授权已使用，run54 尚未获准启动。以下 run52/run51 段落均是历史快照。

## 2026-10-25 run52：认证和地址通过，完整联网待验收（当前）

单次 RAM 授权已使用，113.9 秒确认返回 Android，七项抽查一致，零分区写入，
无人工恢复。wpa_supplicant 在显式 WCN 探测前就绪。自动 WiFi 完成单次扫描、
指定网络密码认证、活动连接 UUID、IPv4 地址和默认路由；网关探测因镜像缺少 ping
触发验证器异常，DNS/HTTPS 未执行，未开放机主界面回归。这不是 WiFi 驱动故障证据，
也不是完整联网通过。GPU 4×4 读回、GNOME 项目 Mesa 映射及联合设备检查完成；
本轮没有人工触摸验收。蓝牙真实文件接收确认仍以 run51 为准。

验证器已同步修复工作/公开源码副本：可选 ping/getent 缺少时记录并继续 HTTPS，
核心 nmcli/busctl/ip/curl 缺少时明确失败。Linux 下 15 项检查通过；run52/run53
各 14 个构造阶段检查通过，run53 完整离线交付检查通过，手机操作为零。
原有镜像/内核/设备树保持不变，音频与传感器只读。音频 SoundWire/EIO、真实
传感器流、WiFi HTTPS/界面、全区域多点触摸、休眠和长期稳定性仍待验收。

Actions40204541108 的完整 rootfs 已完成主机完整下载、ZIP/摘要及独立验证，
SHA256 为 c4a908eec6cbb87ee0cf1644933c4d8476ec7e3e586200aafc896da45053ac62，
尚未用于手机。run53 使用既有镜像与 RAM 增量，等待新的单次授权。
以下 run51/run50 段落中的“最新”“尚未下载”和授权描述均是历史快照。

## 2026-10-25 run51 蓝牙文件传输通过（最新）

机主确认对端收到测试文件，蓝牙一次真实配对/文件传输验收通过。221.5 秒返回 Android，
七项抽查一致，零分区写入，无人工恢复。GPU 读回和 GNOME 图形库映射继续通过，
60 秒记录到 33 次触摸按下。音频和传感器保持只读。

WiFi 自动检查未进入认证：日志显示 D-Bus 无法激活 wpa_supplicant，实际镜像缺少
程序、D-Bus 激活文件和 systemd 单元。已修正手机独立 rootfs 的显式种子与完整性检查，
保留原 Pad 基于 Desktop ISO 的构建路径。14 个签名索引核对的软件包组成 RAM 增量；
三个 ARM64 程序启动检查，以及私有主机 D-Bus 上的认证守护管理接口响应均通过。
八项自动验证器离线检查通过。完整 rootfs Actions40204541108 构建、八项测试和
实际 ELF/激活文件检查通过。新产物尚未在主机独立完整下载复核，也未用于手机。

run52 仅离线准备：在显式 WCN 模块探测前验证认证服务；自动 WiFi 不通过就提前恢复，
通过后才提供界面回归窗口。后检复用 WiFi 结果，避免重复设备查询。本轮授权已用完，
需新授权才能启动。详见 RADIO-RUNTIME-20261025.md；下方为历史记录。

## 2026-10-25 run50 联合验收与后续离线修复（最新）

单次授权已使用，248.8 秒确认返回 Android，七项抽查一致，零分区写入，无人工恢复。
GPU 4×4 读回及 GNOME 项目 Mesa 映射继续通过。90 秒内记录到 67 次触摸按下，
但未验证全区域和多点。机主确认蓝牙能配对，文件发送按钮无反应；WiFi 界面看不到
周围网络。低层 2412 MHz 扫描只发现一个 BSS，不能当作认证/DHCP/联网通过。
后检停在接口查询阶段并触发 50 秒外层限时，随即提前恢复；无线根因尚未确定。

离线确认缺少 bluetooth-sendto 与 OBEX 服务。已准备九个签名索引核对的软件包组成的
独立 RAM 增量，不替换现有 BlueZ 核心；两个 ARM64 程序通过 QEMU 软件启动检查。
WiFi 自动验证器六项离线检查通过，下一轮由 NetworkManager 单独管理扫描与连接，
自动验收认证、DHCP、网关与 HTTPS；通过后才请机主做 WiFi 界面回归。
任何查询超时均停止该路径、取有限日志并提前恢复。run51 尚未执行，需要新授权。

音频路由离线检查发现六个额外控制未接通，不能据此认定 SoundWire/EIO 根因；保持
音频流关闭。手机 OTA 传感器配置已离线提取，通用 ARM64 用户态 Actions40198265425
通过 8+7 项软件测试，尚未启动真实传感器流。详见 OFFLINE-AUDIO-SENSORS-20261025.md。

## 2026-10-25 run49 追加验证（最新）

用户追加一次RAM授权，105.3秒确认Android返回、七项抽查一致，零刷写，
无人工恢复。原生激活/GPU绑定→刷新图形环境→GDM重启顺序验证通过，
GNOME实际映射项目Mesa26.2.3；同轮Adreno830v1的4×4GLES读回通过。
run48的GNOME库选择缺口已关闭，仍不等于现场画面/长期稳定性验收。
WiFi扫描4BSS、蓝牙发现、触摸设备和电池/USB遥测回归通过。音频仅只读。
追加额度已使用，累计四次授权全部消耗；音频SoundWire/EIO和手机传感器等
门槛仍开放。下文run46–48结果为历史快照。

## 2026-10-25 run46–48 多目标 RAM 验证（最新）

本轮单独授权的三次临时 RAM 启动均已使用，均提前确认返回 Android，
七项抽查元数据一致，零刷写/分区写入，未要求人工按键恢复。
run47 修复手机 WSA backend→MultiMedia1 路由后，PCM open、HW_PARAMS、
PREPARE 成功，写入仍 EIO，并出现 SoundWire clash/CMD error；声音未验收。
run48 不重复开音频流，仅只读。专用 Mesa26.2.3 的 Adreno830v1 一次4×4
GLES 清屏/像素读回通过，但 GNOME 仍映射系统 Mesa。启动顺序已离线改为
原生激活/GPU绑定→图形环境刷新→GDM重启，尚未再上机。WiFi 定向扫描和
蓝牙发现通过，不等于联网/配对；触摸设备和电池/USB遥测可读，不等于
完整触控/充电验收。传感器参考配置为OPD2413平板，禁止直接用于PJZ110。
下文为历史状态，最新结论见 [MULTI-ACCEPTANCE-20261025.md](MULTI-ACCEPTANCE-20261025.md)。

## 实际 OPP 与双 mixer/pipe 离线修复

已复现上一轮 -7：旧夹具的 1 GHz 没有绑定真实 575 MHz MDP OPP。
第十一补丁按实际两个 LM 计算下限，并在 SSPP 分配前用完整预算决定拆分，
不修改 OPP 或减半内存带宽。读取实际编译 DTB 的 C 检查得到355764706Hz，
十项 C 的 ARM64 ASan/UBSan、61项ARM64工具测试和完整内核构建40068074272
通过且下载复核；匹配新rootfs/GNOME/QEMU40068689660通过，大附件已在
接手主机完成下载复核与交叉验证，私有候选 e5c6944 已组装并回读校验。
随后机主授权的唯一一次 RAM 验收被环境故障消耗：接手主机为 VMware 虚拟
机，USB 直通在重新枚举时丢失，rootfs 传输 0 字节，preflight/activation
未执行，第十一补丁未上机；手机按镜像内 900 秒截止自动回到 Android，
七项元数据一致、零写入。下次验收需先修 USB 自动直通（或用物理主机）
并再次获得单独授权。详见 [DPU-OPP.md](DPU-OPP.md) 与私有目录
native-acceptance-e5c6944/OUTCOME.md。

## AA569 固定 PHY 候选增量

最新：随后经机主单独授权，完成一次 RAM boot/显式加载，真实预检通过，
但 DPU 性能检查返回 -7，显示未验收。主机动态提前恢复，135.4 秒确认
Android 返回，抽查元数据一致，无刷写。旧测试的 1 GHz 成功用例未绑定
实际 575 MHz MDP OPP；当前预算 711529412 Hz 会被拒绝。已撤销当前
候选再次试机资格，转入实际 DTB/topology/plane split 联合离线修复。
下文手机未操作指先前离线阶段；此次单独授权只有一次，已经用完。

已追通厂商 V7.2 从生产 DTS 到寄存器的十四值提交路径，新增第九补丁，
仅对严格匹配的实验 AA569/SM8750/DSI0 固定速率选择生产时序，并同步
host shared timing，并修复原 host PM/OPP 失败清理。十项 C 的 ARM64
ASan/UBSan 与内核构建40065006440通过；独立时钟/TE与61项ARM64测试
40065992683通过；匹配GNOME/rootfs最终QEMU40066356160通过。
已实现手动RAM预检/一次激活入口，无自动服务；QEMU只检查接口和拒绝公开
无私有参数的环境，未加载真实显示模块。默认native打包继续关闭，显式离线
证据门槛只允许主机组装私有候选，不授权试机。手机未操作；物理显示、触控、
WLAN/GPU和最终组合仍待验收。详见 [FIXED-PHY.md](FIXED-PHY.md)。

## 2026-10-24 PLL/PHY 离线审查

新增实际平台/厂商 C 算术对照。标称 PLL 分数频率可以精确表示，但通用
D-PHY v4 生成的 14 个时序字段中有 6 个与 AA569 生产配置不同。当前只
确认源码差异，不认定为历史黑屏原因，也不直接替换时序。ARM64
Actions40062728159 的 66 组 PLL 对照和 PHY ASan/UBSan 审查通过，附件
已下载核对九个源文件及本地/ARM64 结果一致。运行内核/镜像不变，手机操作为零。
详见 [PLL-PHY-AUDIT.md](PLL-PHY-AUDIT.md)。

## 2026-10-24 DSI 整组发送离线增量

已按原 Pad 主线接口和固定厂商 FETCH_MEMORY 路径实现完整组提交，保留
150 包的 13 个 DMA 边界，补上整组锁/资源持有和错误清理。九项实际 C
主机检查及 53 项工具测试通过；Actions40058811743 的 C ASan/UBSan、
完整 ARM64 内核/模块和诊断 QEMU 通过，Actions40059533734 的新模块/
GNOME/rootfs/QEMU 组合通过，全部附件已下载复核。详见
[DSI-BATCH.md](DSI-BATCH.md)。手机操作为零，原生
桌面显式激活/打包继续关闭，真实时序/PLL/物理显示仍待验收。

## 2026-10-24 原生参数跨切根交接

修复只保留SPR参数、丢失匹配助手和候选标记的缺口。新增版本/双哈希清单，
检查完整输入后仅暂存到RAM overlay与新/run；助手不可执行，不加载模块。
53项主机及ARM64 Actions测试通过，Actions40056382745通过新增QEMU切根后
复制/权限/损坏及链接拒绝检查、桌面交接与180秒重启，产物已下载复核。
固定重用d624154c内核和2957513a根文件系统。厂商DSI批组的进一步对照
确认资源持有和提交差异，名义最大批组312字节；未修改内核发送路径。
详见[NATIVE-HANDOFF.md](NATIVE-HANDOFF.md)。手机未参与；
显式激活、DSI时序和物理输出仍未验证，native桌面打包继续关闭。

## 2026-10-24 原生显示离线修复

按用户最新要求暂停真机调试，本轮设备操作为零。已修复 native helper/内核
SPR/桌面 helper 对 ABL 身份的误判，补上 rootfs 显示加载阻断及 QEMU 实测项，
临时关闭 native 桌面打包。48项测试、新 ARM64 内核/模块构建、八项 C
ASan/UBSan 以及新内核 rootfs/QEMU 交接与恢复通过；物理显示仍待验证。详细范围、证据和下一步见
[原生显示离线门槛](OFFLINE-NATIVE-GATE.md)，下方历史构建不覆盖本轮源码。

用户已批准独立分支和 Actions。d624154c 的 GNOME/QEMU40051767501 通过，
其中 rootfs 为新策略版、内核仍为原固定 c2e659。新内核40051765091和
组合验证40054456226均通过，后者固定提交2957513a中的d624154c内核附件。
新release为7.2.0-oneplus13-g7a81d184e309-c963dc1c909ec-pcd4948652e86。
手机未参与本轮。继承 framebuffer 的资源引用缺口新增为
待核查事项，尚不能判定为黑屏根因。

下一步继续离线处理原生手动启动的跨switch_root交接、厂商13批组与当前
逐包DSI调度差异、PLL取整及显示资源接管；这些门槛关闭前保持native桌面
打包禁用，不安排探索性真机测试。下方历史状态仅为归档。

## 2026-10-24 真机接手后的本地增量

本段描述本次接手会话，下面保留的历史快照不代表当前测试结论。

- 默认300秒RAM诊断已在PJZ110真机启动，USB NCM/HTTP/Telnet可用，145项UFS设备及分区软件只读，未挂载Android；随后返回原Android。
- 首次RAM桌面测试完成7块432734208字节下载、完整SHA、只读SquashFS及RAM overlay挂载，但compatible门槛误拒绝ABL运行时身份，未进入systemd。
- 已参考原项目erhai-physical-platform和init-ncm修复model＋chassis边界，保留Gunyah/VMID/驱动检查，16项离线测试通过。
- 修复后真机重测已确认PID1为systemd，GDM/NetworkManager/D-Bus/存储保护运行，GNOME Shell 50.1初始设置会话运行；屏幕仍黑，原生显示/触控/WLAN未验收。
- systemd平台检测为none，PID1 Virtualization为空。保留900秒截止，约930.26秒后确认返回原Android，元数据一致；主机未发送重启命令。

## 历史归档快照


截至2026-10-24，c2e659aaa062内核、a6c8ceb根文件系统与ef63950完整HTTP交接/恢复版本均已下载复验；两份本机校准RAM桌面候选已生成。**没有在手机启动实验内核，完整硬件适配尚未完成，不能称为可正常刷入使用的系统。**

| 组件 | 状态与证据 |
| --- | --- |
| 平台内核 / 完整模块 | Actions39992904871通过；23项Python、全部主机C ASan/UBSan、ARM64内核/模块和QEMU用户态启停通过 |
| 原厂引导校准 | 默认/触控/显示/无线/GPU五棵DTB分别通过原厂正对照、全部6个覆盖层和15个RAM区保护检查；实际ABL/hypervisor接受未验证 |
| 未签名v4三件套 / v2 RAM格式 | 主机按本机96/8/96MiB容量打包，独立分段回读；没有刷写、签名或修改vbmeta |
| 固定SPR运行接管 | 完整ARM64编译通过；私有参数、全管线UDC预检、空闲/时钟/复位保护、独占DSI0、DSPP保留、flush位8和3次PM恢复主机C检查通过；无DMA/动态UDC |
| AA569原生显示候选 | 新增独立native DTB，准确供电/复位/TE/端点与7项反例通过；仅固定120Hz/DBV1433，物理输出和电气行为未验证 |
| 私有原生显示RAM镜像 | 主机生成并回读；9个显示依赖模块、本机176字节SPR参数、匹配内核和USB就绪后的手动加载；原始init/只读保护/300秒恢复不变；此派生镜像未跑QEMU |
| DSC / DSI / DPU | 完整PPS、物理bpp128/硬件字段256、命令HS上限、初始行数4/full-ICH/包装器/PPB检查和编译通过；6800us性能预算、261组C对照、新原子plane计算和ICC/OPP拒绝已编译；真实传输时长/PLL仍待实测 |
| 默认诊断 / 独立S3910触控 | 两棵DTB与早期badf9e字节一致，MDSS禁用，无AA569；触控模块编译和协议解析检查通过，SPI及物理触摸未验证 |
| USB / 自动恢复 | 编译及用户态检查通过；真实枚举、RAM使用和300秒恢复仍待真机验证 |
| Ubuntu GNOME | Actions40007875169离线通过；实际SquashFS进入systemd，GDM active/running、GNOME50.1、NetworkManager/D-Bus/只读保护通过，两个附件已下载复验；物理桌面未验证 |
| RAM桌面引导 | Actions40010305668离线通过；7个HTTP分块/完整SHA/OverlayFS/交接/恢复服务实际触发通过，900秒生产截止不变；两份本机校准RAM镜像回读通过，实机ABL/USB/恢复未验证 |
| 独立WCN7860无线 | DTB/模块离线通过，匹配本机哈希的OTA输入已取得；实际major2/QMI板号、BDF选择、认证/SAR和收发未验证 |
| 独立Adreno830 GPU | DTB/模块离线通过，正确的本机签名ZAP已取得并匹配哈希；仍需显式separate_gpu_kms=1，认证和真实渲染未验证 |
| Bluetooth | UART/固件/地址及真实收发未完成 |
| 电量 / 充电 / 音频 / 传感器 / 蜂窝 / 相机 | 未完成手机移植，未启用未经验证的DSP/厂商充电路径 |
| 持久安装 / 双系统 | 未提供手机分区或自动安装工具；不得套用Pad流程 |

最新[Actions39992904871](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/39992904871)，实际源码c2e659aaa062647a206c67edcc421f0fa9931f7a。
完整附件12518803835已下载，59797477字节，SHA256为230c9b9258b6c8cf69a8d8ff7e1e6e7bdeb2de2da7c44d0ba858557c4f8fdc80。CRC、35个清单文件、CI校验、镜像分段、七种模块的AArch64/vermagic及SPR运行函数通过本机复验。
内核版本：7.2.0-oneplus13-g7a81d184e309-c963dc1c909ec-p92bbf23dc6a6。
私有显示RAM候选14675968字节，SHA256为960436c36424ba49e82ff1a427ce224cdbab876d78302dd378ec0dbc051c1131；不含GNOME或触控，不得公开其中的本机参数。

当前优先级：显示、网络、触控和进入GNOME的完整启动链。软件离线版本已收口：Actions40010305668完整HTTP下载/用户态交接/恢复通过，本机default/native两份RAM桌面候选分别为14032896/14680064字节，详见[桌面引导](DESKTOP-BOOT.md)。9个OTA输入均与本机哈希匹配，见[固件证据](STOCK-FIRMWARE.md)。唯一下一步是用户后续安排有现场恢复条件的最小RAM引导，先确认ABL/USB/RAM/自动恢复，再按[现场清单](TEST-HANDOFF.md)分别验收原生显示、触控和WLAN。当前只读权限禁止执行这些试启动；尚不能证明可正常刷入使用，也不能在硬件验收前合并外设或制作持久安装。旧诊断交付独立保留，音频及其他外设推迟。
真机门槛：用户后续安排有现场恢复条件的限时RAM引导，先验证USB、RAM和恢复，再逐项验证显示/触控。当前只读权限禁止执行试启动或刷写。

设备状态：本阶段共4次经独立审核、45秒截止/2KiB上限的SSH元数据查询（1次非root、3次用户确认后的root），均与PJZ110 Android16 .501指纹匹配。已确认UID0、WLAN目录和PCI17cb:110e；读取12个固件文件的大小/哈希。公开Lineage参考ZAP/BDF不匹配，匹配版本的官方OTA九文件全部相符。最新有限日志未提供QMI板号或活动BDF，不据此猜测。0次二进制文件传输、手机写入、重启或试启动。未重新散列分区或完整FDT；只读限制继续有效。
# 2026-10-26 offline RPC follow-up

The phone-only RPC overlay preserves and fixes the original input TYPE_SEQ wire
layout (own index, metadata cursor and empty sequence), validates descriptor
indices and checks scalar buffer limits before allocation. Unqualified output
TYPE_SEQ is refused before ioctl. Ten release and ten ASan/UBSan C tests pass
locally; the original golden tests remain intact. The earlier three overlays
passed native ARM64 Actions40250963720; the fourth overlay passed native
Actions40252529300 and exact Ubuntu rootfs CLI/link checks. No new phone run or
sensor stream is accepted. See PHONE-PCB-MAPPING-20261026.md for scope and holds.

# 2026-10-26 phone RPC VFS follow-up

Run75 completed a full bounded service window: Android returned134.6s after boot,
seven baselines matched, display/GPU/desktop passed, the daemon stopped cleanly,
there were zero write-mode refusals and2648 successful reverse invokes. It still
failed the diagnostic bound because method33 registry renames were unsupported.
Overlay0008 now implements bounded RAM-only method33 renames; run75 remains
halted pending native ARM64 and a fresh source-bound review.

Run76 passed the bounded registry-rename diagnostic: one attach,28s window,
2573 successful reverse invokes, zero write refusals and zero unsupported
dispatches, clean stop, no stream, Android return132.9s and seven matching
baselines. Display/GPU/desktop also passed. It retained37 classified missing
config/OEM lookups and did not claim full file-server or sensor acceptance. A
private PCB scalar is now included in the next RAM rehearsal input.

Run77 completed the lookup-inventory target after adding the private PCB scalar:
PCB misses disappeared, missing lookups fell37→31, all31 hashes matched saved
requests and there were zero unknown hashes, writes refusals or unsupported RPCs.
The private runner's stale923-data-file assertion failed after the archive grew
to924; it is corrected and run77 is sealed. Remaining real probes are one camera
blob and three OEM/DSP items;27 vendor configuration probes are absent from the
saved vendor index.

Run74, one source-bound RAM write diagnostic, exposed the next two concrete
gaps: registry temporaries `fstempfile` and `parsed_file_list.csv`, plus a reverse
request larger than256 bytes. Android returned automatically107.7s after the
original boot command; seven baselines matched and display/GPU/ordinary-user
desktop passed. Overlay0007 now adds only those two exact RAM paths and a separate
64KiB listener input buffer; service launch failure is also retained as
diagnostic evidence. Run74 remains halted. See PHONE-RPC-RAM-FILES-20261026.md.
Native Actions40263745661 and a fresh exact-rootfs QEMU-user link/loader/CLI
probe pass; no new phone retry is implied.

Default-off phone overlay0006 now integrates bounded volatile copies for the two
run73 write paths. Host v18 passes13 release +13 ASan/UBSan C tests and6 Python
checks. The exact method5 wire test and storage LSan test pass; full-suite leak
detection remains disabled because the original root-tree builder lacks a
destructor. Native ARM64 Actions40260814820 and artifact12624705085 pass; a fresh
exact-rootfs QEMU-user RPATH/loader/`-W` CLI probe also passes without device
access. No phone operation or run74 qualification. See
PHONE-RPC-RAM-FILES-20261026.md.

The original read-only VFS alias/parent cleanup bug is reproduced with ASan and
fixed in phone overlay0005 before any RAM write backend. Fresh host build v8
passes11 release +11 ASan/UBSan C tests and6 Python checks; the original apps_std
test now really deinitializes its context. Native ARM64 Actions40256968720 passes
the same11+11 C and6 Python checks. Artifact verification and fresh exact-rootfs
QEMU-user normal-RPATH/help/loader checks pass, without changing baseline staging.
No new phone operation or run73 retry qualification. See
PHONE-RPC-VFS-LIFETIME-20261026.md. Earlier snapshots below remain historical.


2026-10-26 run80 safely returned to Android after the metadata-only SSC probe stopped before a qualified result. The reverse service had one attach, module policy and private inputs were unchanged, and there were no samples or streams. Exit255 did not establish a discovery timeout. The diagnostic version retains the original 8-second deadline, validates exact public failure categories, records systemd execution status before cleanup, and bounds private raw failure output to RAM-only root-readable files. Fresh native and full-system QEMU verification is required before any new source-bound hardware review. This is not sensor-stream or camera/audio acceptance.
# Incremental hardware evidence and independent stages, 2026-10-31

r202 public source 95b931d72f2cc2026c844080896b10cb7c8e8df7 completed all five
Actions jobs in run 41178635052. Three downloaded archives and installed inputs
were independently verified. Incremental r203/r204 RAM boots now bind S5KJN5,
verify its expected chip ID (0x38e5), runtime-suspend it, remove the temporary
I2C target and unload owned camera modules. This establishes sensor access,
not real-frame capture. The 5 GHz preservation check and running MPSS/IPCRTR
verification pass. No partition writes occurred; Android's seven baseline
properties match after return.

r204 continues past a clean GNSS pre-start registration failure and an NFC
no-tag result. NFC binds and powers up/polls, then confirms poll-stop and
power-down; it has not detected the owner's tag. USB briefly reports host,
but UCSI disconnect changes the role during physical cable replacement;
no peripheral or read I/O is qualified. A 30-second return confirmation
expired, so the full planned-round acceptance remains false even though
USB device-role cleanup and Android return are confirmed.

The next candidate makes GNSS no-session cleanup explicit and retries the
standard satellite position-report subscription once only after NMEA event
registration returns InvalidArgument. A fix still requires successful start,
stop and either checksum-valid NMEA or a successful satellite position report
with finite in-range coordinates. USB only reconciles a replaced host request
after UCSI independently reports an attached host/source port; no power role
is forced. Native Werror compilation/self-test and 30 focused Python tests pass.
These new changes are candidates pending Actions and new combined hardware tests.
See INCREMENTAL-HARDWARE-20261031.md; no claim of complete adaptation is made.
# r205 combined run completed safely, 2026-10-31

Actions 41182218697 passes all five jobs at f67c02498fd6083f61821ed78818ad41ee71cf92.
The exact image completed every incremental phase in one RAM boot, delivered
all private evidence and returned to Android with seven baseline properties
matching and zero partition writes. Camera chip ID, 5 GHz preservation and
MPSS verification pass. GNSS rejects both event masks before start; USB has
no peripheral enumeration. NFC is explicitly skipped because no physical tag
is available. Full/incremental target acceptance remains false. New diagnostic
source distinguishes GCTL host from bound xHCI/root hubs and records LOC
endpoint selection snapshots. See INCREMENTAL-HARDWARE-20261031.md.
# USB probe cleanup and bounded candidate follow-up, 2026-10-31

The follow-up limits read-only USB storage proof to one verified partition,
times directory/file I/O in a separate child and reserves parent-owned unmount.
Unmount failure explicitly fails overall cleanup and cannot become an I/O pass.
GNSS18 + USB23 focused tests pass; independent source review agrees. No new
phone boot accompanies this follow-up. r205 remains the latest physical result;
GNSS fix, USB peripheral I/O, NFC tag detection and real camera frames are open.
