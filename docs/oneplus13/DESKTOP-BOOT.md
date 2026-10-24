# RAM GNOME boot handoff

Current restriction, 2026-10-24: native desktop packaging is disabled pending
the [offline gate](OFFLINE-NATIVE-GATE.md). The new QEMU observer requires an
actual kmod display-loading-policy check; older passed handoff reports do not
cover it. No further hardware experiment is authorized by this document.

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

Correction after40007507201: the installed rule is confirmed present and inside
the staging root, but the runner's v255 verifier explicitly rejects --root with
FILE arguments. The current/latest manual describes a newer interface. Examined
[v255 implementation](https://github.com/systemd/systemd/blob/v255/src/udev/udevadm-verify.c):
its FILE-only branch directly parses absolute paths without executing RUN.
Validate the asserted absolute staging-file path using that branch and record
the verifier version. The initial offline-chroot missing-path cause is not
independently proven; it is no longer needed by this verification route.

### First complete handoff version, a6c8ceb

Actions40007875169 passes. The actual rootfs has782 packages and SHA256
b047f84a6766b23d2c1de733acfda873df148686ee299433bf0989e6c956bc72
(432734208 bytes). Artifact12524664064 is432771590 bytes, ZIP SHA256
213f54f49b5b81a265ccb0e6338d9dcd397542e1824b4201f000bea76f897811.
Handoff artifact12525316939 is1023409 bytes, SHA256
01f1f7be00a29ad736e5d8431f4a5e2e97c2b0ef0c48eb143c01aad6c976a26e.
Both actual downloads match GitHub digests; local CRC/manifest/file checks pass.

QEMU reaches systemd, confirms the root is OverlayFS, vda is read-only, root is
locked, and the matching kernel marker is present. Guard, deadline timer,
NetworkManager and D-Bus are active. Actual GNOME Shell reports50.1; GDM is
active/running. HANDOFF_OK occurs at62.85s and controlled poweroff at65.05s.
This proves userspace only; no display pixels, input event or radio is emulated.
The900-second timer is armed but its expiry was not exercised by this first run.

Host-only package-desktop.py produces separately named PRIVATE RAM images after
fresh positive-stock / all-six-overlay /15-bank checks. Its image-header and DTB
bootargs must agree with the tested rootfs. Default image14032896 bytes hashes
d8740f3a2e0c96bfa774b6f1840dc19a9eeb9f40e8973a7e7c9ad5d489dc2042;
native image14680064 bytes hashes
f904630641caa55aba25b166547be00db4550ee28a027dab75891a92bc789399.
The native archive adds only the matching existing nine modules and private SPR
profile to the same public control flow; this private archive is not QEMU-tested.
Neither image was booted on the phone. No v4 desktop install image is generated.

Host chunk-server checks pass the64MiB boundary/final-part length and reject four
unlisted paths without changing host networking or contacting the phone.

### Next bounded acceptance: exercise recovery expiry

Use the exact already verified a6c8ceb rootfs bytes, without refreshing/repacking
them. Change only the emulator observer: after HANDOFF_OK, leave the VM running;
an emulator-identity-guarded runtime drop-in shortens the existing deadline timer
to120 seconds and adds a console marker before the original reboot command.
Require HANDOFF_OK, then expiry marker, then kernel restart/process termination.
Production unit900s and initramfs900s remain unchanged. This proves systemd timer
execution under QEMU, not phone recovery, kernel-stall coverage or actual900s timing.

Final software-path acceptance: the first test supplies SquashFS via read-only
virtio block, while the phone must fetch chunks. Exercise the same production
fetch/size/hash/overlay/handoff path using an emulator-only virtio network named
usb0 and the fixed172.16.13.1/.2 addresses. Bind the host chunk server only to
loopback. Require exactly the expected bytes/parts, successful systemd/GDM
checks and expiry-driven restart. Keep the read-only virtual disk as a storage
guard positive control. This tests HTTP client/assembly, not real NCM hardware.
Both emulator selectors require the dummy-virt DT before any emulator setup.

The block-input recovery test40009535169/0379a3a passes: HANDOFF_OK is followed
by the shortened120s systemd deadline and kernel restart. The exact a6c8ceb
rootfs bytes remain unchanged. The HTTP variant uses a180s emulator deadline to
include the additional full-image transfer; production900s remains unchanged.

### Final complete HTTP path, ef63950

Actions40010305668 passes with the unchanged432734208-byte a6c8ceb rootfs.
The actual ARM64 initramfs consumes exactly seven HTTP chunks/432734208 bytes,
checks its size/SHA, mounts the RAM overlay and hands PID1 to systemd. GDM is
active/running; GNOME50.1 and guard/NetworkManager/D-Bus checks pass. HANDOFF_OK
is at113.67s, the shortened emulator deadline at180.53s, restart at180.79s.
This is HTTP over virtio/slirp, not physical NCM or WLAN.

Actual handoff artifact12526077066 is1023996 bytes, SHA256
86dfd652a62464f97e9ccc10d6c772654e59798c2dceb7be2546ce1a9a8ef198.
Local downloaded ZIP CRC, manifest/hash checks and all seven-part counters pass.
Generic initramfs SHA256 is31a94bc3399afd054480917371cae6bba1d940fd25ca0042e0a44c97979c77d2.
The private packager now requires both HTTP and expiry acceptance.
Fresh default/native RAM packages are14032896/14680064 bytes respectively:
6a24fbf939d81f34e59943e2fa89467fe10c01d99e3adcdc0411ec15d0a0a967 and
cf67cb4cd1b62657e811b4ea53207ecc363ed13a7e0f5e07aa27bf6f4072cd58.
Their headers/DTB cmdlines, original stock positive control, all six overlays,
15 protected RAM banks and identical public cpio entries pass offline.
Private added modules/SPR remain untested as an archive and on the phone.
