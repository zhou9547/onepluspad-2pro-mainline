# r263 update: exact full image accepted

Actions41355509240/source d16f1ae7 now passes the complete unattended first-user,
ordinary desktop, GPU/app and Wi-Fi software path. The timezone vendor profile,
small-screen mode and OSK defaults are in the built image. Its optional language
download finishes naturally when the observer waits for it. No functional RAM
patches were applied. Normal users in the delivered image remain zero.
See FULL-UBUNTU-R263-ACCEPTANCE-20261102.md for exact hashes, recovery and remaining
physical USB/touch/Chinese-IME boundaries. The following is the retained history.

# Full Ubuntu first-user desktop, 2026-11-02

## Follow-up on the exact full image

Actions41335006902/source3f6f72af built all five jobs successfully. Independent
readback verifies1662 installed packages, real ARM64 apps, and zero normal users.
r256–r259 prove that packaged hardware bootstrap works without a host-injected
bringup script. r259 also preserves GDM across the test deadline adjustment,
passes5220MHz/HTTP/HTTPS and touch-driven name/password entry. Full onboarding
is not yet accepted: its timezone city search returned no suggestion for the
typed test query, leaving the touch Next button insensitive.

The phone already configures Asia/Shanghai. The vendor profile now uses GNOME's
supported `skip=timezone` option so this redundant search cannot block first-user
creation. Language, input, account, password and the other setup pages remain;
timezone can be changed later in Settings. A new full image and pristine-image
phone test are required for this change.

Observer pitfalls: the final source-image assembler changes the base900-second
timer to300seconds. Read the actual delivered timer. After bootstrap, restarting
that timer propagates through Requires to the firstboot oneshot and GDM; the
attempt guard correctly refuses a second hardware initialization. Retiming the
RAM test uses only daemon-reload, with timer readback and unchanged dependent
service start timestamps. An isolated real systemd experiment verifies this
method; r259 verifies it on the phone. Earlier observer failures remain failures.

The production rootfs contains the full `ubuntu-desktop` dependency set and no
regular user, password or autologin. GDM owns first-user creation. Phone testing
remains temporary RAM boot only; no persistent installer or dual-boot layout has
been approved.

## Hardware and input bootstrap

The full desktop originally reached GDM without executing the native display,
touch, WLAN and SSC prerequisites used by the older RAM test runner. r249's black
screen was not successful desktop acceptance. `qualified-bringup --firstboot`
now executes the qualified hardware path before GDM and exits before the legacy
RAM test-account branch. The full desktop's distro SensorProxy is masked because
it competes for the phone SSC backend's D-Bus name.

The mobile schema enables the screen keyboard and accessibility bridge. Global
`GTK_IM_MODULE`, `QT_IM_MODULE` and `XMODIFIERS` overrides are removed so GTK can
use the native Wayland text-input path. r251's configuration readbacks were not
keyboard success: the owner still could not summon it.

## r253 evidence and limits

One fresh RAM boot used local source `cd64cf8`, the full image from Actions
41315126988 (source `7ad67e2f621d10dc6174443a488d4156ea16e57f`) and exact
hash-bound RAM payloads. Boot SHA256 was
`7c908bce96ed715e5dc500e31c3a9b5db06dbffa1c62cc603aca640d2a6e6a5b`;
rootfs SHA256 was
`0409669f86951f3479f474d7ac4c3032a4f2529487810cdfabde00f2f833d6a1`.
The single-use plan SHA256 was
`f09dae35a25ef906161f1c4ac400e527069fcbb00720c84b7a3ce1af513da224`.

The owner authorized an unattended, disposable RAM account. A temporary virtual
touchscreen used the kernel's existing uinput ABI to exercise
libinput → Mutter → GTK → screen keyboard. No module was loaded for this fixture.
Every fixture was destroyed and its removal checked. This is synthetic input
validation on the real phone, not a new physical touchscreen or USB test.

Touching a text field opened the keyboard inside the display. Touching its keys
entered the test name and two 24-character random password fields. The password
was generated and retained only in a root-readable RAM file, never in arguments,
logs or the image. Initial Setup created the account and transitioned to an
active local Wayland user session with project Mesa mapped. Settings, Nautilus
and LibreOffice executable entry points existed; app launch/render acceptance
remains a separate check.

Initial 5GHz association at 5220MHz, IPv4, interface-bound LAN HTTP and
certificate-verified HTTPS passed. The post-login fresh scan did not advance
NetworkManager LastScan within the old 16-second wait while the device still
reported connected. That stage failed; it does not prove either a healthy
post-login data path or a broken RF link. The whole round is not a combined pass.

The exit path verified all four actual saved firmware values, PC device/sink and
configured UDC. Android returned with seven baseline properties equal, one boot
and zero reported partition writes. No physical dock was attached overnight.
The older r246 exact-image-plus-overlay USB matrix remains the physical evidence;
it must not be relabeled as full-image acceptance. r250/r251's missing firmware
close receipts remain UNKNOWN.

## Next packaged candidate

GNOME's height-only small-screen detection misses a tall, narrow phone. r253's
Pro and timezone pages exceeded 480 logical pixels. Scoped user-service drop-ins
enable GNOME's existing `GIS_SMALL_SCREEN` mode for maximized, scrollable Initial
Setup, including first-login/upgrade welcome. No page is silently removed.

The full metapackage installed a Firefox wrapper that exits without its Snap.
Explicit `epiphany-browser` and `gnome-software` packages supply a real browser
and software manager before Snap seeding. Browser MIME defaults and dock entries
point to installed applications. Package and actual ARM64 binary verification
are required; fresh image launch/render tests remain necessary.

WiFi preservation has an explicit existing-link mode: verify active profile,
configured and actual SSID, actual frequency, IPv4 and interface-bound traffic
without rescanning or reactivating. Fresh scan tests retain one request and a
finite completion budget, with 45 seconds for an associated device. These are
distinct results; an existing-link pass never substitutes for a fresh scan pass.
Kernel/RF/regulatory configuration is unchanged.

Complete-image manifests bind firstboot scripts, schema, compiled defaults,
GDM ordering, small-screen drop-ins and MIME defaults, and verify the distro
SensorProxy mask. A new artifact must pass readback and its own fresh boot;
successful RAM overlays do not qualify new packaged bytes.

Offline verification: 839 `test_oneplus13*.py` tests pass, one skip. Linux strict
schema compilation against the actual full image's schemas reads back enabled
keyboard/accessibility/fixed dock and the Epiphany favorites, including the
Ubuntu desktop override. These checks do not qualify new GUI rendering.

Sources: [GNOME Initial Setup vendor configuration](https://sources.debian.org/src/gnome-initial-setup/48.1-1/README.md/),
[GNOME small-screen implementation](https://github.com/GNOME/gnome-initial-setup/blob/master/gnome-initial-setup/gis-driver.c),
[Linux uinput ABI](https://docs.kernel.org/input/uinput.html),
[Ubuntu Initial Setup test plan](https://ubuntu.com/project/docs/maintainers/test-plans/desktop-team/GnomeInitialSetup/).
