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
PAS9 authentication and actual decoding remain untested.

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
