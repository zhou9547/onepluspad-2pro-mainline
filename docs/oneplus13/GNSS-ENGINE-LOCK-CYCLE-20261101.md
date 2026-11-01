# Bounded, reversible LOC engine-lock experiment

r230 excluded horizontal accuracy: the modem received an explicit HIGH-accuracy
periodic START profile and still answered `QMI protocol error (46):
'GeneralError'`, while the same client's STOP was acknowledged and event
registration had already succeeded. The read-only engine-lock reading in that
boot was `lockType=4`, `clientsConfig=0xffffffffffffffff`,
`engineLockState=1`. The pinned IDL resolves `lockType=4` as
`eQMI_LOC_LOCK_ALL`, which refuses position sessions and leaves registration and
STOP working. That is the standing candidate, not a proven cause: who owns the
persisted lock, and whether it agrees with the phone's own location setting, is
still unestablished.

This candidate adds one opt-in experiment. With `--unlock-engine-lock` the
helper reads `GET_ENGINE_LOCK` (0x003b), saves `lockType`, and — only if it is
not already NONE — sends exactly one `SET_ENGINE_LOCK` (0x003a) with the
mandatory `lockType` TLV set to `eQMI_LOC_LOCK_NONE` (1). It then confirms the
new state with a second readback before running the normal NMEA session, and
finally restores the saved `lockType` and confirms that restore with a third
readback. `subType`, `lockClient` and `clientsConfig` are deliberately not sent:
the IDL states that `lockClient` overwrites `lockType`, so restoring `lockType`
is the faithful minimal inverse. The exact request bytes are pinned by tests
(`01 04 00 01 00 00 00` and `01 04 00 04 00 00 00`).

Failure handling is explicit rather than optimistic. A successful SET marks the
lock as mutated before its confirmation query, so any later error still attempts
the restore. If the restore is not confirmed by readback, the helper prints
`LOCATION_ENGINE_LOCK_UNRESTORED` and exits non-zero; the collector then reports
`lock_restore_proven=false` and `cleanup_complete=false`, so a round can never be
presented as clean with a changed lock. The soft deadline reserves the SET and
both readbacks (seconds + 90) and routes through the same stop/restore path.

Evidence lines are bounded and machine readable: `LOCATION_ENGINE_LOCK_SAVED`,
`LOCATION_ENGINE_UNLOCK already=none`, `LOCATION_ENGINE_UNLOCK_CONFIRMED`,
`LOCATION_ENGINE_LOCK_RESTORED`, plus the error markers above. The collector
keeps them through long NMEA output and records `lock_saved`, `lock_restored`,
`lock_restore_required` and `lock_restore_proven`.

Limits. This is a modem-state mutation and is authorized only by an explicit
owner decision; it is not part of the USB-supply authorization. It does not read
or change the Android privacy provider, does not scan client identities and does
not clear the client mask. It is not a demonstrated GNSS fix: acceptance still
requires an accepted START, a checked real satellite fix and a clean STOP, and
the lock must be restored afterwards. The source candidate needs its own exact
Actions image and a fresh reviewed plan before any hardware use.
