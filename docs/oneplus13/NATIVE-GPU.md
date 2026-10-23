# Independent Adreno 830 work package

## Evidence and scope, 2026-10-24

Saved owner runtime FDT has chipid0x44050001 / Adreno830v2 at3d00000.
Pinned platform7a81d184e309 has that exact ID in a6xx_catalog.c, selects
a8xx_gpu_funcs and requests gen80000_sqe.fw, gen80000_gmu.bin and gen80000_aqe.fw.
The original Erhai project enables the platform GPU and supplies its own zap
path. Reuse platform clocks, GMU, SMMU and speed-bin handling, not its signed zap.

The public sm8750-common vendor reference ca08912660e37ee1ee1652785c92a5c4b3efa131
contains those three firmware files and gen80000_zap.mbn. This is reference
availability only, not evidence that they match the owner's CN .501 system or
that the secure world accepts that zap. No reference binary is promoted or
distributed by this work package. Do not disable zap authentication or SMMU.

Prepare a fifth, GPU-only DTB. Display, touch, PCIe/WLAN and Bluetooth remain
disabled. The render driver stays modular and diagnostic init does not load it.
The pinned msm_drv.c defaults separate_gpu_kms=false; a future authorized
headless experiment must explicitly load msm with separate_gpu_kms=1. Merely
enabling the GPU node does not prove a render node will appear by default.
Inherited platform OPP/clock/power settings are reference candidates, not phone
electrical measurements. Owner-compatible firmware and real GPU rendering are
still required before any combined desktop candidate.

## Acceptance

Check actual compiled DTB chip ID, GPU/GMU/SMMU graph, private-free phone-specific
zap path, reserved memory and isolation. Reject wrong chip ID, foreign zap path,
missing SMMU and accidentally enabled display/radio controls. Build full ARM64
modules and inspect actual a8xx functions in msm.ko. Recalibrate against saved
phone stock inputs before host-only packaging.

Hardware acceptance needs a hardware renderer (reject llvmpipe/softpipe), exact
pixel comparisons, repeated runtime power cycles and over200 seconds without
GMU faults/hangcheck. Test real desktop/multiple contexts/video and GTK GL/Vulkan
separately. Current phone read-only permission does not authorize these tests.

Primary source: [pinned GPU catalog](https://github.com/yzddmr6/linux-sm8750-erhai/blob/7a81d184e3098624d4342d8f4eff5e23674bcc9f/drivers/gpu/drm/msm/adreno/a6xx_catalog.c).

## Actual compiled artifact

Actions39992904871/c2e659aaa062647a206c67edcc421f0fa9931f7a succeeded. Actual
artifact12518803835 is59797477 bytes, SHA256
230c9b9258b6c8cf69a8d8ff7e1e6e7bdeb2de2da7c44d0ba858557c4f8fdc80.
CRC,35 manifest files, seven AArch64/vermagic modules, exact source hashes,
compiled GPU graph/five controls and prior display/WLAN checks pass locally.
Actual msm.ko contains a6228-byte a8xx_hw_init function. The four previous DTBs
remain byte-exact. All five trees pass stock positive control, six overlays and
15 protected RAM banks. This is a compiled graph and driver, not rendering.
No signed GPU firmware or combined desktop image was added.

## Owner hash metadata after root confirmation

One independently reviewed,45-second/2KiB-capped SSH root query confirms UID0
and the same saved Android build. AQE/SQE/GMU sizes and SHA256 match the public
common reference; signed zap does not. No firmware binary was transferred and
no device mutation occurred. Do not package the unmatched reference zap.
Full firmware/authentication/rendering acceptance remains unverified. Prioritize
display/network/touch; software-rendered GNOME can precede hardware acceleration.

## Correct signed firmware recovered

Exact owner-build .501 OTA extraction40002870490 provides the matching signed
ZAP12088 bytes, SHA256a694df58b82343e58e52745da31c3b88e569a2eeae5e7755e0d9bf14d93f5046.
All four graphics files pass independent downloaded/file/owner equality checks.
firmware.py stages SQE/AQE/GMU under qcom/ and ZAP at the DTB's phone-specific
qcom/sm8750/oneplus/dodge/ path. The new GNOME rootfs embeds these four exact files.
The earlier public common ZAP mismatch remains a valid rejected reference.
No TrustZone authentication, GPU voltage/power or rendering test has occurred.
