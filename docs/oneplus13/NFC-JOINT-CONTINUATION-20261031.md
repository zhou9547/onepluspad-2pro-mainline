# NFC observation/cleanup delivery, 2026-10-31

## Priority correction

The owner confirms 5 GHz already works. Preserve the r191 5240 MHz acceptance
and both-band regression. The preceding milestone delivers the same WiFi
control path without a sensor-service prerequisite and with installed health
protection; it is not a new RF adaptation. Actions 41156920220 succeeded in
all five jobs for 9727c0c2204fa210a9aa8fe418b719f473a415d6.

## Reproduced defects and fixes

- Without multicast, wait_found() issued one target query and slept until
  the final deadline. It now waits only until the next one-second query,
  bounds each dump by the observation deadline, and checks again.
- Request ACK and dump DONE handling discarded concurrent multicast events,
  including those later in the same datagram. All relevant sequence-zero
  events are queued before processing replies, with a 128-event fail-closed
  limit. A queried target and an observed multicast remain distinct facts.
- Data without the requested ACK no longer qualifies a successful request.
- Cleanup previously swallowed every STOP/DOWN error and set complete=true.
  It now records responses, requires selected-device power-off readback, and
  makes cleanup failure fail the overall result. Only STOP EINVAL (already
  idle) and DOWN EALREADY (already down) are tolerated, with the same readback.
- A powered or ambiguous initial controller is not taken over. Device indices
  and wait durations are validated before opening the socket; RF waits are
  limited to 120 seconds. The helper reserves bounded protocol/cleanup time
  in addition to the requested RF window. A host timeout must accommodate it.
- The complete image now installs the exact polling helper, records its hash
  and checks the actual SquashFS bytes against both manifest and checkout.
  The binding service still only binds the controller; RF polling is manual.

## Primary reference review

The existing Pad kernel UAPI include/uapi/linux/nfc.h defines device-scoped
target queries, event notification and device power commands. Linux
net/nfc/netlink.c uses sequence zero for TARGETS_FOUND and returns EINVAL
from STOP when polling has already stopped. net/nfc/core.c returns EALREADY
from DEV_DOWN for an already-down controller and rejects an active target.
Those semantics justify the exact cleanup exceptions, not arbitrary errors.

References reviewed directly: torvalds/linux net/nfc/{netlink,core}.c.
No NFC firmware, DTB, GPIO sequence, RF configuration, kernel or Pad
integration is changed. Unit evidence does not prove physical NFC works.

## Joint hardware milestone

After successful Actions/download/readback, bind a fresh single-use plan to
the exact source tree and image. Exercise GNSS configuration/start/real-fix/
stop, NFC real tag and selected-device cleanup, camera CCI plus real-frame
capture, and USB ADSP/Type-C/physical read-only I/O in one temporary RAM round.
Retain desktop/GPU/touch, both WiFi bands, Bluetooth, audio, sensors, modem,
suspend and Android-return checks; apply the existing preservation gate.

Camera source review confirms the first init register sequence fails before
mode programming on CCI error. Capture TPG remains diagnostic only. Do not
label a PHY-only hypothesis as established or promote TPG to a real frame.
USB still needs physical enumeration and I/O; role readback alone is not enough.

No phone operation, old approval reuse or partition write is authorized by
this document. Obtain the current-chat start confirmation for the final
source/image-bound plan. Never reuse r191's consumed ledger or time window.
