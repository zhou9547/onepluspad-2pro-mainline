# Phone firmware provenance and isolated RAM staging

The inherited run39/run43 payload is held against further phone use. Its ADSP
files are the original Pad reference download: only 6 of 58 files match the
current phone. The saved, verified phone OTA modem image provides all 58 exact
current-stock matches. Existing successful ADSP startup and battery observations
are historical behavior, not proof that the inherited firmware was appropriate.

The phone ADSP/DTB split images pass structural review against the pinned kernel
MDT/PAS loader and the actual reserved-memory regions: complete segment set,
lengths, packed header/hash agreement, relocation span and no overlapping loads.
This does not establish secure authentication, DSP ABI, sensor attach or streams.
`review-pil-firmware.py` has nine malformed-input/control tests. Firmware bytes,
owner registry and per-unit identity remain private and are never uploaded.

The inherited WLAN firmware, board file and regulatory database also came from
the reference set. Exact phone OTA inputs are available, and saved Android logs
now establish actual peach BDF/regdb selection. Effective SAR/power policy and
Linux enforcement remain unresolved. Historical Linux logs record
chip_id2/family4/board_id255/soc_id0x40210200 under the reference firmware; these
are useful observations, not proof of Android's active selection or RF limits.
Do not turn prior scan/HTTPS successes into board/regulatory acceptance.

The next isolated candidate disables the Bluetooth node, PCIe WiFi endpoint,
WCN PMU and sound node, retaining the already quarantined WSA branch. A new
matching-module rootfs denies unreviewed wireless, audio, media, NFC, FastRPC,
power-sequencing and PCI power-control loads, including transitive dependencies.
The exact closure currently has 373 modules. Built-in drivers require separate
DT review; this modprobe policy is not a security sandbox. Existing display
manual-load rules and USB recovery remain intact.

Only 58 phone ADSP and four owner-matched graphics files enter the private
minimal firmware payload. It contains no radio firmware, audio topology,
packages, modules or registry overlay. Hashes and platform/thermal gates precede
one ADSP start from offline; no stop/restart loop is permitted. The combined
test checks the new GNOME rootfs, explicit display, real GPU readback, CPU policy,
input and battery/platform inventory. There are no radio tests or sound/sensor
streams. Critical guard/health failure halts further hardware runs.

The generic exact-rootfs QEMU run40219868062 and matching-module/Mesa assembly
run40221133412 passed handoff and automatic deadline. The latter lacked the
complete module policy and is not eligible for hardware. The guarded follow-up
run40223386011 passed final QEMU/artifact/actual-policy-byte verification.
run67 started the exact phone ADSP but hit shared CEC/UBWC display denials and
recovered in70.9s with matching baselines. Actions40226313784 qualified the
explicit shared-core prerequisites on the same rootfs. run68 then jointly
passed exact-phone-firmware display/GPU/ordinary-user desktop/platform checks
and recovered in93.6s with all seven samples equal. No radio or audio/sensor
stream was enabled. See SHARED-DISPLAY-CORES-20261026.md.

Owner sensor registry was read twice consistently and imported offline using
the original narrow helper: 744 files/261787 bytes. Socinfo/property mapping
matches the original shim. Phone ROM configuration is retained separately from
the Pad configuration. None of this establishes reverse-RPC ABI or physical axes.

Both stock amplifier I2C addresses bind aw882xx and log a PID2308-specific
voltage-offset callback. This is indirect family evidence, not a passive raw-ID
read, independent calibration or proof that a compile-only draft is safe.
The draft probe writes profiles and must not be loaded for identification.
