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
Run82/83 restored the fixed previously tested WLAN/BT software/firmware bytes
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
