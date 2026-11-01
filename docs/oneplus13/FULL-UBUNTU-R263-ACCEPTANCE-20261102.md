# Full Ubuntu first-user, desktop and Wi-Fi acceptance: r263

On 2026-11-02, one fresh, exact-bound temporary RAM boot passed all unattended
software gates and returned to Android with all seven baseline properties
unchanged. No functional runtime files were replaced and no manual hardware
bootstrap was injected. No partition writes or permanent installation were
performed. The private per-round ledger is consumed and must not be reused.

## Exact image

- Published build source: `d16f1ae794aa1ee4b3b26958a6e5d9a22349b6c0`.
- Source tree: `b9bafccf91f1b483bc9cdef93b44e18a31a6f210`; local equivalent: `8002be25b8015e6527d9fb6da9cb2495e2dab136`.
- [Actions 41355509240](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/41355509240) completed all five jobs.
- Automatic-OTG RAM boot SHA256: `ba470aee454f9851e49cbbce7dd4c060a1e302b1f0d62045f2e791e51e2d5064`.
- Full rootfs SHA256: `e53f66e31a34654a8b66dc4ece9f7d4f4c47a96247f09b132dd35c9754e81467`.
- Kernel release: `7.2.0-oneplus13-g7a81d184e309-cabf055643d7a-p59bf6260c9f9`.
- Plan SHA256: `af92bcddee9d01a62058981c51865cbbb5f3518107c67fcab1e03b5dd5090d38`.

Independent readback verifies three archive digests, all 41 image and 46 kernel
checksums, 120 firmware files, matching modules, eleven firstboot runtime files,
and 1662 installed packages. The rootfs has the complete `ubuntu-desktop`
dependency set, real ARM64 Epiphany, GNOME Software, Text Editor and LibreOffice
binaries, and Writer/Calc, Nautilus, Terminal, UDisks2 and GVfs packages. The
delivery image has zero normal users, a locked root account, an empty machine-id,
Initial Setup enabled, no preset normal-user password or autologin, and an empty
NetworkManager system-connections directory. The disposable test account was
created by the wizard only in the RAM overlay and is absent from the image.

## Measured software gates

Packaged firstboot initialized the native display, S3910 input driver, WLAN,
phone sensor proxy and Bluetooth before GDM. Initial Setup fit the 480x1056
logical viewport. A temporary uinput touchscreen exercised actual libinput,
Mutter, GTK and screen-keyboard input for the name and two random 24-character
password fields, then completed nine wizard pages and reached a local ordinary
Wayland session. The fixture was destroyed; no password was logged. This is
synthetic input on real hardware, not a new physical touchscreen or Chinese IME
qualification. The fixture selected the US input source in its RAM profile.

The user compositor mapped the project Mesa library. A user-session Gtk4
GLArea GLES context reported Adreno 830 and passed actual red framebuffer
clear/readback for all sixteen pixels, with GL error zero. This does not claim
human visual confirmation of the display.

Ubuntu Dock was enabled and fixed. Settings and its session bus survived three
observations without compositor replacement. Epiphany loaded an actual HTML
fixture; Text Editor and Files opened known files; GNOME Software exposed its
window; Terminal executed a child that created a proof file. Writer exposed the
ODT document window and known document text. An isolated user-service headless
ODT-to-PDF conversion exited zero and produced a valid PDF. Presence of packages
or processes alone was not used as acceptance for these operations.

Initial and post-desktop Wi-Fi checks both measured 5220 MHz and passed association,
IP acquisition, LAN HTTP and certificate-verified IPv4 HTTPS. The post-check used
the existing link without reactivation or directed scan. These are preservation
checks for already qualified 5GHz support, not new RF bringup.

## USB boundary

Under the newly created ordinary user, the packaged automatic OTG service was
active, its kernel owner was healthy, desktop automount was enabled and the
UDisks2/GVfs volume monitor answered. The phone remained physically attached to
the PC: no host/source attachment, external disk node, or new physical U-disk
read was claimed. At exit, the actual saved firmware values were restored,
all four dirty flags cleared, device/sink and UDC returned, and Android matched
its seven original properties.

The automatic OTG and storage-guard runtime file hashes match the retained full
base, preserving the prior implementation. Physical qualification remains bound
to r246 source2b576347/Actions41299915186/boot5aa85c0b plus its exact RAM overlay:
two actual dock insertions, read-only block/file reads,130.6-second hold,
unmounts, watchdog and service recovery. **The new full image still needs its own
physical dock/U-disk regression with the owner.** Read-only results do not qualify
writes, arbitrary peripherals or all docks. Camera/GNSS remain paused and NFC
skipped; audio/calling are not part of this acceptance. Permanent installation
and a dual-boot layout remain unapproved.

## Observer corrections and bounded recovery

The delivered timer is300 seconds, despite the installer's900-second template.
After packaged initialization, this round changed only a RAM timer drop-in and
ran daemon-reload, checking a900-second readback and identical firstboot/GDM
start timestamps. Restarting this Required timer would stop its dependents and
trigger the intentional hardware-attempt guard. Target/host budgets remained
780/1100 seconds. No functional image overlay was used.

r262 passed the real application/GPU/Wi-Fi gates, but its UI observer mistook an
optional language-pack download for a missing Next button after15seconds. The
download finished naturally and an independently bound touch continuation
clicked the real finish button. Its original completed=false is retained.
r263 added a bounded120-second wait for this normal page and completed without
that continuation. r260's40-second TXT conversion timeout was not used to infer
a broken Office package; real ODT GUI and PDF operations passed on r262/r263.

The sanitized evidence is [r263-full-ubuntu-acceptance-20261102.json](evidence/r263-full-ubuntu-acceptance-20261102.json).
Private raw records, credentials, device identifiers and reusable authorizations
are excluded. Delivery contains the paired RAM boot/rootfs and checksum files;
it is a bounded, volatile test system rather than a persistent installer.
