# Reproducible build cache r280

The Ubuntu snapshot service is authoritative for signed package indexes and
dependency selection, while individual pool files can return HTTP 500, 502 or
503 independently. OnePlus 13 builds now restore the exact signed indexes and
previously resolved ARM64 packages from a pinned repository cache.

Cache tag: `cache-oneplus13-r280`

Cache commit: `d5c6fbbe9acc5084b556d9f4b770b026b2d396ce`

The tag stores a manifest under `cache/oneplus13/r280`, safe metadata files,
and 21 content chunks under `cache/oneplus13/r280/chunks`. Only regular files
and directories are accepted. Every archive, chunk and source file has a
recorded SHA256 and byte size. Restored package caches retain their ownership
marker and are rehashed by the package prefetch tool before use.

The cache contains:

- Ubuntu base 26.04.1 ARM64 and the three locked Resources source files.
- Signed list snapshots from `20261020T000000Z` and `20261024T000000Z`.
- All 768 packages selected by the previously accepted diagnostic rootfs
  APT plan.
- The 469 unique ARM64 packages needed by the Resources bootstrap and build
  dependency plans.

Actions automatically runs:

```text
python3 tools/oneplus13/repo-cache.py restore sources apt-lists resources-debs
python3 tools/oneplus13/repo-cache.py restore sources apt-lists rootfs-debs
```

If the repository cache cannot be downloaded or any byte differs, the build
fails closed. The original snapshot and official archive fallbacks remain
available but no unverified file enters packaging.
