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
