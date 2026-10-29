# Phone camera callback checks, 2026-10-29

Camera component Actions40869936054 succeeded on38e3f390. The downloaded archive
matches GitHub SHA256 e22bf2713e66783a7cb6e072d84121a1cff475c8ec9bf859b70103206421398f.
Eleven reported AArch64 object files match their byte lengths and SHA256 values.
The twelfth object, aw88395_lib.o, was compiled but omitted from the upload list.
The workflow now uploads it. This older archive is explicitly incomplete;
do not describe it as a complete independently verified set of twelve objects.

The new check-phone-mmio.py compiles the actual phone PHY callbacks against
bounded host register memory. Only the kernel probe glue is excluded. Both
release and ASan/UBSan executions pass45 cases:29 table rates and core vote
boundaries, lane/timing/rate rejection before MMIO, actual timer-rate rejection,
refgen timeout followed by lane teardown, reset release/assertion, preservation
of unrelated lane-mask bits, IRQ mask/acknowledgement and invalid accesses.
These checks exercise the adapter callbacks, not physical MMIO, the kernel IRQ
framework, the clock/power providers or real sensor capture.

Normal --cphy --phone-cphy component builds now run these checks and preserve
their verification report. --compile-only continues to skip test execution;
--prepare-only continues to skip compilation and tests. The phone source lock
is checked before the catalog generator executes, rather than afterwards.

A clean WSL archive-based cross build with --cphy --phone-cphy --infrared passes
with W=1/KCFLAGS=-Werror, all13 AArch64 objects, the disabled-parent phone CCI DTB,
and the existing audio/C-PHY synthetic checks. No runtime board node is enabled.
Source provenance and fixed upstream inputs remain in the component manifests.

The GStreamer caps error collector now resynchronizes its element iterator and
bounds iteration to16 attempts. Previously repeated RESYNC could loop forever
before the pipeline's finally/NULL cleanup. Nine focused tests pass, including
repeated/resolved resynchronization and the native raw-frame pixels/timestamp/
NULL selftest. This fixes diagnostic cleanup behavior, not the still-open
hardware not-negotiated error.

Bounded read-only Android queries retained a matching seven-field baseline,
found the existing module files but did not identify the selected L/S supplier.
No camera was opened, no frame was collected and no phone files or partitions
were written. Keep raw metadata, identifiers and module contents private.

Capture remains blocked on the selected supplier initialization, a reviewed
19.2MHz three-trio sensor mode and the complete phone CAMSS/CSID power/resource
graph. Rotation polarity, absolute speaker loudness/protection, hardware
framework playback and the remaining peripherals are still open. Retain the
accepted combined desktop/WiFi/Docker/audio baseline until a fresh combined
hardware round qualifies functional changes.
