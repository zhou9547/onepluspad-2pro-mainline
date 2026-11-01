# Reject an expired USB arm before renewing the active lease

The r223 supply sysfs `start` branch checked ARMED, then replaced the saved
deadline before the policy's expiry check. If the restore worker had not run
at the 120-second boundary, a late start could renew an expired arm.

The branch now checks `op13_otg_supply_expired()` while holding the same
battery mutex, before changing the deadline or rescheduling work. An expired
or stopping arm returns an error without GET, SET or timer renewal. The queued
worker and explicit `restore` retain their existing cleanup paths. The active
lease remains 120 seconds; this does not widen any current, VBUS or role policy.

`test_oneplus13_otg_supply_deadline.py` compiles the actual added sysfs-store
and expiry functions from patch 0024. Release and ASan/UBSan cases cover a
valid start, the exact expiry boundary, a delayed worker, teardown, and explicit
restore after expiry. Removing the guard reproduces late reactivation in a
required negative control. These are mocked kernel-interface checks, not
electrical or scheduling qualification.

A new exact Actions image and fresh independently reviewed combined plan are
required before hardware testing. r223 remains the last hardware-tested image;
its plan, ledger and approval cannot authorize this change. The host must
verify WiFi control, arm, then request the actual PC-cable to OTG/U-disk swap.
The operator window must fit within the unchanged arm deadline. USB acceptance
still requires real host/source, exact xHCI ancestry, external enumeration,
read-only block/file I/O and saved-value restore. GNSS, real camera frames and
post-USB 5GHz/HTTPS preservation share the same boot after proven cleanup.
NFC remains owner-skipped.

The same independent review found that the shared optional transport tested
only the send/wait result before latching poison. A matching firmware error
ACK was copied into the return value afterwards, leaving the transport healthy
and allowing a rollback SET. The transfer now consumes that callback error
before the poison decision. Any such failure forbids subsequent optional
traffic, including restore, and the lease remains UNKNOWN. The actual-kernel
scaffold verifies a failed SET ACK followed by manual/watchdog cleanup emits
no additional request. Restoring the former ordering fails a negative control.
No new command or firmware property is introduced.
