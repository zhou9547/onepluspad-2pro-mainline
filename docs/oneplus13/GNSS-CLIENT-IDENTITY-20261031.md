# LOC registration client identity

r207b discovers LOC v2 on the existing selected node but both NMEA and
POSITION_REPORT registration return InvalidArgument before start. Changing
the QRTR node or issuing start after a failed registration would not resolve
that evidence.

Upstream libqmi commit 532de37e84dac82936b056e28fb71ce4c7af60d6 adds the
missing Register Events client identification inputs. Its motivating report
is SM7635/milos gnss8: newer engines reject registration without the AFW
identity supplied by the system location provider. This is a relevant
protocol correction, not proof of behavior on this SM8750 phone. The primary
Qualcomm location_service_v02.h documents AFW=1, NFW=2 and PRIVILEGED=3;
NFW additionally requires a client string and explicit positioning request
notification policy.

The native Linux system location provider now sends fixed AFW=1 and its
own four-byte OP13 identifier. It does not impersonate the Android MHAL
string, select privileged mode or scan different client types. This makes
its provider role explicit. The existing NMEA mask and one bounded
POSITION_REPORT fallback are preserved on the same client and endpoint.
Start remains forbidden unless registration succeeds. The existing bounded
start/stop cleanup and strict satellite fix acceptance are unchanged.

Ubuntu's packaged libqmi predates the new generated setters. The stable
QmiMessage API builds message 0x0021 with TLV 0x01 (LE64 mask), 0x10
(four ASCII bytes, no NUL or internal length), and 0x11 (LE32 AFW=1).
Transactions use the same allocated client's CID and next transaction ID.
Response handling requires a LOC registration response and exact four-byte
result TLV. Malformed and unsuccessful responses do not permit start.
No library ABI replacement, modem restart or persistent setting is added.

Reference sources:

- libqmi data/qmi-service-loc.json and src/libqmi-glib/qmi-enums-loc.h at
  532de37e84dac82936b056e28fb71ce4c7af60d6.
- qualcomm-linux/location-apis-qcom, location.lnx.0.0,
  loc_api/loc_api_v02/location_service_v02.h, qmiLocRegEventsReqMsgT_v02.

Native -Wall -Wextra -Werror compilation and configuration self-test pass
with libqmi 1.38.0. Actual-message tests verify request bytes and response
rejection without opening QRTR. Fresh Actions/readback and a combined RAM
round are still required before claiming registration/start/fix success.
