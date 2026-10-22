# OnePlus 13 adaptation

Target: OnePlus 13 (dodge / SM8750), not OnePlus 13R/13T/13s or the Pad.

User authorization, 2026-10-22: implement in the user's fork, push an isolated
adaptation branch, run GitHub Actions, fix build failures and deliver artifacts.
The user will perform hardware tests later. No device operations, partition
changes or assertions of hardware success are authorized by this offline task.
Use Ubuntu with GNOME as the reference distribution. Preserve Android and defer
storage layout decisions until recovery inputs and device evidence are known.

Keep the existing Pad integration intact. Phone work lives in devices/oneplus13,
tools/oneplus13, docs/oneplus13 and its dedicated workflow. Do not use Pad stock
boot references, calibration, firmware or partition sizes for the phone.
Keep secrets, device identifiers, private keys and factory calibration out of Git.
Use the existing repository license and preserve third-party attribution.
AI-created commits must identify Codex as their author; never forge a human's
Signed-off-by or Tested-by. Compilation is only OFFLINE_BUILD_ONLY.

Before changing code read docs/oneplus13/STATUS.md and TECHNICAL-DEBT.md.
Update status, evidence and the next step before handing off.
