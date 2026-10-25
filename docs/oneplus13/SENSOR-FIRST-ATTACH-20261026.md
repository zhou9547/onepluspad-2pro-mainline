# Bounded phone sensor-domain transport qualification

This review qualifies an optional single transport experiment, not a sensor
service or sensor stream. The working run68 candidate remains unchanged.
Radio, sound and CDSP stay isolated. No registry/data archive is needed for
one INIT_ATTACH_SNS ioctl followed immediately by local close. The separate
phone runtime archive remains undelivered and ineligible for live clients.

## Saved DT comparison

`review-fastrpc-contexts.py` resolves each IOMMU phandle, parses the controller's
parent bus cell geometry, translates nonempty ranges and compares controller
MMIO, SID/mask pairs, context indexes, memory attributes and VMIDs. Comparing
raw phandle numbers would be invalid. The saved phone and candidate ADSP trees
normalize identically: controller MMIO 0x15000000/0x100000, six contexts3..8,
12MiB reusable heap with4MiB alignment below4GiB, VMIDs22/37 and secure domain.
Nine tests cover changed controller/SID/heap/security, disabled ancestors,
truncated/unknown/duplicate contexts and translated/unmapped buses.

DT equality alone is not a hardware permission or DSP ABI acceptance.

## Pinned source comparison

Kernel7a81d184e3098624d4342d8f4eff5e23674bcc9f `drivers/misc/fastrpc.c`
SHA25686e0ce31b6129b419076f443eb886890c12a5b9ee18f8e56f5ad740f287cf9f7
and its UAPI header SHA2561b75dd9e95a2cda193cff7b9ba4a306642c9f6e1454bf99771b3a1e5862b1132
define INIT_ATTACH_SNS `_IO('R',8)`=0x5208, sensors PD2, init handle/method0
and one32-bit client ID. The pinned OnePlus vendor source tree
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3 uses the same sensors wire PD2 and
single32-bit TGID for attachment. Vendor PDR/shared-context recovery is not
assumed to exist in mainline. No retry or shared ADSP stop/restart is allowed.

Kernel-origin attach and release invocations each wait at most10seconds in
the reviewed source. User invocations may wait interruptibly without that
timeout; this experiment sends none. The original hexagonrpcd sends attach
before registering its reverse listener; this probe deliberately stops at
the transport boundary and never starts that listener or an SSC client.

IMPORTANT: `fastrpc_device_release` ignores INIT_RELEASE's RPC return value.
Successful local `close()` is not a DSP release acknowledgement. Never infer
complete teardown, registry service, sensor samples or calibration from it.

## Optional helper contract

`ram-sensor-attach-only.py` verifies RAM overlay, all physical blocks read-only,
recovery guard/timer, absent radio/sound/client activation, exact module/release,
zero dependencies and unchanged denial policy. It refuses any active udev rule
mentioning FastRPC/hexagonrpc/ssccli. It masks sensor client services in RAM,
records one attempt before the explicit module load and retains normal modprobe
denial. It verifies the secure ADSP character node's device number and DT ancestry.

A separately bounded worker issues one literal0x5208 ioctl, immediately closes
its local descriptor and records the actual return/errno and elapsed time.
No dynamic PD, DSP library, reverse filesystem, stream, axis matrix, unload or
restart is requested. The parent permits24seconds for the worker and12seconds
for termination/close; outer transport remains bounded. Any failure ends the
run and requests Android recovery; critical health or recovery failure halts
future hardware. The existing independent600second recovery remains active.

Nine Linux host tests cover the actual worker call sequence/error close and
qualification failures, masks-before-load, retained failure marker and unchanged
module policy. ARM64 Actions must pass before optional hardware execution.
This narrow milestone cannot be recorded as sensor adaptation complete.
