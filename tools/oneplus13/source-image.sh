#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only
# Fresh source builds only. No Actions run IDs or old binary image inputs.
set -euo pipefail
cd "$(dirname "$0")/../.."
case "${1:-}" in
  kernel)
    bash tools/oneplus13/build.sh
    python3 tools/oneplus13/verify.py --artifacts out/oneplus13 --qemu
    ;;
  rootfs)
    sudo bash tools/oneplus13/rootfs.sh
    sudo python3 tools/oneplus13/verify-rootfs.py out/oneplus13-rootfs-artifacts --report out/oneplus13-rootfs-artifacts/download-verification.json
    ;;
  mesa)
    readarray -t pin < <(python3 -c 'import json; p=json.load(open("packaging/mesa/source.json"));print(p["source_url"]);print(p["sha256"])')
    mkdir -p cache
    curl --fail --location --retry 2 -o cache/mesa.tar.xz "${pin[0]}"
    printf '%s  %s\n' "${pin[1]}" cache/mesa.tar.xz | sha256sum --check -
    python3 tools/build-mesa.py --source-archive cache/mesa.tar.xz --profile desktop --output out/mesa-desktop --jobs 4
    python3 tools/package-mesa.py --build-output out/mesa-desktop --output out/mesa-debs
    ;;
  assemble)
    sudo python3 tools/oneplus13/assemble-source-image.py --base out/oneplus13-rootfs-artifacts --kernel out/oneplus13 --mesa out/mesa-debs --output out/oneplus13-source-image
    sudo python3 tools/oneplus13/desktop.py --source-build --kernel out/oneplus13 --rootfs out/oneplus13-source-image/rootfs.squashfs --output out/oneplus13-source-desktop --qemu
    ;;
  *) echo 'Usage: source-image.sh {kernel|rootfs|mesa|assemble}' >&2; exit 2 ;;
esac
