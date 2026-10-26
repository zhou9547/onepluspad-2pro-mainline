# Phone RPC volatile file path

Run73 observed reverse-RPC write requests for these two exact names:

* `/mnt/vendor/persist/sensors/registry/registry/DIR`
* `/mnt/vendor/persist/sensors/cam_registry_dump.txt`

Bounded run74 then showed the same workload using two registry temporaries:

* `/mnt/vendor/persist/sensors/registry/fstempfile`
* `/mnt/vendor/persist/sensors/registry/parsed_file_list.csv`

Phone overlays0006/0007 add a default-off backend for those four names. The daemon only
enables it with `-W`; the common and Pad startup paths remain read-only. No host
writable descriptor or phone pathname is opened for mutation.

The bounded phone qualification service now passes `-W` explicitly. An older
archive without this option fails before attachment because the daemon rejects
the unknown argument. The service's 40-second runtime, single attach, no client,
clean-stop and fail-closed error gates are unchanged.

For a future bounded hardware diagnostic, the worker can select
`--diagnostic-ram-writes`. This mode still requires one successful attach, at
least three successful reverse invokes, a valid complete trace, a clean stop and
zero write refusals. It permits only bounded counts of classified missing-file
or unsupported-dispatch lines, records their counts without paths, and reports
`file_server_accepted: false`. Unknown errors, excessive counts, write refusals,
partial traces and unclean stops remain fatal. The normal mode retains the
strict zero-error acceptance rule.

The worker now records the service state before issuing its one stop. A
`systemd-run` startup error is retained as evidence while status, logs and trace
are collected; an already failed or early-exited unit is then rejected
explicitly. This closes the run74 path where `CalledProcessError` bypassed the
diagnostic summary.

Diagnostic output also carries up to64 SHA256 fingerprints of missing lookup
names. The hashes can be compared with saved vendor and request inventories
without copying private paths or file contents into public evidence.

Native ARM64 Actions40263745661 at
`19c7ea18ea2a6f87db0b400c1ca7a9bd300066ed` passes the expanded13 release,
13 ASan/UBSan and six Python checks plus the300-byte listener fixture.
Artifact12624744782 passes ZIP CRC, exact two-AArch64-ELF manifest and license
checks; runtime SHA256 is
`20ab0e426f023d0f97f2257643103b21aa99d56b8114ff1d93fbd206af2b9880`.
Fresh exact-rootfs QEMU-user RPATH/loader/`-W` startup still opens no device and
performs no ioctl. The expanded private rehearsal archive passes all931-destination
and real UID65534 read checks. These are offline results, not run75 eligibility.

Bounded run75 then completed its28-second service observation with a single
successful attach,2648 successful reverse invokes, active pre-stop state and a
clean stop. Android returned automatically in134.6s; all seven baselines
matched, and display/GPU/ordinary-user desktop regressions passed. The complete
daemon log had zero write-mode refusals. The diagnostic result still failed its
reviewed error bound because method33 (`frename`) was unsupported repeatedly
(436 classified unsupported/refused lines), alongside37 missing configuration or
OEM lookups. The captured failure tail contains no original registry-DIR or
camera-registry write refusal and no large-input cutoff.

Phone overlay0008 implements method33 for the bounded copy-on-write registry.
It admits only basenames below the exact persist sensor registry directory or
the exact camera registry path, atomically renames only RAM data, preserves
source handles, and refuses replacement of an active destination. Limits are512
in-memory files,16MiB aggregate,1MiB per file and64 handles. Host release and
ASan/UBSan tests pass; native ARM64 and a new source-bound review remain
mandatory. Run75 stays halted.

The open methods still require absolute registry paths. Only method33
canonicalizes a bare basename into this registry namespace, matching how the
sensor process composes temporary and final names.

Native ARM64 Actions40265238637 at
`a987c7b010c31a4c7a4cb603c8c916271cb38ebf` passes the method33 overlay and all
previous13 release/13 ASan/UBSan/six Python checks. Artifact12626485873 and a
fresh exact-rootfs QEMU-user link/CLI probe pass; runtime SHA256 is
`44a13f41801579e433f1aeb0f38382b8c3571c7b04344a8f8ed13ba7a5a4d6c3`.

Bounded run76 then passed the diagnostic stage: one attach,28s observation,
2573 successful reverse invokes, zero write refusals, zero unsupported/refused
dispatches, clean stop and no sensor/radio/audio stream. Android returned in
132.9s with seven matching baselines; display, GPU and ordinary-user desktop
also passed. The diagnostic still recorded37 classified missing configuration
or OEM lookups and intentionally reports `file_server_accepted: false`. A
verified owner PCB scalar is now staged privately in the RAM archive to close
the six known PCB path misses; its value and hash are not public artifacts.

## Data and handles

The backend holds at most four files in process memory. Each file is capped at
1MiB, aggregate storage at4MiB, and each read or write at64KiB. A read handle can first copy a bounded
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

Run74 also observed an incoming reverse request larger than the old256-byte
stack buffer. Overlay0007 moves request receipt to a separately allocated64KiB
buffer and retains a hard EMSGSIZE failure above that capacity. The listener
refusal fixture now sends a300-byte request.

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

Bounded run74 exercised the first backend on the phone. Android returned
automatically in107.7s and all seven baseline samples matched; display, GPU and
ordinary-user desktop regressions passed. The bounded log no longer showed the
original registry-DIR or cam-registry write refusals, or the six PCB-version
misses. It did reveal repeated writes to the two additional temporary paths and
a reverse request above256 bytes, which stopped the listener before a diagnostic
summary could be emitted. The service launch wrapper also lost its summary when
`systemd-run` returned the early failure. Run74 is halted and was not treated as
acceptance. The following overlay and launcher changes are fresh software work,
not a retry credential.

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
