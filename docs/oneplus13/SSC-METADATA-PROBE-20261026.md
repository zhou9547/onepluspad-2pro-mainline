# Isolated SSC metadata discovery

Correction from full VM validation: the initial QEMU-user loader check could
fall back to host ARM64 libraries. It does not establish an exact-rootfs pass.
The target lacks four runtime dependencies; the isolated export now includes
protobuf-c, qmi, qrtr and mbim libraries with package/source identities and
copyright files, rather than replacing system libraries. New native and full
VM checks remain pending. The earlier three-executable native checks passed;
13 additional wrapper failure/control checks also pass locally. No phone query
or new hardware qualification follows from these source changes.

This phone-only overlay reuses original libssc 0.4.4 discovery and attribute
constructors. The original two delivery patches and Pad packaging remain
unchanged. It exports a separate probe, library and explicit generic dependency
closure, without an enabled service,
firmware, registry, calibration, installer or phone integration.

Before constructing any sensor, the probe sets a process-wide, one-way guard.
The actual libssc send boundary then accepts only bounded, decoded protobuf
SUID queries for registry/accel/ambient_light/gyro/mag and attribute queries.
Both require explicit updates=false; SUID requests also require default-only
selection and the fixed discovery destination. Unknown fields, invalid
destinations, malformed payloads, measurement requests and subscriptions are
refused before QMI. This guard is default-off for the unchanged original API;
the dedicated executable always locks it. There is no unlock API.

The probe never imports sensor_open/close. It discovers the four basic sensor
types concurrently, with an eight-second GLib deadline. Existing synchronous
QMI release/close callbacks can exceed that deadline, so a separately reviewed
host/service hard deadline and cleanup are still required before hardware use.
Availability means metadata discovery only, not samples, axes, calibration,
desktop orientation, complete file service or a DSP release acknowledgement.

Fresh pinned-tar WSL release and ASan/UBSan builds each pass three Meson
executables: decoded policy checks, rejection through the real send path with
a fail-on-QMI double, and the original delivery encoding regression. The
lock-only CLI passes without QRTR. Original QRTR service integration tests and
leak testing are not claimed. Native ARM64 and exact-rootfs sandbox/link checks
remain pending; no new phone boot is qualified.

Source: libssc commit `0cf77b93b55752da34dca2dcecc06fca8665184b`, archive SHA256
`716d6bd6b34d2d753060c6b54c9a87e34fae75b724c763bf9ef487efa3621587`.
License: original GPL-3.0-or-later notices retained. Dedicated build:
`tools/oneplus13/build-phone-ssc-probe.py`; workflow:
`.github/workflows/oneplus13-phone-ssc.yml`.
