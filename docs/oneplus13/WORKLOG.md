# Work log

## 2026-10-22

The user requested offline adaptation and successful Actions artifacts before
their hardware tests. The supplied link resolves to zhou9547's Pad integration
fork. Its base is 88fd48f85dee54c482a98e55319b11d1739e8852.

The Pad kernel is pinned at 7a81d184e3098624d4342d8f4eff5e23674bcc9f.
index986's OnePlus-13-WIP board at 1f2047e8663eda76c8b172fd3e040e3b3fa17950
provides phone-specific regulator, USB, storage and reserved memory clues.
The newer skb8 fork is research only: its README marks touchscreen support
despite stating that the driver is missing, and its DTS has duplicate properties.
It is not used as a hardware validation source.

Plan: build the pinned platform kernel with a separate phone DTB/config, a
read-only RAM diagnostics initramfs and a non-flashing boot image; run automated
artifact and QEMU userspace checks. Do not inherit the Pad partition/AVB values.

Added a separate native ARM64 Ubuntu 26.04.1 GNOME staging build. The official
base SHA256 was checked against Canonical's SHA256SUMS and package resolution
uses the 20261020T000000Z signed snapshot. No phone firmware, default password,
partition writer or automatic installer is included.

The first rootfs build failed before package installation because Ubuntu Base
does not include the CA bundle needed by HTTPS apt. The fix seeds the standard
host bundle until the signed target ca-certificates package installs it. TLS
and archive signatures remain enabled; apt update now fails on any index error.

Official OnePlus vendor sources were locally inspected at
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3. The dodge touch overlay confirms an
S3910 variant with SPI at 19 MHz, IRQ162/reset161, PM8550VS_J GPIO3 and L4B.
Multiple display/touch variants exist, so matching the user's actual panel is
still required. No guessed active driver node is added to the diagnostic DTB.

The TLS failure repeated with a copied bundle. Local HTTPS retrieval of the same
snapshot succeeded, narrowing this to Ubuntu Base's unconfigured trust lookup.
The next build diagnoses host HTTPS separately and explicitly configures apt's
CA file until target ca-certificates is installed; no third blind TLS bypass.
System QEMU installation is deferred until after compilation, and user-mode
QEMU uses the smaller dynamic host package instead of every static emulator.

Ubuntu GNOME staging build 39807949262 succeeded and produced a 419261065-byte
Actions artifact. The x86 runner remained in slow cross-toolchain downloads
even after changing the mirror, while the native ARM64 rootfs runner fetched
its dependencies quickly. Kernel CI therefore moves to the proven native
ARM64 runner and uses its native triplet-named GCC, avoiding that download.

Review found that --no-install-recommends omitted systemd-resolved while the
image's resolv.conf targets its stub. It is now an explicit package requirement
and asserted after installation. Root credential lock and empty machine-id are
also checked from the actual completed SquashFS, not just the staging tree.
Phone DTS static label inspection found a missing VPH fixed supply; the exact
provider from the attributed phone reference was restored before the next build.

First full native configuration passed all required built-in dependency checks.
The DT compiler rejected missing board-supplied bi_tcxo divide-by-two clocks,
alongside the already diagnosed VPH supply. The complete DTS + included DTSI
reference graph was inspected; both fixed-factor providers were restored from
the same phone source. No force-output flag or disabled compiler check is used.

## 2026-10-23

Native rootfs build 39809729390 succeeded after explicit DNS dependency checks.
Independent verification run 39812509439 downloaded that artifact on a fresh
runner and verified every checksum, all 782 package architectures, actual ARM64
GNOME/GDM/NetworkManager binaries, locked root and empty machine-id in SquashFS.
The image is GNOME Shell 50.1, 419479552 bytes, SHA256
97611cd24f0bc73c67a7393b9def55cbea3e952d26ca1ecfeb99b1d0b6e5ecef.
This does not establish phone hardware support.

Local artifact storage downloads were measured at only a few tens of KiB/s.
Bulk downloads were stopped; actual artifact re-download and verification uses
the fresh CI runner instead. Small verification reports will accompany delivery.
The BusyBox matching Ubuntu source archives are locked from its official .dsc
checksums and included with the diagnostic image, together with Linux source
identity and the generated phone patch.

Configuration review found that the initial fragment conversion dropped Kconfig
negative assignments (`# CONFIG_... is not set`) as if they were prose comments.
That unintentionally retained other vendors' default ARM64 platforms and
expanded the cold build. Restore the original platform exclusions, assert the
absence of unrelated platform families in the final .config, and add a failing
test for accidental ARCH_MEDIATEK enablement. Stop the superseded oversized
build; this is a recipe correction, not a hardware workaround.

Build 39813227953 compiled Image, phone/reference DTBs and the complete configured
module set successfully (C build: 22m29.933s). Packaging then correctly rejected a
duplicate bin/busybox entry: this pinned Ubuntu binary includes `busybox` in its
applet list. Preserve its real file and skip only that self-link. The exact
binary/appet/archive preflight now runs before source compilation. CI now saves
compiler cache immediately after the build attempt, including packaging failures.
