# OnePlus 13 full Ubuntu r286 acceptance, 2026-11-06

The current development branch, descended from the r272 full Ubuntu milestone,
was built as `desktop_profile=full`. Actions 42042903083 passes all six jobs.
The four artifacts match their GitHub digests, and independent actual-image
readback passes the boot/FDT/cmdline/kernel/initramfs/rootfs bindings,
41 complete-image checks, 46 kernel checks, the 1662-package SquashFS,
ARM64 applications, zero pre-created regular users, locked root, empty
machine-id, no saved network credentials or SSH private keys, and default-off
system suspend.

- Source `b03ae70110a74de987ffb9e2c2b951dddeca9b06`, tree
  `17015e9991cdbea6d5801bf584642a98a2d54cc8`.
- Boot `48bb66ab661ec445067ee126be5a976533d7e959a2f10d4a7ee847680492923a`.
- Rootfs `3d2d5c0fc94cdea2bc535f5cc4d37f51ff70142c4775cd7b61cd85ce91feca25`.
- Kernel `7.2.0-oneplus13-g7a81d184e309-cfb5576138fcf-p4a4fad7955bc`.
- Resources `1.10.2-0ubuntu3.1+op13.1`.

Temporary RAM boots used no partition writes and no persistent installation.
The first orchestration boot stopped before target launch when the host route
parser encountered Windows `RouteMetric=None`; that record is retained and
does not qualify the image. After a host-only fix, the same exact image passed
owner-confirmed screen-keyboard setup, real Adreno GLES and GTK
`GskGLRenderer`/MSM activity, automatic native audio, both actual landscape
channel orders, volume/mute, four visible authenticated wakes, and wake after
an actual 180-second idle blank.

A separate fresh USB boot passed all four phone-powered dock attachments:
130.741 seconds in A, 15.503 seconds in A again, 30.419 seconds in B, and
30.643 seconds in B again. Each attachment passed the real node, automatic
read-only mount, 4096-byte O_RDONLY block read, file-prefix read, and unmount.
The 13.777-second watchdog, service restart read/unmount, and 5.005-second
stable recovered source/role/node passed. Saved firmware values were restored,
PC device/sink+UDC returned, and the existing 5220 MHz WiFi link passed
HTTP/TLS, display health, amplifier shutdown, and all seven Android baseline
properties. No manual role forcing or manual USB mount was used.

Recovered USB `-71` lines remain diagnostic evidence and are not claimed to
be absent. The normal scope is this phone-powered dock/U drive, unlocked GNOME,
and read-only use. Writes, powered/PD docks, video output, other docks or
cables, greeter wake, and native deep suspend remain unqualified.

Camera/GNSS remain paused and NFC remains skipped. The r272 tag remains fixed.
The new full milestone is `oneplus13-full-ubuntu-r286-20261106` on its
matching branch. Any later phone boot still needs a fresh exact plan, an
unconsumed ledger, and temporary `fastboot boot` only.
