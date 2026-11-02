# Pristine full Ubuntu: r272 acceptance, 2026-11-03

The exact new image from source `d3605af22a7377a244421babfb65f73afbc617ea`,
tree `db78ba9e36a221f89cb7062cbd2e03e646be57a1`, passes the combined r272
physical full-desktop test. All five jobs in [Actions41462106749](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/41462106749)
succeeded. This is the pristine packaged image, with RAM observation programs
only and no functional OTG, renderer or audio overlay. No partition was written.

| Image | SHA256 |
| --- | --- |
| boot-automatic-usb-ram-experimental.img | `8e21ce9e2ae46486a7c8d82354f470221e16643afa2e79c2c9770637685c15be` |
| rootfs.squashfs | `28c13993f6b01cef36cf55aac151d4226473e20d07d5c356d140fce0b63138bb` |

Three downloaded ZIP digests matched GitHub. Independent readback checked41
image and46 kernel checksums, boot sections/FDT/cmdline, source-bound runtime
files and kernel/rootfs agreement. The OTG helper matches the r270 candidate
byte for byte; other USB and storage guard files retain their prior hashes.
The image has1662 installed packages including Ubuntu desktop, real ARM64
Epiphany, Software, Text Editor, Terminal, Files and LibreOffice Writer/Calc.
It has zero regular users, locked root, empty machine-id, no default password
or autologin. The owner used the actual phone screen keyboard and initial
setup to create a RAM-only account. That account never enters the image.

## Physical USB and recovery

The same dock and Udisk were powered only by the phone, without an external
charger or PD supply. Two planned attachments used the original phone-side
connector orientation. After a proved actual detach, the owner flipped only
that connector180degrees and made a third attachment. There were no extra
attachment retries in r272. The kernel did not expose an orientation attribute;
the physical flip is an owner action record, not an invented kernel reading.

All three attachments produced actual Type-C host/source, external storage
nodes, automatic GNOME NTFS3 readonly mounts and visible desktop volumes.
Each passed4096-byte O_RDONLY block reads, nonempty readonly file-prefix reads,
post-hold block reads and successful unmounts with return code0 and no residual
mount. Continuous hold durations were130.549,15.458 and30.617seconds.

Freezing the automatic OTG process triggered saved-value restoration in
15.525seconds. After killing the frozen process and starting the native service,
fresh block reading and unmount passed. Firmware source, actual host/source
and the same block node remained valid continuously for5.138seconds before
the final recovery result. No forced or lazy unmount, role write, raised current
limit or source-loss grace period was used.

Supply admission remains actual host/source before current64=1250 then VBUS24=1.
Final shutdown restored the actual saved values in24→64→18→17 order with all
four dirty bits clear. PC device/sink and configured UDC were proved before
Android return. This qualifies the tested readonly storage path, not arbitrary
docks, disk writing, external PD/charging, dock video or other hub interfaces.
Prior r268/r269 failures and r270 source-loss/extra-flip evidence are retained;
this pass does not retroactively establish their cause or universal stability.

## Other combined checks and cleanup

The ordinary user inherited GTK GL without an observer renderer override.
Actual GTK MSM engine work and Adreno GLES pixel readback passed. The packaged
first-user audio service automatically ran native microphone and two-speaker
acoustic checks and enabled the correct first user; raw audio was deleted.
Prior owner audition/smoothness feedback on the unchanged audio/render source
is retained separately; r272 repeated machine checks, not a new manual audition.

The same5GHz5220MHz link passed association/IP/HTTP and certificate-validated
HTTPS before and after USB. The post-check preserved the existing connection.
Final CRTC active, Mutter power ON and unlocked desktop checks passed with zero
DPU frame/kickoff/panel-dead and GMU vote errors. Both amplifiers were proved
off at exit. Android's seven baseline properties matched. The fresh one-boot
ledger is consumed and is not reusable.

## Limits and delivery

This is a full desktop **bounded RAM test image**, not an installer or a claim
of complete daily phone support. Its original300second return deadline was
retimed in RAM to3300seconds by the bound r272 plan using daemon-reload only;
firstboot and Required timers were not restarted. Future boots require fresh
current-chat plans/ledgers and authorization. Android is preserved; flashing,
erasing, slot switching, repartitioning, dual boot and persistent installation
remain unauthorized.

`idle-delay=0` avoids automatic blanking; manual lock/power-button wake and
suspend remain unqualified. Opposite-landscape stereo remapping remains open.
Camera/GNSS are paused and NFC is skipped. The GPU resource monitor showing0
is not evidence of CPU rendering; measured rendering evidence is used instead.

The local paired delivery is `images/full-ubuntu-r272-20261103`, containing
the exact boot/rootfs, provenance, independent readback, sanitized acceptance,
Chinese usage notes and SHA256SUMS. Detailed owner actions, the exact bound
plan, observers, consumed ledger and private receipts remain in the local
r272 record. Sanitized machine-readable evidence is in
`FULL-UBUNTU-R272-ACCEPTANCE-20261103.json`.
