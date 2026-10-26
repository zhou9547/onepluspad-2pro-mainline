# Camera, speaker and SSC offline component results

The public follow-up commit `b9b2b0687387ffeed8187aeb0b5d65d9e310b72a` passed
Actions 40291375012 (native ARM64 SSC and composite controls) and 40291375256
(native ARM64 capture/speaker topology compile and decode). A fresh exact-rootfs
QEMU run with the new composite helper is still pending; no new phone boot plan
is created until that source-bound proof is available.

The composite discovery runner now bounds metadata readiness to three seconds and
the actual SSC unit query/stop/state checks to 16/3/2 seconds. Its host suite has
16 additional cases for duplicate attach, incomplete trace, oversized trace or
output, launch/query/stop timeout, nonzero exit, residual activity and incomplete
four-type metadata. A dummy-virt-only concurrent-unit self-test is embedded in the
exact-rootfs assembly recipe; it is pending a fresh VM rebuild and remains separate
from phone qualification. The two AudioReach drafts also enforce one decoded PCM
capability block (S24_LE, 48 kHz, two channels) and have a dedicated ARM64 compile
workflow. Neither change enables streams, calibration, protection or RF.

Native ARM64 Actions40285807929, source4d16034f4c95445d372e14a7f93002c5a18e75f6,
passes the joint camera/amplifier object build with W=1 and -Werror. It compiles
CAMSS, CSID980, VFE980, standalone CSI PHY, CCI, CAMCC, CAMBIST MCLK and the
existing AW88461/shared-parser components. Ten object hashes are recorded;
nine exported objects were independently hash/ELF checked (the shared parser
was compiled but not exported). Twenty-three original patches retain their
hashes. Two separate local corrections remove obsolete locals and return PHY
timing/mode errors before configure/power. Seven actual extracted-function
success/failure controls pass release and ASan/UBSan, together with the actual
amplifier function/parser synthetic checks.

This creates no phone DT integration, installed module or boot image. The
phone's sensor driver, board power/clock/lane graph and custom ultrawide PHY
sequence remain unqualified; RDI transport is not a full ISP/libcamera port.
Speaker chip identity, independent calibration and dynamic protection remain
incomplete despite the saved ACF content match.

Native SSC Actions40285807884 passes three release/three ASan+UBSan executables
plus thirteen wrapper/control checks. Its isolated archive now includes four
generic runtime libraries, package/source identities and copyright files.
Every dependency in the new loader report exists inside the target tree.
Full exact-rootfs VM verification passes the actual UID65534 sandbox, native
guard checks, a real two-second synthetic service timeout (2.858s including
cleanup), handoff and automatic300s VM deadline. No QRTR query or measurement
was executed. The actual embedded scripts/archive/manifest are hash-bound.

This supersedes the initial QEMU-user result: that check could fall back to
host ARM64 libraries, and full VM correctly rejected the incomplete archive.
Both failed VM attempts and the corrected gate record are retained. No phone
was used to debug the dependency problem. Discovery with the reverse file
service still needs a source-bound joint plan and cleanup qualification.

The saved phone OTA audio XML independently confirms microphone TX3 and
Secondary MI2S speaker backends, both48kHz/two-channel/24-bit. The previous
mixer XML matches, but the earlier resource-manager reference differs from
this OTA; use the newly bound source. Separate capture-only and MI2S speaker
drafts compile and decode with the original pinned AudioReach macros, producing
the actual kernel widget names without Pad TDM/WSA/DP routes. These drafts have
no UCM or runtime installation. Android ADC channel-map controls differ from
the selected mainline WCD939x mapping, so copying mixer settings or opening PCM
is not yet qualified. Speaker protection cannot be replaced by a config flag.

Firmware, factory data, XML contents and identifiers remain local. Phone state
remains Android after run79; its automatic return and seven baseline matches
are unchanged. Sensor samples, camera captures, audio streams and RF are not
accepted by these offline results.

2026-10-26 run80 safely returned to Android after the metadata-only SSC probe stopped before a qualified result. The reverse service had one attach, module policy and private inputs were unchanged, and there were no samples or streams. The probe now carries a 12-second discovery deadline plus whitelisted failure classes, so a future attempt can distinguish service lookup, QRTR/socket setup, policy refusal and timeout without exposing raw private output. This is not sensor-stream or camera/audio acceptance.
