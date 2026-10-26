# Phone RPC volatile file path

Run73 observed reverse-RPC write requests for two exact names:

* `/mnt/vendor/persist/sensors/registry/registry/DIR`
* `/mnt/vendor/persist/sensors/cam_registry_dump.txt`

Phone overlay0006 adds a default-off backend for those names. The daemon only
enables it with `-W`; the common and Pad startup paths remain read-only. No host
writable descriptor or phone pathname is opened for mutation.

## Data and handles

The backend holds at most two files in process memory. Each file is capped at
1MiB and each read or write at64KiB. A read handle can first copy a bounded
snapshot from the existing virtual filesystem. W and A create an empty memory
copy; A then appends. R, RB, W, WB, A and AB are accepted for these names.
Other modes, neighboring names, embedded NULs, traversal and unsupported search
variables are refused.

At most16 handles are live. Their positive 32-bit values use a namespace that
does not overlap VFS indices0..255 and include a generation number. Closing one
handle does not invalidate another. Reusing an old generation is refused.
Multiple handles have independent positions but observe shared file contents.
Seeking permits only offsets from0 through the current length, so sparse files
are not invented.

A failed growth or allocation leaves the previous bytes intact. Append resolves
its position at each write. Deinitialization releases all handle state and both
file allocations.

## ABI and preallocation

Method5 follows the pinned Qualcomm `apps_std` IDL at
`a56e9d4de3614a8d8f4b0e15ff561350c4b686e3`: one 32-bit handle, one byte
sequence, and two 32-bit primary outputs for bytes written and EOF. The earlier
static review of the saved phone `libadsprpc` dispatcher fixed the method index,
scalar shape, eight-byte input/output primary values and result layout. The
Android library is not executed.

The generic listener now has an optional method preflight callback. For a RAM
read this checks the live handle and64KiB limit before `alloc_outbufs4`, closing
the path where a large output request would otherwise allocate first. Non-RAM
handles retain their existing read path.

Fread, fwrite, fseek, fflush and fclose recognize the reserved namespace.
Outputs are cleared before validation. Normal-file writes and mapped-file stat
requests remain unsupported instead of reporting stale snapshot metadata.

## Verification

Fresh host build v18 passes13 release and13 ASan/UBSan C tests plus six Python
recipe checks. The exact wire test covers seeded read, write, close, flush,
append, independent cursors, cross-handle readback, failed-write preservation,
embedded NUL and neighboring paths, unterminated and traversal names, oversized
write/read-before-allocation, invalid seek, stale handles and cleanup.

The storage fixture separately passes release, ASan/UBSan and LeakSanitizer with
default-off behavior, capacity boundaries, injected ENOMEM, generation
exhaustion and final cleanup. The complete suite leaves leak detection disabled
because the original root-tree builder, not this RAM backend, has no destructor;
the full wire fixture was also run with leaks disabled and produced no ASan/UBSan
finding.

Earlier generated candidates failed in sequence on a repository-only file in the
source patch, an undeclared builder variable, a test call arity, wrong fixture
path, uninitialized error output, and an incorrect EOF assertion. Each output is
retained privately. None was published, installed or used for a phone boot.

Native ARM64 Actions40260814820 at
`8a724331f292c40c03a7821698212d161ed9f884` passes the same13 release,13
ASan/UBSan and six Python checks. Artifact12624705085 passes ZIP CRC, the exact
two-AArch64-ELF manifest and license checks; runtime SHA256 is
`9fe629152041e9a83b8a6ad7b9c9d328b9c7ca2f8273dbb0913a91a8b7ac1cf9`.
A fresh extraction of the exact phone rootfs system libraries passes QEMU-user
normal-RPATH startup, loader resolution and `-W` usage reporting. Its trace opens
no device and performs no ioctl. The baseline runtime and phone images were not
replaced.

This work does not qualify reverse writes on a phone, sensor streams, CHRE
mapping, missing OEM data or the halted run73 acceptance. No run74 plan exists.
