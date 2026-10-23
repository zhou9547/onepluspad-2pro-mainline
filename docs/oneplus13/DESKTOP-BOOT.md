# RAM GNOME boot handoff

Scope, 2026-10-24: turn the separately built GNOME userspace into a bounded RAM
desktop candidate. Reuse the Pad init-ncm SquashFS/OverlayFS/switch_root design,
chunked NCM transfer and early physical-platform correction, with phone-owned
addresses, identity and services. Preserve the default diagnostic artifact and
its 300-second recovery. Do not introduce an installed-root or partition path.

The desktop profile must be explicitly selected. It accepts only a fixed USB
host URL, a SHA256 and bounded byte size; fetch exactly the derived number of
64MiB parts, enforce every part's size, and verify the complete image before
mounting it read-only. Use a RAM upper/work layer and verify adequate memory.
Only PID1 may hand off; failure leaves diagnostics and its deadline alive.

Runtime services must preserve NCM172.16.13.1/24 (host172.16.13.2), bind all
development shells/evidence HTTP to USB, continuously protect physical block
devices, and preserve an absolute 900-second boot deadline across switch_root.
Stop only tracked initramfs processes. Correct the unused Gunyah userspace
export before systemd starts, guarded by phone identity, HLOS VMID3 and no bound
hypervisor driver. No Pad model/chassis/address/board data may be imported.

Acceptance: use the exact previously verified kernel and modules; record all
input/output hashes. Check runtime units with systemd-analyze, build on ARM64 in
Actions, and QEMU-boot the actual GNOME SquashFS through the handoff. Verify
systemd's liveness marker, locked root, storage protection and bounded recovery.
QEMU proves only userspace, not native display, touch, radio or ABL acceptance.
Prepare a separately named desktop initramfs, never label it flash-ready.

The existing native-display tree remains display-only. Isolated touch/WLAN/GPU
tests are still required before combining hardware. Matching generic OTA files
are inputs, not firmware authentication/SAR or working radio evidence. A future
phone test requires the owner's later hands-on recovery window; current access
is read-only and this work performs no phone command.

Implementation review: use blockdev's BLKROSET ioctl for new physical devices;
the block ro sysfs attribute is read-only. The package's udev rule invokes the
short blockdev command only on add, and a separate early service continuously
checks protection. It suppresses desktop automount presentation only during an
explicit RAM session. The inherited diagnostics retain their existing guard.

Keep a verified GNOME artifact before running the handoff experiment so later
fixes do not repeat the apt/base build. A refresh must first verify the complete
base manifest/SHA256 and ARM64 executables, extract into a fresh Actions staging
tree, replace only this phone package's support files, recheck units/udev, and
repack with provenance linking the base image hash. Include exactly matching
modules and the four verified graphics firmware files. Do not install pending
WLAN inputs into any firmware search path before board selection is known.

The previously independently downloaded/verified GNOME base39809729390 remains
available as artifact12438829003 (419515851 bytes). Use its exact artifact name
as the refresh source, instead of waiting for another complete apt build. The
refresh verifier rechecks every file and actual SquashFS binaries before changes.
The initial fresh build40004679869 and queued667a490 iteration are superseded;
cancel them before running the verified-base refresh. No device state is changed.

Refresh40007121215 reached and independently verified the419479552-byte base
SquashFS (SHA25697611cd24f0bc73c67a7393b9def55cbea3e952d26ca1ecfeb99b1d0b6e5ecef,
782 ARM64/all packages, GNOME50.1). Module/support installation and systemd unit
checks passed. The udev verifier failed during offline chroot path resolution;
that extraction has no /proc mount. Use documented udevadm verify --root with
the rule basename, and assert the installed path is a regular file inside the
staging tree before validation. Do not bypass the verifier or execute udev rules.
