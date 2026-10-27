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

APT legitimately percent-escapes `+` and `~` in snapshot pool URLs. The first
parallel-fetch trial rejected these before downloading; decode before validating
safe paths, retain origin/traversal/separator/SHA256 checks. All 727 rows of a
fresh isolated resolution from verified snapshot indexes now parse, including
86 escaped URLs. Full corrected Actions build and timing are still required.

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
## Current image branch qualification debt

- GitHub Actions can reproduce the public kernel, rootfs and assembled RAM
  userspace, but not flashable per-unit artifacts that require owner-supplied
  firmware or calibration. Those inputs remain local.
- The 2.4 GHz path is device-qualified. The separate 5 GHz target was not
  observed in run88 scans; radio band capability alone is not acceptance.
- WiFi policy/SAR integration remains a separate transport experiment and is
  not silently enabled by this branch.
- Audio streams, camera activation and sensor streams remain separately gated.

<!-- END-CURRENT-IMAGE-BRANCH-20261026 -->

# Technical debt (single register for the phone)

Current WiFi gap: radio-disabled isolated image contains no WCN7860 firmware.
Exact-phone five-file host staging is ready. Dormant SAR transport and the
entire common/WiFi7 family pass native compile/link Actions40319212570 with
15+29 release/sanitized test groups; full Image/modules integration is now
an explicit offline workflow input and still requires its own full build result.
No current-image WiFi test passed. Android GET advertises QCA5/TAS but legacy
GET is NONE/empty; pinned WMI/host numbering has a naming discrepancy. Preserve
raw capability and reject guessed USER/V2 or disabled/unlimited interpretations.
Resolve effective TAS/SmartTx lifecycle/policy before production RF admission,
then rebuild exact candidate and perform scan/auth/DHCP/verified HTTPS jointly
with desktop/platform/recovery checks. No new RAM boot is authorized by CI.

The sections below retain earlier pending stages; current results above take
precedence. Historical stop ledgers remain preserved.

WiFi is now the owner priority. The new transport-free phone SAR codec passes
14 host release and14 ASan/UBSan/LSan groups, including exact bytes against the
actual pinned vendor sender. Native ARM64 is pending. QCA USER6/V2=7 must map
to firmware USER7/V2=8; NONE5 is refused, never treated as firmware BDF4=5.
This codec is not wired into ath12k WiFi7, does not establish a phone policy,
and does not authorize RF. Add capability/GET/event integration and serialization
across firmware restart; qualify exact phone BDF/regdb/firmware rather than the
reference inputs used by historical run66. Then current-rootfs automatic
scan/authentication/DHCP/verified-HTTPS and desktop regression remain required.


The corrected batch now passes: native10 camera/amplifier objects and actual
PHY7 release/7 ASan+UBSan cases (Actions40285807929); SSC3 release/3 sanitizer
executables plus13 wrapper cases (Actions40285807884); and full exact-rootfs
UID65534 sandbox, actual timeout, handoff and VM automatic deadline. This
supersedes the pending rebuild stages below, not the retained fallback failure.
Two phone-specific audio graph drafts compile/decode offline. Missing sensor
driver/media graph, WCD channel mapping, speaker calibration/protection and
physical sensor/RF/audio/camera acceptance remain. See AV-SSC-OFFLINE-20261026.md.

CORRECTION: the earlier SSC QEMU-user -L link result used host ARM64 fallback
libraries and is not an exact-rootfs pass. Full VM exposed missing protobuf-c,
qmi, qrtr and mbim runtime libraries. Old evidence is retained and superseded;
the gate stays closed, with no phone attempt. The isolated archive now records
four generic runtime libraries plus package/source versions and copyright.
Native rebuild and full-VM sandbox/deadline checks are pending. Do not use a
successful loader trace without checking every dependency exists in the target.

The camera local fixes retain all23 upstream patch hashes, remove two obsolete
locals and propagate timing/mode errors before PHY configure/power. Seven
actual extracted-function failure/success controls pass host release and
ASan/UBSan. Native joint camera/amplifier compilation, now including CAMBIST,
is still pending; no phone graph or sensor support is implied.

The camera component draft stages23 original, source-pinned patches: standalone
PHY, external-PHY CAMSS plumbing, Kaanapali dependencies and SM8750 RDI support.
All apply with fuzz=0 to fresh affected files at the phone kernel pin. Native
joint camera/amplifier object compilation remains pending. No phone sensor
driver, board power/lane graph, custom ultrawide PHY qualification, ISP or
libcamera pipeline is implied. Speaker calibration/dynamic protection remain
incomplete. No boot image or phone DT integration is produced.

SSC native Actions40281827817 passed3 release/3 ASan+UBSan executables. Fresh
exact-rootfs userspace loader, lock-only CLI and pure tests pass in an isolated
library namespace; no QRTR query was executed. Hard-deadline/cleanup review and
actual discovery remain separate gates, and all measurement requests stay
blocked. The earlier native-pending stage below is historical.

The isolated SSC metadata probe now has an irreversible process send guard,
real-send rejection tests, original delivery encoding regression and fresh-tar
host release/ASan+UBSan results (three executables each). Native ARM64 and exact
rootfs hard-deadline/cleanup checks remain pending; no sensor samples or new
phone qualification are claimed. See SSC-METADATA-PROBE-20261026.md. The pinned
original-project chronology is recorded separately; camera support is new
work, and phone two-AW/MI2S speakers must not inherit Pad six-AW/TDM tuning.

Run79 jointly passed both synthetic ARM64 userspace tests, the actual read-only
camera-input open, clean reverse-service stop and display/GPU/desktop/platform
regressions; automatic Android recovery took131.7s with seven baseline matches.
The30 remaining requests are27 stock config probes and three OEM/DSP probes.
No sensor stream/camera operation/DSP release acknowledgement is accepted.
Run78 stopped before reboot at an old host command allowlist, zero RAM boots;
its retained stop is addressed by an exact bounded stock battery read with six
host fixtures, not a broader general transport permission. Run79 is sealed.
See JOINT-RAM-RUN79-20261026.md; earlier pending stages below are historical.

The next joint acceptance preparation exports two existing synthetic C tests
separately from the production runtime and adds a twelve-second UID65534 systemd
sandbox with devices hidden/denied and no network. Eleven wrapper/archive checks
pass; native artifacts and full exact-rootfs QEMU execution remain pending.
No new phone scope is qualified by these source changes. Camera input/readback,
service evidence and desktop/GPU/platform regressions must be reviewed together.

The pinned vendor SAR response review now distinguishes parser success from the
SAR2 result field, lossy capability-version/band mappings, the GET assert/clamp
path above64 rows, and SET submission versus correlated result/readback/replay.
See SAR-PROTOCOL-GAP-20261026.md. No firmware response or actual phone RF policy
has been observed. No radio command, phone test or latch change accompanies
this source-only review; do not use GET/parser success alone to open the RF gate.

Current combined offline results: native ARM64 Actions40270669480 passed14
release/14 ASan+UBSan C and6+36 Python checks, fresh exact-rootfs link/CLI probes,
actual UID65534 reading930 files and933 absent delivery destinations. The later
"native14 pending" sentence below records the earlier source submission stage;
it is superseded here. See BATCHED-RPC-PREPARATION-20261026.md. No run78 is
qualified, old halts remain retained, and all peripheral gates still apply.

Overlay0010 stages an exact, read-only camera metadata filename. The private
input was passively copied from Android, matched the earlier inventory hash and
preserved all seven baseline samples; no reboot/activation or phone write was
performed. Source/artifacts contain synthetic tests only. Host14 release/14
ASan+UBSan pass; native14 validation remains pending. The file has not yet been
delivered to a new RAM session and does not qualify camera operation.

All27 absent configuration requests occur literally in the saved stock json.lst
(20 include '#'). Parser semantics remain unproved, so keep exact bytes/ENOENT.
The Qualcomm oemconfig ENOENT warning exception is evidence of reference logging
policy, not proof of phone feature optionality. Dynamic TPPE/CHRE registrations
remain real unresolved inputs; do not execute them to remove a diagnostic error.

Overlay0009 and service cleanup passed native ARM64 Actions40269798259 and fresh
exact-rootfs loader/CLI probes. Method33/9 dispatch and signed seek ABI were
corroborated against35 saved phone ELF instructions, without executing the ELF.

Overlay0009 repairs offline-reproduced snapshot resurrection and missing-source
rename name-table exhaustion, plus an uninitialized index when append creates a
missing file. Bounded tombstones consume the same finite name table; exhaustion
refuses rename before changing names/data. Source handles remain valid. Signed
IDL seek, negative errno mapping and failed-seed cleanup have actual C coverage.
Fresh-tar host13 release/13 ASan+UBSan tests pass; native ARM64 remains pending.
Service controls have36 Python checks including real systemctl nonzero status
semantics, pre-stop query failure and launch timeout cleanup. These repairs do
not resolve missing OEM/camera inputs or qualify a new phone boot/sensor stream.

The owner requests batching multiple adaptation targets into one future qualified
RAM acceptance, with display/GPU/desktop/platform regressions. Do not consume a
phone boot for one isolated repair or repeat an already-passed diagnostic.

Run75 removed observed write-mode refusals and ran the full service window, but
method33 registry rename was repeatedly unsupported. Overlay0008 adds a bounded
RAM-only copy-on-write registry namespace and rename semantics; host tests pass,
native/rootfs and a new source-bound review remain. Run75 halt is retained.

Run76 passed the bounded rename diagnostic with2573 successful reverse invokes,
zero write/unsupported refusals, clean stop, no stream and matching Android
baseline. Full acceptance remains withheld for37 classified missing config/OEM
lookups, absent directory-inode evidence and no DSP release acknowledgement.
Run76's one-shot ledger is sealed; the private PCB scalar addition is not a retry
authorization.

Run77 resolved the PCB lookup and classified every remaining missing request:
27 absent vendor configuration probes, one camera-info blob and three OEM/DSP
probes. All31 SHA256 fingerprints matched saved requests. A stale private harness
file-count assertion caused the wrapper to fail after the service target passed;
it is corrected. Do not fabricate nonzero/extra DSP files or ignore the four real
inputs; run77 stays sealed.

Run74's bounded write diagnostic returned Android and matching baselines but found
two more registry temporaries and a >256-byte reverse input. Overlay0007 adds the
four exact RAM paths in total and a64KiB listener buffer; launcher failures now
preserve status/log/trace facts. Run74 is halted, not accepted. Native/rootfs
qualification passes after the fix, but a new source-bound review is still
required before any further boot.

2026-10-26 phone overlay0006 integrates the reviewed method5 write ABI and two
exact run73 paths into a default-off process-memory backend with preallocation
guards and full exit cleanup. Host/native13+13 C and6 Python checks pass, as do
artifact integrity and a fresh exact-rootfs QEMU-user RPATH/loader/`-W` probe.
It is not phone-qualified. Other method families, persistent storage, DSP-mapped
file data and every remaining peripheral gate stay open. See
PHONE-RPC-RAM-FILES-20261026.md.

2026-10-26 phone VFS overlay0005 fixes reproduced alias/ancestor ownership before
volatile writes. Host and native Actions40256968720 pass11 release +11 ASan/UBSan
and6 Python; the new two-ELF artifact and exact-rootfs QEMU-user linking also pass.
The original apps_std test now calls deinit; only the isolated alias fixture
checks leaks, because the root-tree destructor is still absent. Writable ABI
dispatch, bounded preallocation, RAM cleanup integration, missing OEM lookups
and DSP mapping remain unresolved. See PHONE-RPC-VFS-LIFETIME-20261026.md.

run73 resolved installer permissions and exercised real ODM reverse reads,
but missing OEM/board lookups and two write refusals still block acceptance.
Automatic Android return134.0s; seven samples match, no stream/manual recovery.
The saved tail cannot prove the initial attach or registry reads. A phone-only
read-only PCB mapping and three sanitizer-backed source overlays are now prepared;
release9 and ASan/UBSan9 host tests pass, not native/rootfs/phone qualification.
Shared Pad recipe stays unchanged. Writable registry ABI, DSP library mapping,
other IDL families, actual samples and accuracy remain open. See
PHONE-PCB-MAPPING-20261026.md and SENSOR-REVERSE-FILESERVER-20261026.md.

run72 failed before a successful reverse daemon launch: root umask077 made new
installer directories0700, so UID65534 strace could not stat the executable.
Android returned automatically101.9s, seven samples match; platform regression
passed, no critical signatures in the bounded failure tail. Hardware retry is
latched. The exact executed helper reproduces0700 on the host. Fix new parents
explicitly0755, never relax existing ones, and test actual installation under
umask077 plus real UID65534 reads in the exact-rootfs synthetic sandbox. Prior
QEMU only tested synthetic-process launch and missed the installer interaction.
No successful reverse file service, sensor stream or remote release is claimed.

run70 owner session passed the requested visual display/scaling, real touch,
Settings and on-screen keyboard checks; automatic Android return189.9s and
seven matching samples. New unattended run71 passed one corrected SNS attach
ioctl and immediate local close, plus display/GPU/desktop/platform/health;
Android return104.6s, seven matching samples. Local close is not a DSP release
acknowledgement. No reverse server, registry service or streams ran. Historical
run69 halt/ledger stay immutable, with a new source-bound grant for this scope.
The next bounded reverse-fileserver helper is pending ARM64/QEMU qualification,
not a sensor acceptance. See SENSOR-REVERSE-FILESERVER-20261026.md.

Latest run69: display/GPU/ordinary-user desktop/platform passed; FastRPC registered
six contexts, but the pre-ioctl device guard refused absent misc ancestry.
Pinned source never sets miscdev.parent. Automatic Android return103.1s, seven
baseline samples match, no flash/manual recovery or critical kernel evidence.
The failure halt remains set; no automatic hardware retry/rearm. Offline guard
correction uses unique bound RPMSG ancestry/ADSP label and secure misc devnum;
four additional topology tests cover the actual parentless misc shape. No first
attach, reverse RPC, registry or stream acceptance. See SENSOR-FIRST-ATTACH-20261026.md.
run68 below remains the most recent complete isolated-platform pass.

Current run68: shared-core Actions40226313784 and independently bound artifact
pass. Exact phone ADSP/graphics, explicit display, GPU readback, ordinary-user
desktop software, CPU/input/battery/thermal inventory and health jointly pass.
Automatic Android return93.6s; seven baseline samples match; no flash/manual
recovery/radio/streams. This supersedes the pending/run67 snapshots below.
Software-only desktop acceptance keeps combined WiFi false intentionally.

Phone sensor runtime links pass exact-rootfs host QEMU. A private5-ELF/923-data
archive now excludes Pad auto-attach hooks/matrix, firmware and modules. It is
not attach/stream eligible. HAL-reported sensor families are retained separately
from raw identity. WLAN active BDF/regdb selection is known; SAR script/XML and
vendor selectors are reviewed, but effective limits/units/acknowledgements and
BT provenance remain open. See SHARED-DISPLAY-CORES-20261026.md,
PHONE-SENSOR-DATA-20261026.md and PHONE-RADIO-SELECTION-20261026.md.

Current run67: guarded matching-module rootfs and exact phone ADSP single start
pass; display activation is blocked by shared CEC/UBWC dependency install rules.
Android returns automatically in70.9s with seven matching baseline samples.
No run68 has started. Explicit bound generic-core/data-table prerequisites pass
seven synthetic tests; actual-rootfs Actions40226313784 is pending. Earlier
CEC-only emulator failures are retained, not accepted. See
SHARED-DISPLAY-CORES-20261026.md.

Phone ABI-reference libraries match the original project's pinned binaries;
923-file private data-only sensor package is verified, not delivered/attached.
Android logs confirm actual peach BDF/regdb selection and a separate wifisar
service. SAR/power and BT provenance remain open; no further radio activation.
See PHONE-SENSOR-DATA-20261026.md and PHONE-RADIO-SELECTION-20261026.md.
Older pending/run66 snapshots below are historical.

Current provenance hold: inherited ADSP is Pad reference data (6/58 current
stock matches), and WLAN/BDF/regdb also remain reference inputs. Legacy payload
hardware reuse is blocked. Exact phone OTA ADSP matches58/58 and passes actual
PIL/reserved-memory structural review, but authentication/ABI/streams remain
unaccepted. Prior scan/HTTPS proves historical traffic only; phone BDF selection
and SAR/power policy must precede further RF. Guarded matching-module rootfs
assembly/QEMU run40223386011 is pending; no phone run after66 yet. See
FIRMWARE-PROVENANCE-20261026.md. The first assembly40221133412 is held because
preinstalled modules need explicit peripheral dependency-load isolation.

Original sensor importer passes host-only byte/permission checks on744 owner
registry files; reverse-RPC ABI/attach/streams/axes remain open. Both stock amps
show a PID2308-specific callback, still indirect evidence. Do not use the draft
driver's profile-writing probe as a passive identification operation.

Current run66: two SCMI schedutil policies and CPU cooling devices register after
bounded, exact-hash loading of the already delivered CPUCP/socinfo modules. Full
ordinary-user desktop/GPU/replacement-network HTTPS/BT components/input/battery
regression passes; Android returns in148.6s with seven matching samples. Run64
identified the unbound mailbox and separate UCSI deferred-role issue; run65
refused before module loading on pending ADSP battery temperature, recovered
in73.4s with matching samples. Five actual-shell thermal gate tests now retain
strict CPU sensor requirements without requiring early ADSP battery telemetry.
No stress/voltage/frequency override, role switching, audio or sensor stream.
SCMI bus name is scmi_protocol; the former empty scmi inventory was inconclusive.
See PLATFORM-MODULES-20261026.md. Frequency transition accuracy, thermal policy
under load, power/PD, Type-C and sustained stability remain open.

Saved owner ACF length/hash independently match the existing reference bytes,
and actual-file host ASan/UBSan preflight passes. This supersedes the old false
content-match flag only. Exact amplifier PID, independent calibration, dynamic
protection and MI2S route still block audio. The current draft's probe writes
profiles and is not a passive identification tool. See OWNER-ACF-BINDING-20261026.md.
Fresh rootfs03ecbd66 remains separate pending same-kernel QEMU handoff/deadline
verification; all-feature adaptation remains incomplete. Older snapshots follow.

Current run62: quarantined WSA branch, new-network scan/authentication/IPv4/route/
certificate-verified HTTPS and ordinary-user desktop with three bound HTTPS
samples jointly pass. Android returns in141.8s, seven baseline samples match.
Run59/60/61 recovered in128.7/117.3/134.7s with matching baselines. Their verifier
issues were reviewed offline: await LastScan completion, observe delayed IPv4
without reconnecting, and do not treat optional getent/ping timeouts as failed
core networking. Core query/HTTPS timeout and kernel/recovery failure gates stay.
Software-only desktop acceptance cannot claim combined WiFi acceptance.

New rootfs03ecbd66 is separately downloaded/hash/runtime-verified, not substituted
into the hash-bound hardware image. Audio topology CI40213811895 and AW88461
offline CI40214539084 pass; downloaded reports/source hashes match. The AW draft
is object compile only. Actual chip ID, owner protection/tuning and full MI2S
machine/topology/clock route remain missing. Saved secondary-MI2S phandles and
raw-active-low versus descriptor reset polarity are independently documented.
Sensor config matches the original narrow shim; matching text is not DSP ABI or
registry/calibration acceptance. Full feature register includes camera/modem/GNSS/
NFC/fingerprint/IR/Hall/ToF/haptics/thermal/power/RTC/suspend/storage gaps. Run63
only adds passive sysfs inventory, not function claims or new peripheral activation.

Current run58: ordinary-user active Wayland GNOME, its project Mesa mappings,
Settings network process/application bus, three unchanged-compositor/service
samples and three bound WiFi certificate-verified HTTP200 probes pass. Android
returned in144.8s, seven samples match; no flash/recorded partition writes/manual
recovery. Visible-screen/touch/UI/suspend/long-duration acceptance remains open.
The optional logind Desktop field is empty here and must not reject an otherwise
verified GNOME session. Run56/57 combined failures and recoveries are documented.

Critical audio correction: saved stock runtime FDT disables the WSA macro and
all WSA884x/WSA883x speakers directly or by ancestry. Both AWINIC smartpa nodes
are enabled. The handed-over run42 DT enabled a WSA884x pair and WSA playback
link. Its PCM and route-control progress is not stock speaker-path progress.
That boot-image hash is now held against reuse. Review effective ancestor
status before selecting hardware; do not fix a copied QRD route by trial streams.
Correct AW88461 identity, driver, owner-matched protection/tuning and gain policy
remain open. See RAM-AUTOMATIC-ACCEPTANCE-20261026.md. Older snapshots follow.

Current 2026-10-26 run55: automatic association/IPv4/default route/DNS and
WiFi-interface-bound HTTPS pass, HTTP 200 and ssl_verify_result 0. RAM staging
time was corrected to the host; the monotonic recovery deadline remained exactly
unchanged and no RTC write was requested. Android returned in 129.3s, seven
sampled keys match, no flash/manual recovery and host firewall cleaned. GPU
readback/project GNOME Mesa and combined inventory/telemetry/service gates pass.
No owner interaction was requested; visible desktop, physical touch and UI
regression are not newly accepted. Run54 had TCP success and certificate failure
with old September timestamps; its exact certificate cause was not captured.

The owner directly grants unattended RAM work until 2026-10-26 04:55:14 Asia/Shanghai.
Time-window checks require a 780s recovery margin, no individual-grant fallback
for unattended runs, and no prior recovery/kernel health failure. This overrides
older per-run authorization statements only during this specific window. No flash
or partition writes. Audio SoundWire/EIO, sensor streams, independent RTC/network
timekeeping, real touch/UI, suspend and sustained use remain open.

Current run53: Android returned in 128.6s, seven sampled keys match, zero recorded
partition writes, no manual recovery, host firewall rule removed. WiFi scan,
authentication, active UUID, IPv4/default route and getent DNS completed. Optional
ping was skipped correctly. Interface-bound HTTPS returned curl 28; complete
traffic and GUI acceptance remain open. Owner confirms other devices can use
the same network. No DNS/TCP/TLS timing evidence exists for run53, so no specific
driver, address-family or target-reachability diagnosis is established.
GPU/project GNOME Mesa and combined inventory/telemetry regressions passed;
audio/sensors stayed read-only and there was no owner interaction window.

Subsequent offline-only work binds HTTPS to the tested IPv4 path and retains
numeric DNS/TCP/TLS/first-byte/total timings on errors without exposing peers.
Eighteen Linux checks and three actual candidate ARM64 curl loopback TLS checks
pass, including certificate rejection and a timeout after TLS. No phone or
external network used in those checks. Run54 stage/delivery preparation passes
but needs a new owner grant. This does not prove the phone timeout is resolved.
Older run52/current-state statements below are historical snapshots.

Current run52 evidence supersedes older snapshots below: one RAM grant consumed;
Android returned in 113.9s, seven sampled keys matched, zero partition writes,
no manual recovery. Supplicant was ready before explicit WCN probing. Target
scan, authentication, active UUID and IPv4/default-route checks completed.
Missing ping raised an uncaught FileNotFoundError before DNS/HTTPS, so complete
WiFi and GUI acceptance remain open. This does not establish a driver fault.
GPU readback/project GNOME Mesa and combined inventory/telemetry stages passed;
there was no owner touch window. Real Bluetooth file receipt remains run51 evidence.

The checker now returns sanitized missing/unavailable executable categories,
continues past missing optional ping/getent, and fails missing core clients or
failed interface-bound HTTPS. Working and public copies match; 15 Linux offline
checks pass in each copy, with 14 constructed stage checks per run52/run53 and
a full run53 image/payload/service/localhost delivery check. No phone operations
were performed for this repair. Run53 is prepared but needs a new owner grant.
The complete refreshed rootfs has now been downloaded and independently verified
on the host; it remains hardware-untested and is not substituted in the RAM plan.
Audio SoundWire/EIO, phone sensor streams, full touch coverage, suspend/resume
and sustained use remain open. Older future-tense run52/download statements are
historical records, not current authorization or acceptance.

Run51 latest: owner confirms actual Bluetooth file reception. Android returned
in221.5s, seven sampled keys matched, no flash or manual recovery. GPU/project
GNOME Mesa pass;33 touch downs observed, no full-area/multitouch acceptance.
WiFi authentication was never reached: actual rootfs lacks wpa_supplicant,
its D-Bus activation file and systemd unit. The phone Base/explicit-seed build
now requires these dependencies; normal Pad Desktop-ISO assembly is unchanged.
The verifier checks every declared seed plus actual ARM64 clients and activation
contracts. The old rootfs is correctly rejected. Refreshed full-rootfs Actions
40204541108 builds and passes8 tests plus actual runtime/activation checks.
Host full-download verification and hardware handoff remain; do not relabel the
old image as refreshed.

Fourteen authenticated-index packages are prepared as a RAM-only radio overlay,
preserving working BlueZ core. Three ARM64 QEMU startup checks and the actual
supplicant manager reply on a private host bus pass, with no wireless interface.
Eight fake-process checks pass. Run52 will validate supplicant before explicit
WCN probing, skip the owner window if automatic WiFi fails, and avoid redundant
post-interaction WiFi queries. It is offline-only pending a new owner grant.
Audio SoundWire/EIO and actual phone SSC sensor streams remain open.

Run50 latest: returned Android in248.8s, seven sampled keys matched, no flash or
manual recovery. GPU readback/project GNOME Mesa pass; touch records67 downs,
not full-area/multitouch acceptance. Owner reports Bluetooth pairing works but
Send Files does nothing, and WiFi GUI sees no surrounding networks. The2412MHz
scan saw one BSS; association/DHCP/traffic remain unaccepted. Postcheck stopped
at the WiFi interface-query phase and its50s outer timeout requested recovery.
Do not claim a driver root cause from this bounded evidence.

Missing bluetooth-sendto/OBEX components are now prepared as a separate additive
RAM overlay; nine signed-index packages, two ARM64 QEMU startup checks pass,
existing BlueZ core preserved. A bounded automatic NetworkManager WiFi checker
passes six offline fake-process checks. No raw scan/managed-state handoff; owner
WiFi GUI regression is offered only after automatic authentication/DHCP/HTTPS
passes. Radio query timeout skips the interaction window and recovers early.
Run51 is prepared offline only and requires a fresh owner grant.

Audio saved evidence has six additional incomplete macro/slave routes; this is
not proof of the SoundWire EIO cause. No audio stream is authorized by the
offline route checker. Phone sensor ROM/config was extracted on the host and
generic ARM64 userspace Actions40198265425 passed8+7 software tests; phone DSP,
identity, loader semantics and RAM calibration/registry policy gates remain.

Latest run49 consumed one additional owner grant: Android returned in105.3s,
seven sampled keys matched, no flash/partition writes or manual recovery.
The activation -> user-graphics-environment refresh -> GDM restart order now
passes hardware acceptance of library selection: GNOME maps project Mesa26.2.3,
and the same run passes an Adreno830v1 4x4 GLES readback. This closes the earlier
GNOME distribution-Mesa selection gap, not long-duration compositor/visual
acceptance. WLAN scan4BSS/BT discovery/input presence/power telemetry regressions
pass at their stated scope. Audio remained read-only; SoundWire/EIO and phone
sensor configuration are still open. All four recorded RAM grants are consumed.

Latest 2026-10-25 multi-target RAM acceptance supersedes older hardware status:
run46/47/48 consumed the current three-run grant. All returned to Android with
seven sampled keys matching, no flash/partition writes or manual recovery.
Phone WSA backend routing fixes PCM open EINVAL: HW_PARAMS and PREPARE pass,
but WRITEI_FRAMES reaches EIO with SoundWire clash/CMD errors. Do not enable
an automatic speaker UCM or repeat streams until the phone port/timing path
is reviewed offline. Run48 audio was read-only. Project Mesa26.2.3 performs
an Adreno830v1 4x4 GLES clear/readback; GNOME still maps distribution Mesa.
The native-activation -> environment-refresh -> GDM-restart ordering fix is
offline-checked only. WLAN scan/BT discovery, input-device presence and battery
telemetry are partial gates. Phone sensor ROM/config is missing; existing
OPD2413 registry assets must not be installed on PJZ110. See MULTI-ACCEPTANCE-20261025.md.

New offline increment: patch0011 derives the clock floor from the actual two-LM
reservation and splits pipes against the inverse burst/inefficiency budget of
the real OPP before assignment. Aggregate bandwidth is unchanged. Actual compiled
DTB is mandatory, budget evidence version3 binds its hash, and private packaging
rejects older evidence. Ten ARM64 sanitizer C checks and61 ARM64 tooling tests
pass without skips in40068074272; the complete kernel artifact is downloaded and
verified. Matching refreshed rootfs/GNOME/QEMU40068689660 passes; its large artifact
has been re-downloaded and independently cross-verified on the successor host, and
the private candidate e5c6944 is assembled with read-back checks. Source fixtures
are not physical allocator/SSPP acceptance. See DPU-OPP.md.
Authorized single RAM acceptance for e5c6944 was consumed by an environment
failure: the successor host is a VMware VM whose USB passthrough dropped at the
bootloader-to-NCM re-enumeration, the rootfs transfer stayed at zero bytes, and
the phone self-recovered via the in-image 900-second deadline with all seven
metadata keys matching and zero writes. Preflight and activation never ran, so
patch0011 remains untested on hardware and this is not regression evidence.
Retry requires a new authorization plus fixed USB auto-attach (or a physical
host). See native-acceptance-e5c6944/OUTCOME.md.
No new phone operations; previous single-test authorization remains consumed.

Latest separate authorization: one native RAM boot and one explicit activation
completed. Real preflight passed; module load returned, but DPU atomic performance
check rejected with -7. Host requested early recovery and Android returned at
135.4s with sampled metadata matching. No flash/partition changes. The one-test
authorization is consumed; further phone operations require a new authorization.
The 1GHz success fixture missed the actual 575MHz MDP OPP, while the present
full-width budget requires 711529412Hz. Current candidate is ineligible for retry.
Bind compiled-DTB OPP, actual topology/plane splitting and performance checks;
review vendor/original processing before correcting the votes, never raise the
OPP just to suppress rejection. Physical display and all other acceptance gates
remain open. See FIXED-PHY.md for the separate hardware evidence.

Fixed-PHY increment: vendor V7.2 timing_val/enable/commit path confirms direct
14-register production values. Patch0009 selects them only for the attached
AA569/SM8750/DSI0 fixed-rate candidate and synchronizes shared host timing.
Patch0010 fixes ignored runtime-PM failures and PM/OPP cleanup on clock failure.
Ten real C ARM64 ASan/UBSan checks and kernel build40065006440 pass. Actual
CCF/TE callback fixtures and 61 ARM64 tooling tests pass in40065992683; matching
GNOME/QEMU40066356160 passes. These verify source calculations and guarded
interfaces, not physical clocks, TE, framebuffer takeover or panel output.
An explicit RAM-only one-shot preflight/loader is implemented, without an auto
service. Actual module loading is untested. QEMU mocks USB active and uses a
fixture observation clock; real deadline threshold tests remain independent.
Default native packaging remains closed; an explicit reviewed-evidence gate
permits host-only private candidate preparation. No phone operations or hardware
authorization; physical display/touch/WLAN/GPU acceptance still blocks a usable
combined port. See FIXED-PHY.md for the exact evidence and remaining gates.

2026-10-24 PLL/PHY audit: nominal 1.3632 GHz and valid 2x/3x VCO values are
exact in the 18-bit fractional arithmetic, but six of fourteen generic D-PHY
timing fields differ from the final AA569 production DTS override. Actual C
platform/vendor arithmetic checks added; ARM64 sanitizer audit40062728159 passed
66 PLL cases plus PHY checks. Downloaded artifact, nine public source blobs and
local/ARM64 C results match. Kernel job skipped; runtime artifacts unchanged.
Do not promote this to physical frequency/timing equivalence or patch the generic
PHY with board bytes. Trace vendor V7.2 timing commit/overrides and shared CCF
pixel/byte selection next. See PLL-PHY-AUDIT.md. No phone/kernel/image changes.

2026-10-24 D07 increment: explicit bounded whole-group DSI API and the AA569
13-group sender are implemented, with actual C packing/resource/failure tests.
No cross-call queue and no silent serial fallback. Nine local/ARM64 C checks
(Actions ASan/UBSan) and 53 tooling tests pass. Kernel/module build40058811743
and refreshed matching GNOME/rootfs/QEMU40059533734 pass; all artifacts have
been downloaded and checked against manifests, module release and group hashes.
Physical PLL/TE/burst timing, takeover and D16 activation are still open.
See DSI-BATCH.md. Zero phone operations; native desktop packaging stays disabled.

2026-10-24 follow-up: the private payload now has a versioned release/profile/
helper hash manifest and a data-only stage across switch_root. Old or partial
payloads fail closed, merged-/usr is handled explicitly, and the helper remains
non-executable in /run. Host and ARM64 Actions suites: 53 passed. The new QEMU
observer in 40056382745 verified copy/permissions/failure controls after
switch_root, handoff and 180-second expiry/reboot; downloaded evidence matches.
See NATIVE-HANDOFF.md. Additional pinned vendor review confirms deferred
kickoff/resource cleanup in FETCH_MEMORY, FIFO/non-embedded overrides and the
broadcast early-flush exception. Nominal single-link groups peak at 312 bytes;
wire timing equivalence and actual PLL behavior remain unproven.
D16 activation and D07/D10/D17 physical timing/resource work remain open;
native desktop packaging is still disabled. No hardware operations this round.

Current offline gate, 2026-10-24: see OFFLINE-NATIVE-GATE.md. No hardware work
in this phase. D15: native helper/SPR identity source fixed and host-checked,
new ARM64 build 40051765091 and eight C ASan/UBSan checks passed. D16: full
rootfs aliases bypassed diagnostic manual loading; the fail-closed kmod policy
now passes actual QEMU loading controls with the rebuilt kernel in 40054456226.
Native desktop packaging remains disabled until rebuilt policy, handoff and
explicit activation are validated. D07/D10 timing and physical acceptance stay
open; these new findings are not a proven cause of the default desktop black screen.

D17: the default simple-framebuffer node has no clock/power-domain/supply
references. Archived phone logs show simpledrm registration before unused
clock/domain cleanup. Review the pinned sysfb driver and actual display resource
ownership; this is a lifecycle gap and a black-screen hypothesis, not a proven
diagnosis. No blanket ignore-unused boot flags or speculative hardware trial.

Actions40051767501 validates the new kmod policy with the original pinned
kernel and refreshed rootfs. D16's explicit activation/cross-root path remains
open and native packaging remains disabled. The rebuilt identity-fixed kernel
combination 40054456226 passed independently using integration 2957513a and
kernel artifact d624154c. This closes the offline build/kmod/handoff portion,
not physical display acceptance or explicit native activation across switch_root.

| ID | Temporary choice / location | Reason and impact | Removal criterion |
| --- | --- | --- | --- |
| D01 | Community low-memory fallback in the default DTS | The owner-specific calibrated candidate now uses actual 15-bank runtime RAM and excludes every stock protected interval offline, but bootloader fixups and actual RAM use are untested | Verify memory/fixups through a bounded RAM boot before promoting the private calibration to the default board profile |
| D02 | Firmware framebuffer in phone DTS; native candidate identity-domain patch0005 | Enables testing inherited display without inventing a panel sequence; resource lifetime and pixel format are not hardware verified | Port and verify native phone panel/DSC/timings/power sequence |
| D03 | Pad-maintained SM8750 kernel as a pinned platform base | Reuses platform fixes only; its board support is not phone support | Track upstream and replace with a maintained phone kernel after equivalent validation |
| D04 | Sleep targets masked in GNOME staging rootfs | Avoid entering untested phone suspend/resume paths; ordinary standby is unavailable | Cold-boot and repeated suspend/resume tests on the phone with independent recovery |
| D05 | Phone-only MSM DSI native422 RC glue in kernel-patches/0001 | Selects existing 422 tables and adapts the DRM group-bpp arithmetic to MSM physical-bpp consumers; complete PPS/RGB controls pass offline, actual pipeline remains untested | Replace when upstream has equivalent format/rate semantics, preserving the byte-exact PPS and real-device regression results |
| D06 | Native422 command HS-ceiling selection0002 and fixed AA569 burst-budget patch0006 | Replaces synthetic CMD-porch clock selection only for an explicit characterized ceiling on a single D-PHY link; validates packet budget and conservatively scales DPU performance votes for6800us with new-state/OPP/ICC rejection; does not program a hardware transfer timer or prove PLL rounding; peak votes intentionally overestimate until measured | Replace with equivalent upstream command-transfer timing support and validate bandwidth, actual clocks, frame completion and power-cycle regression on hardware |
| D07 | AA569 fixed DBV1433 with bounded synchronous vendor-group submission in patch0008 | Exact production bytes, group boundaries, resource lifetime and error controls pass host C checks; only the experimental native DTB enables the component, no brightness UI is enabled; physical group/TE timing remains unverified | Validate actual PLL/SPR/transfer scheduling and physical init/power cycles, then add validated PWM/brightness behavior |
| D08 | SM8750 native422 DPU corrections in phone-only kernel patch0003 | Bridges vendor container/initial-line, full-ICH precision, modern-wrapper and PPB requirements while preserving physical-bpp semantics; actual output remains untested | Replace with equivalent upstream changes and preserve vendor/register-capture controls plus real-device regression |
| D09 | Private AA569 fixed-profile format in kernel/spr-aa569 and spr.py | Separates private coefficients from public sources and bounds the decoder/transaction planner before runtime integration; not a standard firmware ABI and not a working SPR pipeline | Replace with an upstream panel/DRM configuration interface when available; retain strict field checks, private-data isolation and vendor-equivalent packing |
| D10 | Opt-in fixed-profile SPR CPU startup/PM backend | Reuses community quiet-pipeline approach with private AA569 data, all-pipe UDC preflight, idle/clocks/reset guards and explicit display exclusivity; no DMA, live profiles, partial update or fingerprint/UDC functionality | Replace with reviewed upstream SPR/REGDMA integration after hardware timing/ownership/power-cycle validation; retain strict profile/geometry and no-private-data-in-Git controls |
| D11 | WLAN-only stock-minimum constraints, fixed IO system-load and reference PCIe PHY supplies | pwrseq only bulk-enables supplies; phone consumer requests differ from the base parent range/Pad minimums. PCIe PHY rails and RF clock are same-SoC reference candidates, not independent electrical proof. Exact OTA inputs now match owner hashes, but active BDF selection and SAR remain unverified | Verify exact phone PHY/shared-rail behavior, firmware/board/revision/SAR and replace fixed load with an upstream consumer request when available; do not promote this standalone tree before hardware acceptance |
| D12 | GPU-only tree uses pinned platform GMU/clock/OPP graph | Phone chip ID and microcode reserved memory match, and the correct signed ZAP now matches the owner hash; authentication, voltage/frequency behavior and hardware renderer remain unverified; headless mode needs explicit separate_gpu_kms=1 | Verify bounded isolated authentication/render/power tests, then replace with upstream board support and integrate only after real regression |
| D13 | Separate RAM desktop profile, fixed USB debug services and 900-second absolute deadline | Provides an observable reversible userspace handoff before storage installation; root shells are restricted to trusted USB, there is no persistence and no unattended permanent desktop | Validate phone USB/handoff/recovery and individual hardware first; replace with an explicitly chosen persistent layout/account policy and packaged optional debug support |


Unimplemented peripherals are tracked in STATUS.md, not represented as working.

## 2026-10-24 本地真机补充

D14：ABL改写根model/compatible，导致手机physical-platform误拒绝。已按原项目model＋chassis方式修复并通过正反例，真机已越过切根门槛并进入systemd/GDM。继续保留VMID3、Gunyah及无绑定驱动条件。保持900秒截止的真机会话已返回原Android，单次交接与返回验证完成；物理显示、触控、GPU及WLAN仍独立待验收。
2026-10-26 phone-only RPC follow-up: input TYPE_SEQ now selects its own checked
descriptor and consumes sequence metadata correctly, including empty sequences;
the original input golden-wire test remains unchanged. Output TYPE_SEQ is
explicitly unsupported before ioctl, and allocation-failure handling and other
IDL families are not exhaustively qualified. Native rebuild and exact-rootfs
CLI/linking passed Actions40252529300 plus host QEMU-user; writable-registry
ABI, absent OEM data and DSP library provenance remain gates.
See PHONE-PCB-MAPPING-20261026.md; source unit tests do not qualify phone streams.


2026-10-26 run80 safely returned to Android after the metadata-only SSC probe stopped before a qualified result. The reverse service had one attach, module policy and private inputs were unchanged, and there were no samples or streams. Exit255 did not establish a discovery timeout. The diagnostic version retains the original 8-second deadline, validates exact public failure categories, records systemd execution status before cleanup, and bounds private raw failure output to RAM-only root-readable files. Fresh native and full-system QEMU verification is required before any new source-bound hardware review. This is not sensor-stream or camera/audio acceptance.
