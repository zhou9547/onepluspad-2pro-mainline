# Incremental combined RAM tests, 2026-10-31

## r205 complete combined round

The exact source f67c02498fd6083f61821ed78818ad41ee71cf92 passed all five jobs
in Actions 41182218697. Three downloaded archives matched GitHub digests;
independent image readback verified 37 image files, 46 kernel files, 66 runtime
files, 120 qualified firmware files and 18 native ELF dependencies.
Targets boot SHA256: 8600fe252845ef624693c60ebb21a3e08837e5029f03246888eb90fb7a8ade87.
Rootfs SHA256: b1886d4c8e81c2b8c3cc62b27ff4c3cfdcbcffbde85bfce2944930937be81d37.

One fresh temporary RAM boot completed every planned phase, delivered its
private command evidence, cleaned up and returned to Android with all seven
baseline properties matching. No partition writes occurred. The final guest
receipt arrived at about 290 seconds uptime. Camera chip ID, existing 5 GHz
WiFi and MPSS verification passed. These are preservation and sensor-access
boundaries, not real camera-frame acceptance.

Both NMEA and POSITION_REPORT LOC registration returned InvalidArgument;
the explicit NO_SESSION marker confirms no start request was submitted.
GNSS failed cleanly and the following USB stage still ran. NFC was explicitly
skipped at the owner's request because no physical tag was available; the
previous test item was another Android phone emulating a transit card.
This is not evidence of a failed NFC controller.

USB had a host-mode register readback, but its end-of-wait inventory had no
xHCI instance or root hub. After cable removal, Type-C reported no partner
and remained device/sink. Device-role restoration passed. External USB I/O
and GNSS remain unqualified; full and incremental target acceptance are false.

The next diagnostic candidate records xHCI driver binding and root-hub
ancestry under this phone's a600000.usb controller, initial/transition/final
inventories and bounded private USB kernel diagnostics. GCTL host readback
alone cannot permit cable removal. LOC records all discovered service
node/port/version/instance and the selection snapshot, while preserving the
existing selection and strict fix/start/stop acceptance. Snapshot selection is
not a claim about the later actual socket destination. This candidate needs
its own image build and fresh review before any new hardware round.

## Earlier r203/r204 observations

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
