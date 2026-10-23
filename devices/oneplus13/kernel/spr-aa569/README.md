# AA569 SPR2 profile and transaction planner

This GPL-2.0-only component is compiled into the isolated phone msm module for
API checking. There are no callers, MMIO, firmware loads, DMA submissions or
runtime hooks. It cannot enable SPR or the display. The default and touch DTBs
remain unchanged. Host tests use synthetic coefficients; private profiles are
generated on the owner's host only and must not be uploaded to Actions/Git.

The private v1 format is176 bytes, little endian: magic AA569S2 followed by NUL,
eight u32 header fields (version1, width1440, height3168, refresh120, wordcount34,
IEEE CRC32 of the payload, flags0, reserved0), followed by34 fixed u32 words.
Words are cfg17[4], cfg16[8], cfg13, cfg10, cfg15[16], PBA, opmode, two-LM mode1
and full-frame PU origin0. There are no arbitrary offsets, addresses or writes.
CRC detects accidental corruption, not authenticity or matching hardware.

The decoder checks exact size/magic/geometry/version, CRC, every field mask,
the investigated PenTile/2DAvg/YYGM control route and PBA consistency. It rejects
UDC/reserved bits. The planner retains the separate PBA direct, INIT REGDMA
and PU REGDMA paths, with bit25 preserved only at SPR_CONFIG. It does not
write the legacy cfg14 register0x54. Failed calls leave outputs unchanged.

Packing is derived from OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750
at d50b305f7da9e14715a25120a4ac7b1a4b8b97c3, display-drivers/msm/sde/
sde_hw_reg_dma_v1_color_proc.c (reg_dmav1_setup_spr_init_cfgv2 and its helpers).
The original helpers have already been checked independently against private
Android ARM64 conversion. No vendor binary, XML or private coefficient is here.

Before use, implement DSPP reservation, explicit panel requirement, all-pipe
preflight, UDC ownership rejection, powered/quiet execution, bounded REGDMA
completion and mappings retained until DMA stops, flush, disable and runtime
power-collapse restore. Native422 alone does not establish a panel SPR need.
Another panel's CPU-write startup path is not a substitute for this contract.
