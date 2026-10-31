# Owner resumes adaptation, 2026-10-31

Owner clarification in the current chat: 5 GHz already works, including the
5240 MHz r191 control channel. Treat both WiFi bands as preservation/regression
baselines, not an unfinished RF adaptation target. Current work prioritizes
the remaining GNSS, NFC, camera and USB goals in combined physical rounds.

The current chat requests continued adaptation with 5 GHz WiFi first, then
the original project's integration order. Preserve working features, combine
several reviewed targets in one physical round, publish meaningful progress,
and confirm a successful Actions image at completed milestones rather than
on every small edit. Builds and offline tests are resumed. This does not
renew a historical phone-test ledger, deadline or shutdown authorization.
A physical round still needs its fresh source/image-bound plan and current
chat start confirmation. No flashing or persistent installation is permitted.

# Owner finishes this round for archive and shutdown, 2026-10-31

The owner requests completing the current modifications, committing code,
compiling, then updating C:\Users\LYC\Desktop\temp\op13-linux with the
current and Linux-17 chat records and all needed local material. Move existing
task material into that archive rather than creating another full copy.
After all required work and verification, shut down this computer once without
another confirmation. This one-time shutdown authorization is not reusable.
The r191 phone round has ended and its ledger is consumed. Any later phone
round needs fresh per-round approval; do not reuse old approvals or time windows.

# Owner resumes compilation and joint testing, 2026-10-29

The newest owner instruction resumes builds and testing and offers human assistance. This supersedes the source-only pause below. Preserve temporary RAM boot only, source-bound joint plans and the existing 19:00 Asia/Shanghai device deadline unless explicitly extended.

# Current owner instruction, 2026-10-29: source changes only

The owner now requests completing the remaining source/configuration work before
any further compilation or testing. Do not start builds, workflow dispatches,
unit/synthetic tests, emulator tests or phone operations until the owner resumes
that phase. Earlier unattended phone windows do not override this newer pause.
Read-only source inspection, source generation, editing and publishing reviewed
source commits without CI dispatch are permitted. Keep uncompiled and untested
candidates explicitly separate from hardware acceptance; do not claim all
adaptation difficulties are solved by adding unverified code.

# Current owner authorization, 2026-10-27

The owner explicitly authorizes uploading the qualified firmware and calibration
needed to build the complete RAM image in Actions. Exclude WiFi credentials,
network identities, device serials/MACs/IMEIs, tokens, private keys, personal
data, raw private records and unreviewed datasets. Publish only the scrubbed,
hash-bound `devices/oneplus13/qualified-data` allowlist and preserve provenance.
This supersedes the older blanket calibration exclusion below. The owner also
requests QEMU be optional, disabled by default for unchanged qualified inputs.
Historical authorizations below are a record, not a revocation of later direct
owner instructions. Never flash, repartition or persistently install the phone.

# OnePlus 13 adaptation

Target: OnePlus 13 (dodge / SM8750), not OnePlus 13R/13T/13s or the Pad.

User authorization, 2026-10-22: implement in the user's fork, push an isolated
adaptation branch, run GitHub Actions, fix build failures and deliver artifacts.
The user will perform hardware tests later. No device operations, partition
changes or assertions of hardware success are authorized by this offline task.
Use Ubuntu with GNOME as the reference distribution. Preserve Android and defer
storage layout decisions until recovery inputs and device evidence are known.

User authorization, 2026-10-23: the owner's network ADB endpoint may be used
with existing root for READ-ONLY evidence collection. Every command must select
that explicit endpoint (kept only in private local records). Save evidence only
on the host. No push, device-side files, remounts, setprop, service control,
input injection, firmware commands, reboots, unlocking or partition writes.
This overrides the earlier prohibition on device queries only; booting a test
kernel and any operation that changes the phone remain unauthorized.

Keep the existing Pad integration intact. Phone work lives in devices/oneplus13,
tools/oneplus13, docs/oneplus13 and its dedicated workflow. Do not use Pad stock
boot references, calibration, firmware or partition sizes for the phone.
Keep secrets, device identifiers, private keys and factory calibration out of Git.
Use the existing repository license and preserve third-party attribution.
AI-created commits must identify Codex as their author; never forge a human's
Signed-off-by or Tested-by. Compilation is only OFFLINE_BUILD_ONLY.

Before changing code read docs/oneplus13/STATUS.md and TECHNICAL-DEBT.md.
Update status, evidence and the next step before handing off.

Owner instruction, 2026-10-23: before writing a workaround, first inspect the
original Pad project and public/community/vendor solutions. Reuse appropriate
implementations after checking SoC generation, panel identity, bpp conventions,
kernel APIs and license/provenance; do not copy another board's calibration.
The owner later provided a slow SSH access method. The existing read-only
device restriction remains in force. Limit any necessary queries to small,
bounded text output and avoid phone-to-host/host-to-phone file transfers.
Keep the endpoint and credentials out of Git and public artifacts.

Owner confirmation, 2026-10-24: SSH has root; verify it and perform only the
bounded firmware metadata reads already described. Review the single command
independently before connecting. This adds no authorization for binary phone
transfers, writes, reboot, experimental kernel boot or flashing.

Owner priority, 2026-10-24: first make native display, networking and touchscreen
usable and complete the path into GNOME. Defer audio and secondary peripherals.
The desired eventual flashable system does not revoke the phone read-only rule;
prepare concrete build/test inputs without flashing or repartitioning the phone.
