# Batched RPC preparation: offline evidence and remaining holds

The owner requests multiple adaptation targets to be prepared together before
one joint RAM acceptance. This batch covers volatile file semantics, phone wire
ABI, bounded service error cleanup, and an exact read-only camera input. It has
not been delivered to a new RAM session and does not qualify a sensor stream.

## Source and verification

Runtime source commit: `ca18be3c271ee12573a1d6847b8f6c5069f0bd78`.
[Native ARM64 Actions40270669480](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40270669480)
passed14 release C tests,14 ASan/UBSan C tests,6 builder Python tests and36
bounded-service Python tests. Fresh pinned-tar WSL v28 passed the same C suite.
Full-suite leak checking remains excluded because the upstream root tree lacks
a destructor; do not describe this as a full leak-check pass.

Artifact12627952266 passed ZIP CRC, licenses, the exact two-AArch64-ELF runtime
inventory and hashes. Runtime archive SHA256:
`a87e394ec174c6b648e7f6869b9d1c8abf1625c363b7f4f2f38a5c104a5e036d`.
Fresh exact Ubuntu rootfs QEMU-user RPATH, loader and CLI probes passed, with no
device open/ioctl in the help trace. This is a link/CLI check, not a real RPC or
sensor execution test.

## Changes checked together

- Overlay0009 fixes offline-reproduced snapshot resurrection after rename and
  name-table exhaustion after missing-source rename requests. Bounded tombstones
  hide the immutable source; full tables and busy destinations refuse before
  changing names or bytes. It also fixes append-to-missing-file indexing,
  failed-seed cleanup, negative errno conversion and signed IDL seek offsets.
- Saved phone ELF dispatch review pins35 instructions for method33 rename and
  method9 seek, including three-input/no-output rename, length/terminator guards,
  and sign extension into libc fseek. The saved library was not executed; this
  does not verify every apps_std method.
- Service tests cover nonzero systemctl is-active results, failed pre-stop
  queries and launch timeouts without skipping the stop request. Current
  unsupported-mode messages are counted as write refusals even in diagnostics.
- Overlay0010 maps only the exact camera metadata filename from an optional
  staged file. Missing input stays ENOENT; the host persist directory is not
  exposed and the input is outside the RAM writable namespace. Synthetic binary
  tests cover NUL bytes, EOF/seek, neighbors/traversal, actual wire readback and
  write-mode rejection. No camera client or sensor stream is started.

The private input was copied passively from Android, matched the previously
saved inventory and preserved all seven baseline samples. It remains local;
neither its bytes nor its per-file hash is included here. The private delivery
archive passed the actual helper parser, umask077 installation and real
UID65534 reads of930 regular files, including925 data files; all933 destinations
are absent from the exact rootfs. The previous924 data files are unchanged.

## Limits and next joint acceptance

Run77 remains the latest RAM session: automatic Android return and seven matching
baseline samples, successful bounded service diagnostic, then a stale private
harness count assertion. Its stop latch and every earlier latch are retained.
The new camera mapping has not been checked on the phone; do not reduce run77's
observed31 missing lookups to30 on paper.

All27 absent config requests occur literally in stock json.lst,20 with a '#'
prefix. The DSP parser's comment semantics are not established; keep stock bytes
and missing-file errors. Qualcomm's oemconfig ENOENT logging exception does not
prove this phone feature optional or operational. TPPE/CHRE registration,
bounded dynamic loading/release, effective RF/SAR policy, and audio calibration,
protection and backend routing remain separate unresolved gates.

Any later source-bound joint RAM acceptance must include the new reviewed
targets plus display/GPU, ordinary-user desktop, input inventory, battery and
platform health, automatic Android return and all seven baseline samples.
Unqualified RF, audio, sensor streams, haptics, suspend and USB role changes stay
disabled. No flashing, partition change or persistent installation is included.
