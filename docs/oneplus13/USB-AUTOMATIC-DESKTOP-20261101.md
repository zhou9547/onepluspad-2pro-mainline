# Automatic desktop OTG candidate

The owner requests ordinary desktop plug-and-use OTG before preparing the full
Ubuntu desktop and dual boot. The r234 combined round already qualifies one
physical dock and attached NTFS U disk for 4096-byte readonly block and file I/O,
unmount and exact USB saved-value cleanup. Automatic desktop behavior is **not
yet hardware qualified**. That round halted after GNSS lock restoration was
unproven; later camera and 5GHz post-check did not run. Android return is not
proof of GNSS lock restoration.

## Reference and phone scope

The reference supply implementation is
[yzddmr6/linux-sm8750-erhai d9383c7](https://github.com/yzddmr6/linux-sm8750-erhai/commit/d9383c7269f626e3fa752d2396fd0d1716103826).
Its model prepares AP17/SW18, follows firmware0x50/0x51 notifications, sets
current64 before VBUS24 and leaves the data role with UCSI. This candidate keeps
the existing phone kernel pin and phone-derived1250mA current target; it imports
no Pad calibration or partition layout.

## Separate automatic ownership

The old single-use120s manual API is preserved. A separate immutable boot flag,
`qcom_battmgr.oneplus13_otg_auto=1`, exposes the root-only automatic endpoint.
Probe rejects simultaneous manual/automatic owners. The transport still
serializes optional traffic and permanently poisons this instance after an
ambiguous send, timeout, firmware error or service loss. Rebinding cannot evade
the boot-wide ownership latch.

An automatic session captures actual baselines through the checked supply
implementation. A new cycle is possible only from idle or a proven full restore
with no dirty values and healthy transport. Firmware notifications must be exactly
owner32778/type2/opcode7/16bytes and full-width0x50/0x51;0x150 is not accepted.
The source request has a local generation. A delayed userspace activation for an
older generation, or one with a pending detach, is rejected before supply writes.

The desktop service observes the real attached Type-C host/source and this exact
DWC3's running xHCI/root hubs twice before requesting activation. It never writes
debugfs or changes a Type-C power/data role. UCSI owns the role. The kernel checks
the event generation around current64/VBUS24 operations and restores on detach.
It does not infer physical connection from a chat button or a software role write.

The separate automatic watchdog is15s. Userspace renews every3s only before the
old deadline expires. A queued old watchdog rechecks the current deadline under
the mutex; it cannot restore a renewed session accidentally. Failed heartbeats
cannot extend an expired session. A stopped/killed service closes ownership, and
the kernel watchdog covers loss of userspace. Restore remains24->64->18->17 with
actual saved values. Transport ambiguity can still leave UNKNOWN; no restart or
unproven readback turns it into success.

## Desktop packaging and acceptance

The systemd unit is installed and enabled conditionally on the automatic flag.
No default account/password is added. The delivered helper, unit and udev rule
are hashed and read back from the actual SquashFS. UDisks/GVFS support is included.
In RAM qualification only real external USB blocks are exposed to the desktop
volume monitor; the existing block-level readonly rule remains in force. The
service opens no media files and changes no host storage policy.

An additional automatic-USB RAM desktop boot is built alongside the unchanged
manual alternative. Its exact cmdline, DTB, kernel/initramfs, conditional service
link and source runtime are verified. Unqualified parent images cannot acquire
the automatic flag. A full system and dual-boot installation remain deferred.

Acceptance requires actual ordinary-desktop operation without manual role/power
commands, real storage nodes and readonly I/O, repeated unplug/reinsert, active
operation beyond120s, process-death cleanup and PC device/sink+UDC return. Charger
or PC sink mode must never enable VBUS. Camera and5GHz preservation follow in the
same boot, with readonly GNSS diagnosis only until r234's lock issue is resolved.
Every phone boot still needs exact current-chat source/image/plan binding and a
fresh unused ledger. No partition writes or persistent installation are included.
