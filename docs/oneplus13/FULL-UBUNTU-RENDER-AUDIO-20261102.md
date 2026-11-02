# Full Ubuntu GTK/audio migration and idle-display boundary, 2026-11-02

r264 owner testing confirmed actual screen-keyboard first-user creation, but
reported silence in Settings and sluggish desktop interaction. r266 reused the
exact d16f1ae7 full image from Actions41355509240 with a source-bound RAM renderer
override and audio user adapter; it did not qualify a new pristine image.
Boot SHA256: ba470aee454f9851e49cbbce7dd4c060a1e302b1f0d62045f2e791e51e2d5064.
Rootfs SHA256: e53f66e31a34654a8b66dc4ece9f7d4f4c47a96247f09b132dd35c9754e81467.
Plan SHA256: 22f27ff5bc27ed9253b23af07f272b36a1a17158925918c9d26d9ec488d5c05c.

## GTK renderer

The full rootfs and firstboot script forced GSK_RENDERER=cairo. The earlier
Adreno GLArea test proved a real GL context, but did not prove GTK widget scene
rendering used that context. r266 changed only the RAM environment to ngl and
read the actual Gtk.Native renderer: GskCairoRenderer for the control,
GskGLRenderer for the GPU path. The fixed animation consumed3.596 CPU seconds
in5.641 wall seconds with Cairo, versus1.310/4.806 with GL. Callback rates were
similar; these are controlled widget CPU measurements, not compositor FPS.

An independent GTK widget process exposed msm DRM fdinfo:923872959ns GPU engine
time and347762335 GPU cycles. GNOME Shell itself had17698389802ns and4912402432
cycles; Settings and Nautilus also exposed msm GPU work. The owner confirmed
the desktop was clearly smoother. A resource-monitor GPU0 indicator does not
override this driver evidence; its MSM statistics integration remains separate.

The candidate now uses the current GTK spelling GSK_RENDERER=gl (ngl is the
same renderer's deprecated alias in the measured GTK build), removes the
software override from the desktop checker, and retains actual renderer checks
as a hardware gate. References: https://docs.gtk.org/gtk4/running.html and
https://docs.gtk.org/gtk4/method.Native.get_renderer.html.

## First-user audio

The image already contained the exact OnePlus13-Audio-Probe graph, phone ACF,
UCM and bounded native tests. Firstboot did not activate them; the desktop helper
also hardcoded the old account name. r266 adapted only that account constant in
memory to UID1000, preserving original file/kernel/board/policy hash checks.
The actual two-second microphone check and independent two-amplifier acoustic
correlation passed; raw captures were deleted, controls restored and amplifiers
stopped before desktop integration. The existing Pulse ALSA fallback then
provided the system sink at50% software volume. The owner confirmed audible
output. Cleanup later verified both amplifiers off and fault-free.

The candidate selects GDM's actual first user rather than creating an account.
Its conditional RAM service is bound to user@1000.service and requires native
firstboot. Only the automatic full-desktop boot carries the new immutable
oneplus13.first_user_audio=1 gate; manual probe alternatives remain unchanged.
It runs the existing real microphone/acoustic prechecks once per RAM boot before
enabling the original UCM/PipeWire route. It does not fake precheck receipts,
increase the existing1023 ceiling or add stock dynamic speaker protection.
This remains a bounded RAM validation profile, not persistent audio policy.
Stale numeric Pulse node/module IDs are never sent into a replaced user bus.

The owner also identified a remaining stereo issue: one landscape direction
matches the physical speakers, while the opposite direction needs left/right
remapping. Orientation-dependent routing is not yet accepted. Dynamic speaker
protection, absolute Android-equivalent loudness and long-duration use remain open.

## USB and automatic blanking

r266 first insertion passed actual host/source, U-disk enumeration,4096-byte
O_RDONLY block reads before/after130.694seconds, NTFS3 read-only file reads,
desktop volume visibility and unmount. Actual detach restored VBUS/current.
The second insertion again had host/source and a real USB storage node, but no
desktop mount appeared. Two-insertion/watchdog/service-recovery acceptance did
not complete and the whole round remains failed. Do not call it full USB success.

The owner saw a black screen that did not wake on touch or short power press.
Saved state showed ScreenSaver active, idle-delay300, PowerSaveMode3/OFF and
disabled CRTC. Normal Mutter DPMS ON returned PowerSaveMode0 while retaining
the lock, but the owner still saw black. A later post-wake collection was refused
after the USB identity disappeared; no post-wake DRM success is inferred.
Screen blank/unblank and physical wake-key integration remain unqualified.

The RAM candidate now keeps idle-delay0 so this known unqualified display-power
transition cannot silently interrupt testing. It does not disable manual lock,
claim a wake fix or qualify suspend. Diagnose proper display/input wake before
a persistent daily-use profile; the initial repeated-mount failure may relate
to locking, but that causal link has not yet been established on the phone.

Exit restored actual saved USB values in24->64->18->17 order with dirty0,
device/sink+UDC returned, both initial/post5GHz5220MHz HTTP/verified HTTPS passed,
audio stopped cleanly, and Android's seven properties matched. No flashing,
slot changes, partition writes or persistent installation were performed.
Camera/GNSS remain paused; NFC skipped. Source changes require a new complete
Actions image and fresh source/image-bound phone plan and unused ledger.
