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
