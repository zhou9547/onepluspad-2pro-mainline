# Manual RAM watchdog recovery check

The exact pinned `drivers/watchdog/gunyah_wdt.c` implements the hypervisor's
start/stop, timeout, keepalive and elapsed-time interfaces. It limits timeouts
to32s, supports magic close and stops an active watchdog in its suspend callback.
The original Pad's optional systemd profile uses30s, but is not enabled for the
phone. Presence of `/sys/class/watchdog` alone does not prove recovery.

`ram-watchdog-recovery.py` is a separate host-served, source-bound manual test.
It requires the protected RAM overlay, read-only physical storage, the exact
kernel release, active guard/deadline and uptime60..510s. It accepts exactly one
inactive Gunyah watchdog with nowayout0, verifies the character device's dev_t
and ioctl identity/capabilities, sets12s and observes countdown and keepalive.
It then holds the descriptor open without pinging for20s. If execution returns,
magic close disarms it and the report records failure. A successful reset must
be observed independently by the host together with the original Android
baseline. The armed RAM receipt alone never claims an observed reset.

Run it only at the end of a combined bounded hardware session, after other
clients are quiesced. Keep the existing absolute600s recovery deadline; never
replace normal recovery with an unverified watchdog. This test does not suspend
and does not enable any persistent watchdog policy. The driver stops it on
suspend, so successful ordinary reset still does not qualify suspend recovery.

The r57 final experiment returned `armed=false`, `countdown_verified=false`,
`keepalive_verified=false` and `disarmed_after_return=true`. No independent reset
was observed; normal host recovery returned Android with the baseline intact.
The diagnostic now preserves the failing stage, ioctl errno or bounded validation
reason and numeric readbacks. This adds evidence without relaxing countdown,
keepalive, identity, timeout or cleanup checks. A fresh combined round is required.
