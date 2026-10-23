# Stock calibration and native input/display

## Scope and acceptance, 2026-10-23

The owner authorized root ADB reads from their running Android phone, and
explicitly prohibited every phone modification. No boot experiment is allowed.
The independent pre-device audit found no write operation in collect-stock.py.
All original images, runtime FDT, identifiers and logs stay outside Git in the
private host workspace. Public reports contain only board facts and hashes.

Read-only collection must establish phone/SoC identity, current slot, boot image
formats and sizes, actual RAM/reserved ranges, selected panel and touch driver.
Every block read uses dd with if only and host stdout capture. No debugfs control
file, raw register accessor or device-character protocol endpoint is read.

Offline acceptance: reproduce stock image parsing and selected DTBO application
with a positive stock-tree control, mechanically compare panel commands to the
running FDT, implement isolated candidates and run structural/build checks.
Compilation cannot establish screen output, physical touch or bootability.

Hardware acceptance, deferred under this authorization: bounded RAM boot, real
debug transport and recovery; then native panel takeover and physical multitouch
across cold boot and display power cycles. Persistent installation follows those
checks and requires separate authorization.

## Evidence

Private host evidence: workspace private/oneplus13-stock-20261023. Current-slot
boot, init_boot, vendor_boot, dtbo, vbmeta and runtime FDT were collected with
read-only commands. Each host SHA-256 matches a separate device-side sha256sum.
The ABL image was read for offline inspection too. Nothing was uploaded from
the phone to GitHub. The running Android version is PJZ110_16.0.10.501(CN01).

Stock boot/init_boot/vendor_boot use header v4, page size 4096. Partition
capacities are 96/8/96 MiB respectively. Boot has a kernel and no ramdisk;
init_boot has the generic ramdisk; vendor_boot has a vendor ramdisk and 13 base
DTBs. Actual bootconfig selects base index 2 and DTBO entry 5 of six. These are
phone evidence, not copied Pad indexes or capacities.

The libufdt positive control uses LineageOS/android_system_libufdt
70c20864187df19f3e7d358ca8436f77d61a3f39 plus the pinned kernel libfdt. It
reconstructs the selected AA569 panel subtree and S3910 HBP subtree with every
runtime property matching. DTBO root identity is selection metadata outside
fragments: libufdt does not merge it. The running root qcom,msm-id/board-id match
the selected overlay's root byte-for-byte; the selected base SoC pair is present
in that table. An initial test wrongly required libufdt's merged root to equal
runtime and failed; retained private v2 output documents why that assumption was
replaced by two explicit checks, without weakening the subtree control.

The local MinGW compiler is 32-bit and Python is 64-bit, so ctypes cannot load
its DLL. The host ufdt-apply harness avoids that ABI mismatch. Its declaration
is checked with -Werror=implicit-function-declaration. No phone change is needed.

Debugfs golden snapshots (DRM state, clocks, regulators) are unavailable in the
running Android mount namespace. cat returned error text; those files are not
accepted as hardware evidence. Debugfs was not mounted or configured.

Only board facts are exported to stock-profile-pjz110-24g.json. Panel serials,
boot arguments, calibration, FDT originals and images remain private.

## Candidate validation

Actions 39892351557 / d337d2f4bea9fae5e4ed0d87f8d97c2eff9c707b built the
kernel, both DTBs and S3910 module, and passed QEMU. Both default and touch DTBs
then passed every one of the six actual stock overlays in the isolated sink;
the operational mainline nodes were unchanged. The selected stock control checks
all 764 panel and 34 touch properties in both directions, rejecting extra
properties as well as missing or different ones.

The owner-only memory profile has 15 nonempty banks. Every protected stock
interval inside those banks is already covered by the platform reservations;
no new reservation was needed. Overlapping RAM banks and protected overlaps
with a reusable pool are rejected. Two separate Python processes with different
hash seeds produce identical DTBs after sorting the symbol union. Bootloader
memory fixups and actual RAM usability remain hardware questions.

package-calibrated.py uses the captured full partition capacities and stock
vendor header addresses, the calibrated DTB, and the verified kernel/initramfs.
It generates unsigned v4 boot/init_boot/vendor_boot and a v2 RAM-format candidate
on the host, then independently slices all image sections back. The generic
ramdisk is an empty valid archive; diagnostic init stays in vendor_boot. No
Android command line, original image, AVB signing key or vbmeta change is copied.
Actual ABL loading/relocation and the hypervisor path are still unverified.

The collector now records blockdev --getsize64 results and rejects incomplete
full reads. Its updated header-only path was exercised read-only on the phone;
the running FDT and all current-slot header bytes match the first capture.
The captured Android is rooted: these are backups of the working current
snapshot, not a claim that every image is a pristine OEM recovery image.
