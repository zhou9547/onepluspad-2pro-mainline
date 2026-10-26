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

Nine C tests pass in release and ASan/UBSan on the host after the three phone
patches. The original builder explicitly lacks a destructor for its virtual
tree, so leak checking is excluded and recorded separately; invalid memory and
undefined-behavior checks remain active. Six Python source-recipe/archive and
artifact-environment refusal tests pass. Native ARM64 is still required before
runtime qualification, followed by actual phone-rootfs linking. Other untested
IDL families and writable-registry semantics are not accepted by this result.

`build-phone-rpc.py` builds just generic hexagonrpcd and libhexagonrpc from the
pinned original source and five unchanged patches plus three phone overlays.
The dedicated native ARM64 workflow runs both C variants, records input hashes,
and exports only the two ELF files and source/test/license evidence. It adds no
service/udev hook, ROM, private registry, DSP library or installer. Meson sees a
limited build environment so its recorded test logs do not inherit runner or
proxy credentials. No phone operation or sensor/DSP executable is run by the
builder. Ubuntu24.04 host-built ELF still needs exact Ubuntu26.04 rootfs CLI/link
verification; a successful build is not a working sensor system.
