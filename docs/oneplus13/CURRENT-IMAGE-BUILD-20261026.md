# Current OnePlus 13 image build

The build branch is based on the complete public `oneplus13-bringup` tree and
overlays the latest public platform handoff files. The earlier platform-only
overlay lacked kernel build inputs, so it is retained as a failed qualification
attempt and is not used as this branch's parent.

The branch targets the same public components exercised by the owner-tested
run88 RAM image:

- kernel source commit `7a81d184e3098624d4342d8f4eff5e23674bcc9f`;
- kernel integration artifact `1f5c1128d42a62244bef9974e58cfe07adf29f7d`;
- Ubuntu GNOME desktop rootfs artifact
  `oneplus13-desktop-rootfs-de8eef9ca4d94940e6edb63f26a1dcd9d0bed7b2`
  from run `40068689660`;
- assembled rootfs SHA-256
  `64930aeb440de2ee4e0643c632cd4350b700ae59421985caa06056a0704a90c1`;
- assembled rootfs size `471007232` bytes.

`oneplus13-current-image.yml` runs the public offline gates, downloads those
exact pinned public artifacts, checks kernel, modules and rootfs hashes and
sizes, and boots the exact SquashFS in QEMU.

The `oneplus13.yml` and `oneplus13-rootfs.yml` workflows independently compile
the kernel and rootfs from source at this branch. The platform handoff pipeline
exercises exact component assembly.

Proprietary phone firmware, calibration, FDTs, keys, WiFi credentials, device
identifiers and private run records are absent. This public branch builds the
reproducible public image components; producing a per-unit RAM image still
requires owner-supplied private inputs locally.
