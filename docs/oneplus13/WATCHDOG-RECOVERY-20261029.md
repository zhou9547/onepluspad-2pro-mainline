# Manual RAM watchdog recovery check

r59 on the exact da0f54cb Actions40820121568 image records raw STATUS elapsed
0 immediately after keepalive and44 after2.0004s, with GETTIMELEFT12 both times.
Enabled changes0 to1 on open; bit31 is already1 immediately after open. These
are direct values, not a confirmed interpretation of firmware time/flags.
The watchdog was disarmed and ordinary host recovery returned Android with
matching baselines. Independent reset remains unqualified.

The mutually exclusive `--diagnose-clock` mode uses the same root/RAM/kernel/
storage/device/guard checks, requires the STATUS diagnostic before open,
retains32s timeout, and pins only its own process to the lowest allowed CPU.
It samples idle2s, busy2s and idle2s without keepalives between samples, then
records a final keepalive response on that CPU and magic-close disarms. Wall
time and process CPU time accompany the samples; original affinity is restored
even on a sampling failure. No CPU is offlined and no cpuidle/PM configuration
is modified. No units or pass/fail reset criterion are inferred from this
comparison. The original `--arm-one-reset`12s countdown/keepalive/expiry gates
are unchanged. Both modes must be invoked explicitly at the end of a combined
session; neither enables a default watchdog policy.

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

r58 identified the failure at countdown: both timeout readbacks were12,
support options were0x8180, but timeleft remained12 after2s. Cleanup returned
the watchdog to inactive. The new kernel patch exposes root-only
`/sys/devices/platform/gunyah-wdt/hypervisor_status`; it performs only the
existing STATUS SMC and returns result, enabled, expired and elapsed_raw.
It neither pings nor changes timeout/control/PM behavior. The helper records
monotonic samples before open and around existing pings/timeleft reads.
`--require-hypervisor-status` refuses a missing diagnostic before opening the
device. The raw value is evidence, not a second software countdown or a guessed
ABI conversion. The original countdown/keepalive/reset checks remain required.

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
