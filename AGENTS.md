# OnePlus 13 adaptation

Current owner instruction, 2026-10-24 (takes precedence over historical records):
continue porting OFFLINE. Inspect the original project and vendor references,
complete theoretical checks and record passed/blocked evidence before proposing
another hardware test. Do not use the phone for exploratory debugging. This
phase authorizes no ADB/Fastboot operations, reboot, RAM boot or flashing.
The owner explicitly approved uploading the reviewed public-source changes to
an isolated branch of zhou9547/onepluspad-2pro-mainline and using GitHub Actions
for ARM64/QEMU offline builds. This does not authorize hardware testing.

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
