# Bounded phone reverse file-server qualification

run73 followed the successful150-test ARM64 and exact-rootfs real-UID/umask
sandbox/deadline40247176201. The old permission refusal is gone: actual phone
ODM configurations were opened through reverse RPC, with37 successful invoke
returns in the saved tail and clean service stop. Strict acceptance still
refused missing lookups and write requests. Android returned automatically in
134.0s with seven matching samples; platform regression passed, no streams or
flash/manual recovery. The single corrected-attempt ledger is halted too.

There were27 requested source-absent vendor-index names,20 containing a literal
# prefix;11 other missing OEM/board lookups, and two refused writes, including
the existing registry DIR and camera dump. Do not strip/alias # names, fabricate
data, discard errors or enable writes as a success shortcut. Passive Android
metadata for14 actually requested candidates found4 present and10 absent;
private values/hashes stay local. No library execution or phone write occurred.
The saved trace tail does not contain the initial attach/registry operations;
successful later invokes cannot reconstruct those missing facts.

The helper now emits bounded derived facts from its COMPLETE local trace before
any log-based refusal, preserving the strict failure. It reports error counts
without arbitrary paths/data, explicitly refuses write-mode warnings and checks
private-copy/module-policy/client postconditions even on rejected service exit.
The original rpcd_builder maps registry with a trailing slash; its trace match
accepts that exact directory with or without the slash, rejects neighboring
names, and remains separate from proof of registry use or sensor data. These
offline diagnostic improvements do not qualify another hardware attempt. First
review read-only virtual-FS/write ABI, actual OEM DSP inputs and board mapping;
no dynamic DSP ELF or SSC/iio client has been approved here.

Offline follow-up40246612604 passed148 native ARM64 tests and ordinary exact
rootfs handoff, but the expanded assembled-rootfs observer hit its old180second
emulator deadline at180.806s, immediately after native handoff selftest180.290s.
The new sandbox had not reached its success marker; no sandbox exception or
phone result was observed. This is a failed offline gate, not evidence that
the permission fix passed its integration test. The expanded dummy-virt-only
HTTP observer now gets300seconds, while the original fixture remains180 for
the ordinary check; phone runtime/initramfs deadlines and SquashFS stay
unchanged. Two tests reject phone/nonmatching installer inputs and constrain
the rewrite to the sole explicit emulator fixture. The VM must still prove
the real UID/umask read checks and automatic deadline/reboot before hardware.

run72 update: initial native146 tests and both QEMU/deadline jobs passed at
Actions40245671869, but the phone rejected executable traversal under UID65534.
The delivery shell's umask077 made newly created root-owned parents0700;
strace could not stat hexagonrpcd. Platform regression passed, Android returned
in101.9seconds with seven matching samples, and further hardware is latched.
The exact saved helper reproduces this failure on the host. The original
synthetic sandbox did not exercise installation under that umask.

The correction explicitly chmods only new parents0755 and refuses inaccessible
existing parents without changing them. Two new unit tests cover both cases.
The emulator now invokes the actual installer under umask077 and requires real
UID65534 reads of public synthetic binary and0640 registry paths. This tests
the previously missed installer/sandbox boundary, still without real RPC or
private inputs. Revised ARM64/QEMU results are required before another review.

run71's single INIT_ATTACH_SNS ioctl returned0 and the local descriptor closed
in approximately0.001seconds. Display/GPU/ordinary-user desktop/platform and
final health passed; Android returned automatically in104.6seconds with seven
matching baseline samples. It did not start a listener, deliver registry data
or request samples. Kernel release ignores the remote release status; local
close does not prove a DSP teardown acknowledgement.

The next proposed milestone reuses the original pinned hexagonrpcd, its narrow
property shim, separate vendor/ODM mappings and phone-specific saved inputs.
The five generic ARM64 ELF files have an existing native build/test artifact;
the phone's userspace ABI-reference library hashes match its pinned references.
No Pad mount matrix, claimed sensor identity, service/udev hook, firmware or
kernel module is delivered in this private runtime archive. Its923 data files
include the unit's original registry and saved socinfo. No private bytes or
manifest are published. Loading files is not evidence that calibration is used
correctly or sensor axes/accuracy are accepted.

`ram-sensor-fileserver.py` binds the module/release/policy, corrected attach
guard, archive, manifest and trace executable by hash. It validates every
archive path, size, byte hash, mode, ELF architecture and all three exact data
mapping links before extraction. No target may already exist, use a symlink
ancestor or collide with another member's parent. It writes only the RAM
overlay. Exact bytes are checked before the only attachment and after service
exit; any changed data fails qualification.

The existing unit-denial policy stays intact; automatic sensor clients are
RAM-masked and one attempt marker precedes the sole explicit module load.
The file server runs as UID/GID65534, without capabilities, with read-only root,
private networking, AF_UNIX only and one allowed FastRPC character device.
No SSC/iio client or dynamic PD is launched. There is no restart loop. A28second
observation has a40second systemd runtime cap and12second stop cap; outer host
staging and both independent RAM recovery timers remain in force. A stop or
health failure requests immediate Android recovery; no ADSP restart/unload is
used as a retry. This does not make a timeout equivalent to guaranteed remote
teardown.

The actual daemon is wrapped with the existing pinned ARM64 strace, recording
only openat/ioctl/close and numeric ioctl arguments, never dereferencing RPC
payloads. Raw logs remain private. Acceptance requires one successful attach,
successful invoke returns, actual config and registry mapping opens, no logged
unsupported/refused/error operation, clean service stop, retained policy and
unchanged private data. Mere process liveness or an ioctl return cannot prove
these file-service conditions. Sensor samples, axes, accuracy and stream
shutdown remain separate gates.

Nineteen Linux unit tests cover byte/permission/architecture/hook/mapping and
destination refusal, exact single attach trace, failed opens, bounded sandbox
properties, early exit, close timeout and unsupported reverse methods. The
assembled-rootfs QEMU observer additionally exercises the exact transient-unit
builder with a synthetic non-RPC process, UID/capability checks, refused root
writes, allowed state output and clean stop. It checks dummy-virt identity and
cannot run on a phone. That sandbox test does not execute real strace, an
ioctl or any proprietary input; separate exact-rootfs link/CLI probes cover
the real generic runtime. ARM64 and QEMU qualification must pass before a
phone file-server run is eligible.
