# Phone Iris preparation

The pinned SM8750 kernel already contains the VPU3.5 Iris decoder and its
clock/power/ICC/IOMMU graph. The current phone image compiles `qcom-iris.ko`
but leaves its DT node disabled and module loading denied. The original Pad
also stages an Iris candidate; its firmware must not be substituted for the
phone's product-signed image.

The owner's C.93 `vendor.img:/firmware/vpu35_4v.mbn` is2417352 bytes, SHA256
`e1b2cb6de867893537fe6a1ffba312c2a2949402ca9892d393e2f40de255690a`.
It differs from the Pad's same-sized firmware. The saved phone FDT and the
qualified Linux tree both reserve8MiB at0x9c300000 for video, with no-map.
The first bounded r63 activation opens the firmware session without kernel faults;
actual pixel decoding remains unqualified. See the r63 evidence below.

`video-probe-dtb.py` prepares a future separate camera/video tree by changing
only the existing Iris status and firmware-name, after the camera derivation.
It preserves every other node/property, resource reference and memory reserve.
The firmware path is explicitly phone-specific. Tests check exact preservation
and reject an active/foreign core or altered memory range. The exact phone
firmware is now staged in the owner-authorized qualified data under
`firmware/qcom/sm8750/oneplus/dodge/vpu35_4v.mbn` and is hash-checked during
source-image packaging. `build-video-probe-boot.py` creates a separate manual
RAM candidate with the Iris node enabled and the same kernel/initramfs as the
desktop image. The default boot tree remains disabled and no video hardware is
auto-started.

Before a hardware round, stage only the reviewed phone firmware with provenance,
build and independently verify the alternative in Actions, then check firmware
authentication, one bounded linear-format decode, result frames, runtime suspend,
teardown and the retained desktop/radio/audio/sensor features together. A device
node or successful query alone must not be reported as decoding or VA-API support.

The next source-built runtime includes a static AArch64 V4L2 client and a guarded
manual coordinator. The only input is a generated905-byte AVC frame containing
four public synthetic color bars. The client waits for a stateful source-change
event, uses mmap queues, requests linear NV12, checks the returned timestamp and
visible luma pixels against all four bars, then stops both queues. There is no
software decoder fallback. Native/QEMU pixel-validator checks reject short,
invalid-stride, corrupted and blank output under ASan/UBSan; these are offline
checks, not hardware decoding.

The manual coordinator binds the live DT/resources, product firmware, module
dependency bytes, executable and fixture to the exact image. It enforces the
existing RAM/read-only-storage/absolute-deadline guards, requires idle camera,
SSC and WiFi, waits for runtime suspend and removes Iris afterwards. Real-device
activation uses the independently verified r62 awake recovery scope and a fixed
90s separate awake guard. r63 completed session setup and safe teardown, but its
client rejected the input buffer size before decoding. Idle and suspend recovery
remain separate tasks.

Secure-memory source review pins OnePlusOSS modules/devicetree commit
`d50b305f7da9e14715a25120a4ac7b1a4b8b97c3`. Its
`vendor/qcom/opensource/video-driver/driver/platform/sun/src/msm_vidc_sun.c`
selects firmware `vpu35_4v`, PAS9, a nonsecure start of0x25800000 and secure
nonpixel range0x01000000/0x24800000. `driver/vidc/src/firmware.c` derives SCM
protection arguments0/0x25800000/0x01000000/0x24800000 from that table, matching
the pinned mainline Iris VPU3 table. The original phone FDT IOVA partition and
firmware carveout are different address spaces; do not substitute their sizes
for the SCM protection arguments. Both fetched files were checked against their
Git blob IDs; SHA256 values are respectively
`b167da87eb103471edfe4ccd30e1c88cedd573e2718f948c0745150dc14b29df`
and `b8f28a1f5d9d54312584866bd2f95ec8ad2430dc9ec1018b3207604dbe1816e7`.
This source agreement alone does not establish firmware authentication or decoding.

## First hardware activation and allocator correction

[The r63 sanitized result](evidence/joint-video-r63.sanitized.json) records a
successful firmware session and clean teardown, but EOVERFLOW at input allocation.
The pinned iris_dec_bitstream_buffer_size formula uses the4K baseline even for
this small fixture:4096*2304*3/2/2 =7077888 bytes. The client's2MiB single-buffer
limit was too small. The corrected client uses the negotiated sizeimage, an8MiB
input ceiling, unchanged2MiB capture ceiling, and64MiB per-queue aggregate bound.
It logs actual granted count and QUERYBUF plane lengths. Offline release and
sanitizer tests exercise that real allocator, including partial-error unmapping.

The V4L2 [REQBUFS contract](https://docs.kernel.org/userspace-api/media/v4l/vidioc-reqbufs.html)
requires honoring the returned count; the driver negotiates buffer storage through
S_FMT/QUERYBUF. No allocation or successful open substitutes for verified NV12
pixels and timestamp. A new Actions image and retained-feature joint run are
required before accepting this fix or claiming hardware decode/VA-API support.
