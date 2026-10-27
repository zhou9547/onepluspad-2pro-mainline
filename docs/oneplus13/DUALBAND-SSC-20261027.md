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

# Joint 5 GHz and SSC metadata continuation

Baseline: `570428aeddf591b518112e66b239cf07a643f65a`, the complete Actions
image accepted by run91 for 2.4 GHz association, DHCP and LAN HTTP 200.
Run88's physical display/touch/GPU/desktop and Bluetooth receipt are historical
evidence. They remain regression requirements for a new candidate.

## WiFi

The first joint RAM boot used the immutable run91 image and source-bound
new helpers, not a newly assembled complete Actions image. It returned to
Android in 268.1 seconds, with seven baseline properties equal and no partition
writes. Stock Android confirmed the target on 5240 MHz before and after it.
The 5 GHz target was absent from the Linux directed scan. The 2.4 GHz target
was seen, but activation timed out; neither band passed traffic acceptance.

Post-return audit of the retained kernel tail found IOMMU context faults,
WLAN hardware restarts, invalid runtime IDs and vdev failures. The original
selected-signature screen missed these; its zero count is not a clean health
verdict. Hold this candidate. A disconnected stock-country transition was
acknowledged by the selected PHY, but has been withdrawn from the active
verifier. No new country/channel/SAR transition or IOMMU bypass is enabled.

The same WCN7860 hw2.0 / single-pdev firmware configuration has a reviewed
community scan fix in [Armada PR 594](https://github.com/armada-os/armada/pull/594),
head `9b2654ceeb3be0a2a8dd6bf5d6b0d3272175885f`. Its first single-pdev
frequency-range fix already exists in the pinned kernel. Preserve danyi's
attribution and import only its remaining two unchanged GPL kernel patches:
firmware-derived range batching, then associated-scan TX drain/home-channel
rest and recovery pause ownership. They apply cleanly to the exact pinned
kernel; other hardware/modes retain their existing path. Firmware bytes and
qualified board inputs are unchanged. This is a candidate fix, not proof of
the cause of every observed IOMMU fault or of hardware success.

`check-wcn7860-scan.py` compiles seven actual patched helpers, with release
and ASan/UBSan checks for hardware scope, malformed ranges, request order,
allocation errors, cleanup and TX failure paths. It cannot simulate firmware
or kernel event scheduling. Full kernel compilation and joint acceptance are
still required. `ram-kernel-health.py` reads bounded full kernel history and
rejects DMA faults, restarts, invalid runtime IDs and vdev failures; subsequent
RF phases must not continue after such a fault.

The parser accepts the real `iw` whole-MHz decimal format (`5240.0`) as well
as integer output. Archived PHY output exposed this before a phone boot.

Private runtime credentials may select `band: "a"` for 5 GHz or `band: "bg"`
for 2.4 GHz. NetworkManager receives the matching band constraint. The verifier
then reads the actual link frequency with `iw dev <interface> link`; a missing,
ambiguous, wrong-band or failed observation stops before traffic acceptance.
Association, a matching actual band, IPv4/default route and interface-bound
LAN HTTP 200 must all pass. A successful 2.4 GHz connection is never reported
as 5 GHz acceptance. Credentials and raw link output are not published.

`oneplus13-wifi-radio-report.py` reads channel capabilities and regulatory
domains without requesting a scan or setting a country/SAR value. Its numeric
report distinguishes disabled, passive/no-IR and DFS channels. This is needed
to diagnose an invisible 5 GHz target before choosing a driver change. No
unproven firmware swap, channel-flag bypass or power-policy SET is introduced.
External DNS/ping/HTTPS diagnostics now require explicit runtime opt-in;
the current owner's default remains LAN HTTP only.

The first full run built kernel/Mesa/SSC successfully; its GNOME job failed
on the signed Ubuntu snapshot provider's 502/503 responses. New builds avoid
unneeded APT translation indexes, retain finite transport retries and TLS,
and save the populated kernel ccache after a cache miss. The snapshot date and
archive-signature requirements are unchanged.

## SSC

Run81's saved stderr contains `g_value_set_boolean` / `G_VALUE_HOLDS_BOOLEAN`
assertions. The pinned libssc registers `available` as a string but its getter
writes a boolean. It similarly registers stream type/sample rate as strings
while returning uint/float. A phone-only patch corrects all three declarations.
The native regression compiles the actual sensor implementation and checks
false/true/false availability, numeric property reads and adjacent memory
canaries without QRTR, measurement commands or a device.

The original two libssc packaging patches and the one-way metadata send guard
are unchanged. The first joint boot discovered accel, gyro and mag metadata after this fix;
ambient_light remained unavailable. Evidence is a unique exact SHA256 match
of saved stdout to the deterministic public four-type output template, because
the raw RAM stdout was not retrieved before recovery. Do not relabel that as
a directly captured stdout transcript. The wrapper now emits a strict public
four-type inventory even on failure, while withholding raw diagnostics.
No sample/stream command was sent. These results do not qualify sensor axes,
rates, matrix or applications.
The all-zero mount-matrix warning is separate and remains unresolved.

The complete-image workflow builds the isolated probe at the same integration
commit as the kernel/GNOME/Mesa. Release and ASan/UBSan each require the new
property regression, the policy test, real send-boundary rejection and original
delivery test. Packaging checks source identity and every archive entry, stores
the probe in `/usr/lib/oneplus13-ssc`, and verifies its actual SquashFS bytes.
It installs no sensor service, registry or measurement policy. Discovery still
requires separately reviewed RAM-only private registry/file-server staging,
one attach, a hard deadline, clean stop and the existing metadata-only wrapper.

## Joint hardware acceptance

Prepare one new single-use RAM plan after the Actions artifacts are downloaded
and their hashes verified. Combine 5 GHz association/DHCP/LAN HTTP, a 2.4 GHz
regression, guarded SSC metadata discovery and preserved-feature checks.
Do not start a separate phone boot for each target. Use the registered device,
per-connection RAM identity, immutable physical storage, staged recovery timers
and seven Android baseline properties. No flash or persistent installation.
No new hardware success is claimed by the source or compile checks.

Follow the original project's next sequence: independent WCD microphone
capture and SSC/accelerometer before ambient light/compass/gyro integration;
speaker playback still requires phone-specific protection and calibration.
