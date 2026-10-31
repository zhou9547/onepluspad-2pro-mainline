# GNSS stop ownership and evidence retention, 2026-10-31

Source review found that a SIGTERM or global timeout could initiate stop while
the collection timer was still armed. A second termination could send another
stop or exit while the first stop was pending. Stop ownership is now idempotent,
removes the collection timer, and ignores repeated termination during cleanup.
A pending start is allowed to settle before stop; both failed and lost start
replies attempt stop rather than assume that no modem-side session was created.

The native soft deadline is collection+45 seconds. A pending start and LOC stop
can each need 20 seconds. Python now reserves collection+95 seconds, including
ten seconds for timer granularity and exit. These are upper bounds, not a
claim about measured device timing. An outer combined runner must exceed this
wrapper bound and include evidence delivery, health and recovery reserves.

Long NMEA output used to truncate the start/default-selection markers from its
8192-character tail. Three bounded lifecycle lines are retained separately so
a long real stream does not become a false engine-control failure. Checked
NMEA coordinates and a successful start/stop remain mandatory for acceptance.

The original Pad project has no equivalent native LOC helper. This keeps the
existing libqmi/GLib asynchronous interfaces and optional-configuration policy.
No modem firmware or satellite/RF configuration changes. Linux host compilation
uses -Wall -Wextra -Werror; the built-in no-QRTR test covers 14 checks. Python
GNSS tests cover the real entry point, checked NMEA and long-output lifecycle.
These are offline checks. No GNSS fix or new hardware success is claimed.

Owner authorization is unattended until 2026-10-31 14:16:51 Asia/Shanghai.
NFC tag presentation, physical USB swap and orientation transitions are skipped
without acceptance. Preserve the r191 5240 MHz WiFi baseline and all existing
functions. A new exact image and fresh single-use reviewed plan are required.
