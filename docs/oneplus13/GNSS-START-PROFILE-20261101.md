# Explicit HIGH horizontal accuracy as the next single LOC START variable

r228 registered events as AFW/OP13, then START still returned QMI
`GeneralError` (46) and the same client's STOP was acknowledged. The engine-lock
read-only query reported status 0, legacy `lock_type=4`, subscription and
deprecated lock client null, `clients_config=0xffffffffffffffff` and
`engine_lock_state=1`. Code 46 is the generic QMI protocol error and carries no
further meaning, so the remaining LOC refusal cannot be attributed from the
reply alone.

The pinned Qualcomm IDL documents the START request TLVs
(`qmiLocStartReqMsgT_data_v02`): `0x01` session id, `0x10` fix recurrence,
`0x11` horizontal accuracy level, `0x12` intermediate report state and `0x13`
minimum interval between position reports, with `eQMI_LOC_ACCURACY_HIGH = 3`
and the note that an omitted accuracy defaults to LOW. Every round up to r228
omitted `0x11`, so the modem received a LOW-accuracy periodic request with
intermediate reports enabled.

This candidate changes exactly one variable: the same periodic session now
carries explicit `0x11 = 3`. The profile is built once in
`tools/oneplus13/location-session.c` with the stable raw message API because
Ubuntu's libqmi 1.38 exposes only the session, recurrence, intermediate-report
and interval setters and no accuracy level. The message is sent on the same
allocated LOC client through the device command path already used for event
registration, and the response is validated for service, message id, client id,
transaction id and the four-byte result TLV before any start is accepted.

`tests/test_oneplus13_location_start.py` compiles the actual builder and
validator with the installed libqmi and asserts the exact serialized TLVs
(`01 01 00 01`, `10 04 00 01 00 00 00`, `11 04 00 03 00 00 00`,
`12 04 00 01 00 00 00`, `13 04 00 e8 03 00 00`) after the QMUX header, the
accepted success acknowledgement, every protocol error code, malformed and
inconsistent result lengths, and foreign message/transaction/indication
rejection. A required negative control rebuilds the r228 profile without
`0x11` and shows the candidate differs from it only by that 7-byte TLV, so the
experiment stays attributable.

The raw builder reproduces libqmi's own error formatting, so a rejected START
still emits the identical `QMI protocol error (46): 'GeneralError'` text that
`ram-gnss-check.py` uses to classify a rejected START followed by an
acknowledged STOP as clean-but-unqualified. A dedicated case pins that text.

The helper now also prints one bounded evidence line,
`LOCATION_SESSION_START_PROFILE accuracy=high recurrence=periodic
intermediate=on min_interval_ms=1000 session=1`, and the collector records it as
`start_profile` and preserves it through long NMEA output. That line is
evidence of which profile was sent; it never qualifies a fix by itself.

Limits. This is one bounded experimental variable, not a demonstrated fix. No
engine-lock SET, client-identity scan, privacy or subscription change is
included, and `engine_lock_state=1` is still not interpreted as a client
unlock. GNSS acceptance still requires an accepted START, a checked real
satellite fix and a clean STOP on the same client. If START still fails, the
next single variables are the position-report timeout and GNSS-only reporting
TLVs, or an owner-controlled privacy/lock investigation; they must not be
combined into one unattributable round.

This source candidate needs its own exact Actions image and artifact readback
and then a fresh combined RAM plan with a new unused ledger and this chat's
explicit start authorization. r228's image, plan, ledger and approval cannot
authorize it, and no hardware result is claimed here.
