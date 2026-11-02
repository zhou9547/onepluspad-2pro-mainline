# Full Ubuntu RAM controller candidate, r270, 2026-11-02

Base image source6ce1507882de86efd4d65c5639d2f15e89027169,
Actions41441022720; boot4d2b9bff57097d1e74ee1a5ee5cfce08341ce348bd1b8a88292d802d9dcc0612,
rootfs a77ed07b1b0dd8f48c544ed6c2021c5edd43508ba855af8a268bf18474d534c2.
The exact local source candidate is e1ddf0275c1e5c05ec84c09dc42ce6fb6638ec08.
Fresh one-boot plan c1918e09ec5b03fb1153991e237139c264f699322a47d6b0a57f408df9352ca1.

The image-native first-user screen keyboard/account, real GskGLRenderer/MSM
engine work, GLES readback, automatic native microphone/acoustic prechecks and
first-user audio pass. The only functional RAM overlay replaces the automatic
OTG service execution path with the exact candidate helper. Installed image
files remain unchanged. Actual saved firmware values are restored before the
owner change. Native initialization is not repeated. Current/voltage limits,
the15-second kernel watchdog and24->64->18->17 restoration are unchanged.
This is an image-plus-RAM-candidate result, not pristine final-image acceptance.

The following complete within one RAM boot:

- First actual dock/U-disk insertion: real host/source, automatic NTFS3 read-only
  desktop mount,4096-byte block and file-prefix reads,130.297-second hold,
  repeated reads and successful unmount.
- Actual detach and current/VBUS saved-value restoration.
- Second successful insertion: the same real enumeration, automatic read-only
  mount, block/file reads and unmount.
- Deliberate service-process freeze/kill: kernel saved-value restoration in
 15.271seconds; service restart followed by a fresh4096-byte block read and
  successful unmount, with actual returncode0 and no remaining mount.
- Initial and existing-link post5GHz5220MHz association/IP/HTTP and
  certificate-verified HTTPS; active CRTC/Mutter ON, unlocked desktop and zero
  recorded DPU/GMU timeout/dead-panel counts in the final display gate.
- All four firmware dirty flags clear with actual saved values, PC device/sink
  and UDC return, amplifier-off verification and seven matching Android
  properties. One boot, no partition writes, no persistent installation.

An important exception is retained: the initial second-attachment attempt briefly
entered supply, then firmware source and physical Type-C host/source disappeared
before a desktop mount. There was no userspace `off` trigger in the new trace.
The owner physically unplugged, flipped the phone-side Type-C connector180degrees
and reinserted within the same waiting window; that attachment and the later
recovery checks passed. This is an additional failed attachment plus retry, not
two uninterrupted attempts or proof that orientation alone caused the failure.
The candidate policy defect is independently fixed, but it does not explain
every observed source-loss event. Reversible-connector/negotiation stability
remains a separate open qualification item. Original failed traces are retained.

Next: package the exact tested helper once in the reproducible complete image,
independently read back every relevant source/runtime binding, and validate the
new exact image physically. Do not transfer this RAM-overlay result into a
pristine image claim. Keep zero precreated normal users; the owner creates their
account. Opposite-landscape stereo and proper blank/unblank remain open;
idle-delay0 is avoidance only. Camera/GNSS paused, NFC skipped. Android is
preserved; flashing/slot/partition/persistent installation remains unauthorized.
