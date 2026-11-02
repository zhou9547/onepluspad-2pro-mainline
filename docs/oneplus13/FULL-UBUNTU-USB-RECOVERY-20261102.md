# Complete Ubuntu USB evidence and recovery candidate, 2026-11-02

Source6ce1507882de86efd4d65c5639d2f15e89027169 / Actions41441022720
passes all five jobs. All three archive digests and independent boot/rootfs/kernel
readback pass. Boot4d2b9bff57097d1e74ee1a5ee5cfce08341ce348bd1b8a88292d802d9dcc0612;
rootfs a77ed07b1b0dd8f48c544ed6c2021c5edd43508ba855af8a268bf18474d534c2.
The full image contains1662 packages and zero normal users, locked root, empty
machine-id, first-user setup and no autologin. It is still a temporary RAM image.

r268/r269 establish image-native GskGLRenderer with actual MSM engine activity
and GLES readback, automatic native microphone/acoustic checks and first-user
audio activation. The owner creates the account with the screen keyboard and
confirms audible sound, smooth interaction and visible desktop. No functional
RAM renderer/audio overlay is used. The opposite landscape speaker mapping and
blank/unblank remain open; idle-delay0 avoids automatic blanking, not a wake fix.

r268's first physical USB attempt reads4096-byte block/file prefixes but is
interrupted at80.712seconds. The owner confirms accidental physical loosening.
A same-boot continuation then fails before a new physical attempt because its
observer omitted restarting the already stopped OTG service. That controller
error is retained; its separate replacement explicitly starts the service before
waiting for actual readiness. No old ledger or failed result is reused.

r269 uses the same pristine full image in one new bounded boot. Two real dock
insertions enumerate the external disk, automatically mount NTFS3 read-only,
read4096-byte block and file prefixes and unmount successfully. The first holds
130.562seconds and repeats its reads. Actual detach restores current/VBUS.
The process-freeze watchdog restores all four saved values in16.315seconds.
Display CRTC remains active, Mutter power is ON and DPU/GMU error counts are zero
through the ordinary insertion/hold phase. Both initial/post5GHz5220MHz checks
include HTTP and certificate-verified HTTPS.

The original service-restart block read succeeds but its immediate unmount check
fails without sufficient return diagnostics. A new, separately source-bound
same-boot observer records unmount status and bounded mount-table settling; it
does not relax success or force/lazy-unmount anything. Its attachment read/file
read/unmount succeeds and its watchdog restores values in15.839seconds, but the
subsequent service restart never regains host/source. Kernel history contains
descriptor/address errors-71 and real USB bus removal. The owner confirms the
connection stayed seated, with no safe-remove action or external power change.
Therefore neither a mount-table race nor a complete recovery fix is established.
Overall extended USB acceptance remains false. Firmware saved-values/PC role,
amplifier off,5GHz post and Android's seven baseline properties pass at exit.

The candidate corrects an independently reproducible policy defect: once power
is active, a temporary absence of xHCI/root-hub enumeration currently issues
`off` even while both actual Type-C host/source and firmware source remain valid.
Controller availability stays mandatory for initial activation. Active supply
now follows actual Type-C and firmware source, so real role/source loss still
turns power off immediately. No role is forced, no current/voltage is raised,
and the kernel watchdog and24->64->18->17 restoration remain unchanged.
The last off-trigger observation is retained for the next diagnostic run.

The actual controller regression fails before this correction and passes after
it.25 focused tests pass; the phone suite runs823 tests with one skip and no failures. These are offline
state-machine tests, not phone proof. The candidate is not yet built into a new
qualified image or proven to explain the observed-71 recovery failure. It needs
an exact source/image-bound RAM validation and then a reproducible image build
at a stable milestone. Camera/GNSS remain paused and NFC skipped. No flashing,
slot/partition change or persistent installation occurred.
