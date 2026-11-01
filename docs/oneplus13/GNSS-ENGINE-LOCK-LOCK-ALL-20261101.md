# r230: HIGH accuracy excluded, legacy LOCK_ALL is the standing candidate

The r230 combined RAM round booted the exact 96928a96 image once, completed all
13 planned phases in 202.44 s of guest uptime, returned Android with the seven
baseline properties matching, reported zero partition writes and left no
firmware UNKNOWN. USB AP17/18 armed to 1/1 and restored to the saved zeros in
24->64->18->17 order with state 2/used 1; the owned exfat/ntfs3 modules were
removed. No physical dock or U-disk swap happened in this round, so nothing is
claimed beyond that clean preparation and cleanup.

GNSS is the decisive result. The helper sent the new profile and the receipt
records it verbatim:

`start_profile = accuracy=high recurrence=periodic intermediate=on min_interval_ms=1000 session=1`

START still returned `QMI protocol error (46): 'GeneralError'`, the same client's
STOP was acknowledged, no NMEA or fix arrived, and the LOC endpoint was the same
`node=0 port=94 version=2 instance=0`. Explicit HIGH horizontal accuracy is
therefore excluded as the cause; the r228 failure is unchanged.

The read-only engine-lock query in the same boot is unchanged: status 0,
`lock_type=4`, subscription and deprecated lock client null,
`clients_config=0xffffffffffffffff`, `engine_lock_state=1`, operation mode
`standalone`. The pinned IDL resolves the missing semantics:

- `eQMI_LOC_LOCK_NONE_V02 = 1` - do not lock any position sessions
- `eQMI_LOC_LOCK_MI_V02 = 2` - lock AFW position sessions
- `eQMI_LOC_LOCK_MT_V02 = 3` - lock non-AFW/NFW position sessions
- `eQMI_LOC_LOCK_ALL_V02 = 4` - lock all position sessions

So `lock_type=4` is the legacy LOCK_ALL state, not "AFW is locked", and the
all-ones client mask is consistent with it. A LOCK_ALL modem refuses position
sessions while still accepting event registration and STOP, which is exactly the
observed shape: registration passes, START fails generically, STOP succeeds.
`engine_lock_state=1` in the newer IDL is the engine ENABLED bit and does not
contradict a legacy lock.

This is a candidate interpretation, not a proven root cause, and it does not by
itself justify a mutation. The next step is read-only and owner-visible: check
whether the phone's own location/privacy setting and the modem NV lock agree,
and confirm which component owns the persisted lock. Any experimental
`SET_ENGINE_LOCK` would need its own bounded plan that saves the current lock,
sets one value, starts once, restores the saved lock and proves the restore by
readback. That mutation is outside this chat's USB-supply authorization and must
not be folded into an unrelated round.

Camera repeated the single-primary attempt and failed with proven teardown; the
chip-ID and modem gates stayed green. 5 GHz and certificate-verified HTTPS
passed after the round. NFC remains owner-skipped.

See R230-GNSS-START-HARDWARE-RESULT-20261101.json for the sanitized result.
