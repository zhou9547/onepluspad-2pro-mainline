# Read-only engine-lock diagnosis

r211 AFW registration succeeds, START returns QMI GeneralError (46), and STOP
is acknowledged. Read-only qmicli queries report engine lock=all and
operation mode=standalone. The lock is a concrete candidate explanation,
not proof of causality. Standalone mode does not establish the engine is enabled.

Primary Qualcomm LOC declarations describe ALL as locking all position sessions
and describe the setting at subscription scope, with dedicated-data subscription
as the default. This is not a per-client lease. Persistence and privacy effects
of SET are not established, so there is no lock setter or automatic unlock in
the native candidate. An obsolete Python fallback that issued an implicit
unlock through multiple qmicli processes is removed. Missing/non-executable
native helper now fails before any command; the same-client native path remains.

The native helper adds --get-engine-lock: one empty GET 0x003b request on its
allocated LOC client, default dedicated-data subscription. It does not run the
NMEA setup, registration, START or STOP sequence. A 35-second process deadline
covers discovery, opening, allocation, response and indication; external runners
must reserve process termination/transport and recovery time separately.

Successful diagnostic output requires both an exact successful response and
one matching indication on the same client. The response validates service,
message, transaction, CID and exactly one four-byte success TLV. The indication
validates LOC/0x003b/CID and mandatory success status, rejects duplicate or
wrong-width known fields, leaves absent optional fields null and ignores unknown
TLVs without exposing their bytes. A failed/malformed indication cannot qualify.

LOCATION_ENGINE_LOCK_RESULT JSON fields follow Qualcomm IDL:

| TLV | JSON field | Width |
|---|---|---|
| 0x01 | status | 4, mandatory success=0 |
| 0x10 | lock_type | 4 |
| 0x11 | subscription | 4 |
| 0x12 | lock_client | 8, fixed-width hex string |
| 0x13 | clients_config | 8, fixed-width hex string |
| 0x14 | engine_lock_state | 4 |

The 64-bit masks use strings to preserve every bit in JavaScript consumers.
Engine-lock state 1 means enabled; 2 means disabled for mobile-initiated sessions.
Unknown optional fields are not inferred from lock_type.

Primary source: qualcomm-linux/location-apis-qcom, branch location.lnx.0.0,
loc_api/loc_api_v02/location_service_v02.c, GET_ENGINE_LOCK IDL lines 3439–3475.
The reviewed source SHA256 is
b66db26326a17b15ec94750aa3ac6eea7ad2ed00e07c24e37e87eb0237aa3f47.
The associated header supplies semantic descriptions. libqmi's public raw-TLV
and QmiDevice indication APIs retain the packaged runtime ABI. No new private
device identifiers or position records are included.

This diagnostic is source/offline qualified only until a fresh combined hardware
round observes its output. A read-only result is not a GNSS start/fix acceptance.
