# Camera teardown and fallback acceptance, 2026-10-31

The unattended combined-runner audit found three reproducible userspace defects.
The CAMSS probe retry rewrote the global kprobe table and did not enable its
events. It now refuses existing reserved probes, enables each owned event,
and disables/deletes only its own events while reporting cleanup failures.
Function-tracer setup and teardown now attempt every restoration, report errors,
and refuse a tracer or filter already owned by another user.

A real validated sensor frame from RDI1/RDI2 was rejected by the primary
RDI0 return code. Acceptance now considers that validated sensor fallback.
The separate TPG file cannot qualify a real sensor frame. Module-unload or
media-inspection timeouts no longer prevent policy restoration or the remaining
cleanup attempts. A failed cleanup is reported as failed, never accepted.

The original Pad/reference trees have no equivalent userspace camera capture
helper. The existing Linux kprobe reference in CAMERA-TRACE-CONTINUATION-20261031.md
documents per-event enable and selective deletion. No power, CCI timing, C-PHY,
firmware, device tree, or sensor register change is made on speculative evidence.

Offline Linux camera suite: 26 tests pass, including additional cases for
probe retry ownership, failed function setup/restore, actual RDI acceptance,
TPG rejection, continued unload after timeout and media-inspection timeout.
Failed exits and short/absent frames cannot qualify. Each attempt removes its
old output first; residual data from a failed attempt never qualifies.
Insertion ownership is now recorded before invoking modprobe/insmod. A timeout
or failed insertion can leave a registered module; teardown must still inspect
and unload that attempt. Modules already present on entry are not taken over.
Three regressions cover normal and debug insertion failures and preexisting
modules. This retains the same dependency order and reviewed module selection.
This is diagnostic and acceptance correctness, not real-frame hardware success.
The latest physical evidence remains r191: CCI initialization timeout -110.

5 GHz WiFi remains qualified historically at 5240 MHz; preserve both bands.
GNSS real fix/start/stop, physical NFC tag, real camera frames and USB physical
I/O remain open. Current unattended authorization is recorded privately;
no physical operator actions can be requested or counted as passed.
Any new boot still needs a fresh reviewed exact-image plan and unused ledger.
No phone operation has been performed for this correction.
