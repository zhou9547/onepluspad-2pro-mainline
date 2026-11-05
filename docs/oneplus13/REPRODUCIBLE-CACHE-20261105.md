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

## Validation

Actions [42011681214](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/42011681214)
passes all six jobs for source
`6bc555f5100a9080fdf26c2b5bb72400c2b2f6f0`. Resources completed with the
repository package cache, and rootfs completed without the snapshot download
failure seen in earlier runs.

The four Actions archives were downloaded and matched their GitHub digests.
Independent image readback checked 41 complete-image checksums, 46 kernel
checksums, 15 Resources checksums, boot sections, FDT/initramfs/kernel,
SquashFS, ARM64 ELF files, 841 packages, runtime binding maps, privacy state
and default-off suspend policy.

- boot SHA256:
  `bb74d98aca34c249ed8b11390e10909081f5f3c8ec44d56a2d44ef2501ba29bf`
- rootfs SHA256:
  `23060c692b3a2a7c270f605d369894fbd2aaa67c23349ad7c2abbb89a802999e`
- delivery: `images/diagnostic-r280-20261105`

This is an offline and independently read-back image qualification. Physical
acceptance of this exact pristine pair remains a separate temporary-boot step.
