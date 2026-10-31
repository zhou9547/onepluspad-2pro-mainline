# USB fixed firmware gate candidate, 2026-10-31

The owner prioritizes USB before the remaining peripherals. r214 proved only
GET AP_ENABLE17=0 and OTG_SWITCH18=0. Earlier physical rounds reached a real
xHCI/root hub before detach, but UCSI returned device/sink and no peripheral
partner/enumeration followed. This candidate addresses those firmware policy
gates. It has not established VBUS supply, physical enumeration or storage I/O.
Dual-band WiFi and the existing working peripheral paths remain regressions.

## Source and scope

The vendor reference is OnePlusOSS
android_kernel_modules_and_devicetree_oneplus_sm8750 at
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3, GPL-2.0-only.
oplus_hal_adsp.c lines1781-1814 initialize AP17, lines9333-9386 independently
set/get SWITCH18, and lines3010-3027/3082-3086 validate SET responses without
requiring a value echo. Header definitions bind owner32778, GET0x32, SET0x33,
AP17 and SWITCH18. VBUS_REGULATOR24, GPIOs and TYPEC_MODE22 are separate
paths; this candidate does not add those writes or an OEM fallback.

## Fixed, opt-in policy

The default built-in driver and regular desktop image remain read-only.
Only the targets experimental boot adds
qcom_battmgr.oneplus13_otg_lease=1; this exposes a root0600 fixed start/restore
attribute on the exact phone identity. The flag never starts a lease.
The installed RAM helper additionally needs an explicit --firmware-lease,
root, protected RAM marker and both experimental boot flags.

One boot-wide atomic latch permits one acquire, with no refresh/rebind retry.
The driver is built-in; a loadable build refuses store. Both baseline GETs
must equal0 before any SET. The120s delayed-work watchdog and wake hold arm
before possible mutation; a boottime deadline forbids late enable writes.
Ownership is recorded before each SET. The fixed sequence is AP1/GET1,
SWITCH1/GET1, then final AP1/SWITCH1 GETs. SET ACK is not an echo.
Restore performs SWITCH0/GET0 then AP0/GET0, then final AP0/SWITCH0 GETs;
only the final pair clears dirty ownership and proves restored.

Transport is serialized with normal battery traffic, with its own exact
completion. The first exact reply owns completion; late optional GET/SET
replies cannot acknowledge ordinary battery reads. Timeout, send error or
service loss permanently poison optional traffic for this driver instance.
UNKNOWN is terminal, never retried or relabeled clean. The removal path
drains work without holding its mutex and restores before releasing GLINK.

## Helper and time accounting

The fixed command subprocess budgets are start20s, restore15s, status3s;
start can need8 one-second transactions, and restore6. Killing a userspace
writer does not cancel kernel sysfs execution. These budgets include margin
but do not guarantee bounds on kernel mutex/send/scheduler stalls.

With an explicit lease, the peripheral wait defaults/maxes at45s. Its80s
work deadline begins before start, leaving40s of the120s watchdog period
for cleanup. The wait deducts diagnostic time, and a32s mount/read/unmount
probe runs only with at least32s work budget left. Without the lease, the
existing75s role-probe default remains. Firmware restoration runs in nested
finally even if DWC3 role restoration fails. After an attempted start,
only used1, terminal RESTORED2 or clean REFUSED4, dirty0/0 is accepted;
IDLE0 after rebind is insufficient evidence. Failed status reads produce
explicit unknown cleanup, with no blind retry.

## Evidence and remaining admission

The full Linux repository suite passes871 tests with5 skips; the phone
subset713 with1 skip. Shipped tests exercise the actual policy with GCC
ASan/UBSan,13 helper lifecycle controls, and22 release/sanitizer controls of
the actual kernel store/watchdog/remove header. An independent review ran
71 additional fault controls over the actual callback/transport, policy,
kernel scaffold and helper. The patch applies to the pinned kernel source
and the generated driver matches byte for byte. See
USB-LEASE-SOURCE-REVIEW-20261031.json. Full Actions compilation and exact
image readback are the next offline gates; no new phone boot occurred.

This is best-effort watchdog restoration, not a firmware lease/TTL or a
hard wall-clock guarantee. No transaction ID, nonpersistence promise, or
firmware reset-on-reboot guarantee was found. A SET can apply before ACK
loss; poisoning then leaves UNKNOWN and may prevent restoration. Kernel
failure or GLINK loss can defeat delayed work. Active reboot bypasses
devres cleanup; returning to Android is not a firmware-restore receipt.

A future source/image-bound combined round must require verified firmware
restore before normal Android return and have an explicitly reviewed
UNKNOWN recovery procedure. Existing r214 authorization/ledger is consumed.
USB gate success is separate from real Type-C partner, xHCI enumeration
and a bounded read from the owner's USB storage. Functional failure with
successful cleanup should continue later independent regression phases.
No flashing, partition writes, shutdown, or additional phone operation is
authorized by this source publication.
