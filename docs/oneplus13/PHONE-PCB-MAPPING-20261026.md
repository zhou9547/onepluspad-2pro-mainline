# Phone PCB read-only mapping and offline RPC sanitizer fixes

run73 requested `/proc/oplusVersion/pcbVersion`, which the original virtual
filesystem did not expose. A bounded passive Android query confirmed that the
file exists and saved its small scalar privately. Nothing in the public patch
contains that value, calibration, a device identifier or a Pad substitute.

The supplemental phone-only patch maps that single virtual file to
`<device-root>/board/pcbVersion` through the existing read-only mapped backend.
An absent input stays ENOENT. It does not expose host `/proc`, add a write API,
change the original five patches or change the shared Pad recipe. Synthetic C
tests check missing/exact data, EOF/seek, neighboring names and unrelated host
proc/traversal refusal. Providing this file alone does not qualify a sensor
stream or resolve run73's other missing lookups and refused writes.

The new dedicated builder also tested the original RPC code with ASan/UBSan.
The existing misaligned output fixture exposed an unaligned uint32 wire-size
store; use a local little-endian word and memcpy, retaining exact encoded bytes
and checking four destination alignments with canaries. The original packed RPC
fixture then exposed native pointer loads immediately after a uint32 length;
use byte copies and identical cursor sizes for the packed in/out descriptors.
The ioctl test double also called memcmp/memcpy with null pointers for a valid
zero-byte argument; skip only those zero-byte test accesses. Sanitizer checks
stay enabled. These findings are host reproductions, not claims that they caused
a previous phone failure. The original failure logs remain local evidence.

The first three overlays passed nine C tests in release and ASan/UBSan on both
the host and native ARM64 (Actions40250963720). The original builder explicitly lacks a destructor for its virtual
tree, so leak checking is excluded and recorded separately; invalid memory and
undefined-behavior checks remain active. Six Python source-recipe/archive and
artifact-environment refusal tests pass. The fourth overlay described below
passed native Actions40252529300 and exact phone-rootfs CLI/link checks. Other untested
IDL families and writable-registry semantics are not accepted by this result.

`build-phone-rpc.py` builds just generic hexagonrpcd and libhexagonrpc from the
pinned original source and five unchanged patches plus four phone overlays.
The dedicated native ARM64 workflow runs both C variants, records input hashes,
and exports only the two ELF files and source/test/license evidence. It adds no
service/udev hook, ROM, private registry, DSP library or installer. Meson sees a
limited build environment so its recorded test logs do not inherit runner or
proxy credentials. No phone operation or sensor/DSP executable is run by the
builder. Ubuntu24.04 host-built ELF still needs exact Ubuntu26.04 rootfs CLI/link
verification; a successful build is not a working sensor system.

## Input type sequences: preserve the original wire contract

The original golden-wire test already covers TYPE_SEQ after a TYPE with the same
descriptor index. It hides a real bug: TYPE_SEQ never selects its own inner type,
so sequence-first uses an uninitialized pointer and differing indices reuse the
previous type. A private draft refusing both input and output sequences failed
that unchanged original test and was rejected before publication or phone use.

The fourth phone patch selects and validates the input descriptor, advances past
its metadata buffer for subsequent arguments, and makes zero-count sequences
consume no metadata in allocation/encoding/freeing. Buffer counts stay wide until
the scalar's eight-bit limit is checked before allocation. Output TYPE_SEQ has no
validated implementation and is refused before consuming pointers or ioctl.
No new output ABI is claimed.

The added real C mock-ioctl test checks exact bytes and buffer ordering for a
sequence first, different indices, consecutive sequences, a following blob,
fixed-blob structs, zero count and invalid descriptor/count refusal. All original
tests remain unchanged. Ten C tests pass in release and ASan/UBSan on the host;
the uninitialized-inner-type warning is gone. This is not exhaustive IDL or
allocation-failure validation, and does not remove the hardware/registry holds.
Standard GPL/LGPL license text and contributor attribution accompany artifacts.

Native ARM64 Actions40252529300 validates commit
`c93d2a9d7f88513ad0f256af7c0e616fd514aab9`: ten release plus ten ASan/UBSan C
tests and six Python recipe tests pass. Downloaded artifact12621352875 passes
ZIP CRC, manifest hashes and the two AArch64 ELF checks. Runtime archive SHA256:
`4469edf223632c8e0c341ca559381a4ad807bdc38b97e79ab181f9b4cf47ba13`.

In a fresh extraction of the exact phone Ubuntu26.04 rootfs, the normal RPATH
loads the new library and daemon `--help` returns the original usage/exit4.
A separate loader report resolves the intended new library; the help syscall
trace opens no device and issues no ioctl. This is a host QEMU-user linking
probe, not a DSP/file-service test. The baseline sensor runtime and phone
candidate were not replaced. run73's missing OEM libraries and writable-registry
ABI remain unresolved, and its hardware stop state is retained.
