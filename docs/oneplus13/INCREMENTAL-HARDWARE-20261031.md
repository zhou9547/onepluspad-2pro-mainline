# Incremental combined RAM tests, 2026-10-31

Image source: 95b931d72f2cc2026c844080896b10cb7c8e8df7.
Successful Actions run: 41178635052 (kernel, rootfs, Mesa, SSC, assembly).
Targets boot SHA256: ae247850900bc9dfd0bab2fba4a21d4634540dd0303bb717f709fee95a1cc5d4.
Rootfs SHA256: 188ffcc6b624c30bf64d00f9b9719e60d0b78a6217c9087cb8891f7c437766ee.
This file contains sanitized conclusions; private device/network/tag identities
and raw logs are deliberately excluded.

| Boundary | Direct observation | Remaining acceptance |
| --- | --- | --- |
| Camera | Expected S5KJN5 ID 0x38e5, driver bound, runtime suspended; temporary target removed and owned modules unloaded | Real sensor frames |
| WiFi | Existing 5 GHz automatic preservation gate passes | No new RF adaptation claimed |
| MPSS | Running, IPCRTR present, firmware verified; not restarted | GNSS fix/session |
| GNSS | NMEA defaults supported; register-events reports InvalidArgument before start is submitted | Successful start, satellite fix and stop |
| NFC | Driver bind, powered controller, polling, stop and power-down confirmed | Real tag discovery |
| USB | Requested host readback; no external peripheral; device role restored | Stable Type-C/host enumeration and read-only external I/O |
| Recovery | Android returned, all seven baseline properties match, zero partition writes | Preserve per-round exact plan and unused ledger |

r204 ran the GNSS, NFC and physical USB stages in one temporary boot, about
325 seconds to the final receipt. GNSS pre-start failure and NFC no-tag result
did not prevent the following stages. Its USB-return card expired before the
owner reply was consumed; therefore the final planned phase/evidence acceptance
is false. Individual observations are retained without promoting partial
evidence to full-round or full-adaptation success.

## Source changes after these observations

GNSS uses the libqmi LOC Register Events protocol (message 0x0021, uint64 mask
TLV 0x01). A rejected NMEA subscription gets one retry with the standard
POSITION_REPORT bit on the same client. Other protocol/transport errors fail.
A position qualifies only with LOC success, the SATELLITE technology bit and
finite coordinates inside latitude/longitude bounds. Intermediate or network
positions do not qualify. NMEA and normal start/stop remain supported. An
explicit marker proves that no LOC start was requested, allowing cleanup to be
classified as unnecessary without pretending the engine or fix passed.

USB follows the pinned upstream DWC3/UCSI ownership model: UCSI partner changes
call usb_role_switch_set_role and can replace an earlier debugfs host request.
The bounded external-device wait now records role/Type-C transitions and may
reassert DWC3 host only after an attached port reports both host and source.
It never requests a Type-C power swap or writes a storage partition. Physical
enumeration/read acceptance remains false until new direct evidence proves it.

Protocol/API references are the pinned local libqmi 1.38.0 sources
(qmi-service-loc.json and qmicli-loc.c), and kernel commit
7a81d184e3098624d4342d8f4eff5e23674bcc9f drivers/usb/dwc3/{core,drd}.c and
drivers/usb/typec/ucsi/ucsi.c. This reuses existing upstream interfaces and does
not substitute another board's firmware, calibration or sensor registers.

Offline checks: native cc -O2 -Wall -Wextra -Werror, 19 native configuration
assertions without QRTR, 16 GNSS Python tests, 14 USB Python tests. New hardware
success and new Actions completion must be recorded separately when observed.
