# Offline diagnostic candidate: wake, stereo and GPU monitoring

The owner requests code review and compilation only, with no phone available.
This branch is **not hardware qualified**. Do not boot, query or modify a phone.
Preserve the accepted r272 full image and fixed milestone tag. New artifacts
must retain `hardware_tested=false` until a later separately authorized round.

## Reference revisions and compatible backports

Reviewed the original integration repository at
[`9762c0994e2b5acd672be2ddbda680fd61f1cad6`](https://github.com/yzddmr6/onepluspad-2pro-mainline/commit/9762c0994e2b5acd672be2ddbda680fd61f1cad6),
which pins kernel v0.6 at `70b572544d504735e2924f6c3f5fe3bd726ef275`.
The kernel repository's default branch still points to v0.2, so checking only
its default HEAD misses the newer integration pin. The phone keeps its exact
7a81d184 kernel base and phone-specific patch stack rather than replacing it
with a tablet tree/configuration. Four generic GMU fixes are backported:
stale RPMh shutdown votes, dependency votes from the GPU OPP device, removal
of the boot bus vote when GMU bandwidth takes over, and masking HFI before
GMU boot. Exact source commits and hashes are recorded in
`devices/oneplus13/kernel-patches/UPSTREAM-GMU-20261103.json`.

These are relevant to the observed GMU timeouts but are not a proven sole
cause or a new phone wake qualification. Existing DPU/SPR admission, exact
panel packets/calibration, USB supply/restore policy and RF configuration remain.

## Lock and visible wake candidate

Follow the original project's compatibility display-power design. The phone
panel previously exposed only its fixed startup brightness. It now exposes a
binary backlight:0 sends DBV0,1 sends the already used normal DBV1433. It adds
no lower-brightness range, HBM, AOD, new calibration or higher brightness.
Callbacks use the panel mutex, reject invalid levels and avoid DSI writes when
the panel/rails are not active.

Phone-scoped GNOME Settings Daemon interposition converts display blanking
to a credential-checked local backlight service. It keeps KMS/SPR running;
this is **compatibility blanking**, not repaired native DPMS or deep suspend.
The power-key service grabs only the PMIC key, confirms GNOME lock before
blanking, and restores visibility using a modifier-only wake event without
deactivating ScreenSaver or bypassing greeter authentication. Invalid/failed
lock requests do not blank. A brightness0 setting is restored to binary1 on
wake. Services require the RAM marker and desktop command line; foreign panel
names/compatibles and nonbinary brightness devices are rejected.

Unlike the latest tablet default, phone automatic system suspend remains
disabled: its RAM return timers and peripherals are not qualified over suspend.
Idle blanking returns to300seconds with dimming disabled for the binary
control. Physical lock/unlock, key wake, greeter, repeated cycles and error
logs remain mandatory future tests.

## Reverse-landscape stereo

A PipeWire filter sits before the existing qualified native speaker PCM.
Its four mixer coefficients are only0/1 permutations, with no amp controls or
additional gain. Read the **actual internal DSI logical monitor transform from
Mutter**, not raw accelerometer orientation; external primary monitors do not
choose the phone mapping. Transform1 retains the owner-confirmed route;
transform3 swaps channels. Portrait retains the old route. On transient
monitor/session loss retain the last valid matrix, and rebind after PipeWire
object replacement. This mapping assumption still needs owner audition.

Native streams are muted while moved behind the new filter; only streams
targeting the phone sink move. Default volume stays50% on the filter with
native software unity and the existing1023 hardware ceiling. Bluetooth/other
sinks are not moved. Filter stop restores the native50% software cap; ordinary
audio shutdown still stops the graph and proves actual amplifiers off.

## Actual Resources monitoring, not invented GPU activity

Import the same author's generic
[Resources MSM telemetry work](https://github.com/yzddmr6/xiaomipad-8pro-mainline/tree/main/apps/resources)
and its pinned Ubuntu source context backport. This is userspace telemetry;
no Xiaomi firmware/calibration or power configuration is imported. Original
GPL-3.0-or-later patches, authors and COPYING are retained under
`packaging/oneplus13-resources`.

The patched application resolves platform DRM/render nodes to their actual
card instead of requiring PCI or attributing unknown clients to card0. It
reads MSM fdinfo engine/memory counters and Adreno device-tree identity,
devfreq and gpuss thermal data. Missing live frequency remains unavailable,
not a substituted maximum or fabricated load. The source package is built
natively for ARM64 with Debian's vendored Meson/Cargo build/test rules;
corresponding patched source accompanies the deb artifact. Phone GPU counters
and permissions must still be checked against actual renderer work later.

## Lightweight image and later acceptance

Actions now accepts `desktop_profile=diagnostic` or `full`; the diagnostic
profile omits the full desktop metapackage, recommended office/browser/Software
suite and Docker while keeping GNOME/first-user OSK, Settings, Files, Terminal,
Text Editor, GNOME System Monitor, patched Resources, Wi-Fi, USB and audio
dependencies. Resource tools are pinned to the newly built same-commit artifact.
The full profile remains selectable. No regular user is precreated and no
password, Wi-Fi secret or local owner file enters the build.

Compilation, static image readback, fault tests and isolated PipeWire PCM
proof cannot establish real panel, acoustic orientation, GPU telemetry or
peripheral recovery on the phone. Future hardware acceptance must bind the
new exact boot/rootfs/source and a fresh ledger, preserve Android and retain
USB/5GHz regressions. Camera/GNSS stay paused, NFC skipped; no permanent install.
