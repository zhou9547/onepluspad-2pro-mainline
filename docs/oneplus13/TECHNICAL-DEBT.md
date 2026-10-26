# Technical debt (single register for the phone)

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

