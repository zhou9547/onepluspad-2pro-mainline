# Unattended RAM userspace acceptance, 2026-10-26

The owner directly authorized five hours of unattended RAM-only testing. No
flashing or partition changes were authorized. The phone returned to Android
after every completed run; seven sampled baseline properties matched. This
does not prove a byte-for-byte comparison of all persistent storage.

## Internet and system time

Run54 reached an IPv4 TCP connection but failed certificate verification.
Its saved guest clock was in September; the exact certificate cause was not
captured. Run55 corrected only the RAM guest's CLOCK_REALTIME to a bounded
host epoch. The monotonic recovery deadline was identical before and after;
no RTC operation was requested. WiFi scan, authentication, IPv4/default route,
DNS and interface-bound IPv4 HTTPS then passed, HTTP200 and verification0.

The checker retains numeric timing and certificate metrics on failure, keeps
certificate validation enabled and makes no low-level radio resets. Optional
ping/getent absence does not bypass the required HTTPS probe. This host bridge
does not solve independent RTC/NTP timekeeping for an installed distribution.

## Ordinary user GNOME session

The RAM-only desktop helper requires both the root overlay and the RAM-session
marker before configuring GDM. It preserves other GDM sections and enables
temporary autologin only on explicit invocation. The generic rootfs still
ships no default account/password or autologin policy.

Run56's initial verifier incorrectly required a specific optional logind
Desktop value. Run57 recorded an ordinary UID1000 Wayland user session with
Desktop empty, separate from the same UID's manager session. It verified the
user shell's project Mesa mapping and launched the Settings network application
with a successful application D-Bus Ping. A subsequent HTTPS stability probe
failed, so combined acceptance was not granted; that early helper did not save
the probe's numeric result. Do not invent a driver or certificate cause.

Run58 preserves independent desktop checkpoints and three bounded HTTPS
samples. The ordinary user session, the same compositor, project Mesa,
Settings process and D-Bus, GDM/Bluetooth/guard/timer health, and all three
interface-bound HTTPS probes passed. HTTP200/verification0 totals were
1.313270,0.991232,1.404604 seconds. The phone returned in144.8s; seven samples
matched, no recorded partition writes or manual recovery. GPU pixel readback,
input-device inventory and battery telemetry also passed at their stated scope.

These checks establish short software/session acceptance, not visible-screen,
physical touch, comprehensive UI, suspend/resume or long-duration stability.
Bluetooth real file reception remains owner-confirmed run51 evidence. Audio
and sensors stayed read-only in these runs.

## Audio correction and test hold

A new offline review checks effective status through every ancestor in the
saved stock runtime FDT. Both AWINIC smart-amplifier nodes are enabled; the WSA
macro at6b00000 is disabled and every WSA884x/WSA883x speaker node is disabled
directly or through its ancestor. The run42 candidate instead enabled a WSA884x
speaker pair and WSA playback link. Merely finding template nodes in stock was
insufficient evidence to activate that route.

Run47 PCM open/HW_PARAMS/PREPARE success on that candidate does not establish
progress on the stock speaker path. Do not repeat WSA streaming or equate six
missing WSA mixer controls with the phone speaker fix. Hardware reuse of that
boot-image hash is held. Correct hardware mapping, an isolated AW88461 driver,
matched protection/tuning and a mute/gain policy remain separate gates.

## Offline checks and build scope

Twenty automatic-WiFi tests, four mocked clock tests and six RAM desktop
policy/session/probe tests pass on Linux. The helper rejects greeters, wrong
users, non-Wayland or inactive sessions and non-RAM configuration attempts.
Its HTTPS probe records failures separately from desktop success. The rootfs
workflow runs these tests on ARM64 before verifying the actual desktop runtime.
Build success is OFFLINE_BUILD_ONLY and is not an additional hardware result.
