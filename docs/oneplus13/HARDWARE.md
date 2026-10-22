# Hardware evidence and reuse boundary

No evidence below was collected from the user's physical phone. Hardware
acceptance requires its stock FDT, stock image metadata and actual runtime tests.

| Area | Pinned source evidence | Implementation / gap |
| --- | --- | --- |
| SoC | Erhai kernel 7a81d184e3098624d4342d8f4eff5e23674bcc9f, sm8750.dtsi | Reuse platform clocks, interconnects, SPMI, USB PHY and UFS drivers |
| Board regulators | index986 OnePlus-13-WIP 1f2047e8663eda76c8b172fd3e040e3b3fa17950 | Attributed phone regulator declarations, not Pad board values |
| USB | Same phone DTS: eUSB repeater L15B/L5B, HS PHY L2D/L3G, QMP L3G/L2D | Adapt old wrapper labels to the newer flat usb/usb_hsphy node layout; device role only |
| UFS | Same phone DTS: reset215, L17B VCC, L1D VCCQ, PHY L1J/L3G | Driver built in; RAM init makes each discovered disk read-only and does not mount it |
| RAM | Same phone DTS, low bank e3720000..ff800000 and secure carveouts | Conservative fallback; actual bootloader memory fixups and capacity unverified; D01 |
| Display | OnePlusOSS d50b305f7da9e14715a25120a4ac7b1a4b8b97c3: dodge display overlay lists AA545, BF262, AA569 EVB/EVT/production | No single panel can be selected for an unidentified phone; inherited framebuffer only, D02 |
| Touch | Same official revision: tp/dodge-oplus-tp-23821.dtsi declares S3910, 19 MHz SPI, IRQ162/reset161, L4B and PM8550VS_J GPIO3 | Vendor framework driver needs a real mainline port; a compatible string alone is insufficient |
| Keys | Phone community DTS: PON power/resin, PM8550 GPIO6 volume down | gpio-keys/PON configuration; physical tests outstanding |
| DSP / charging | Phone community DTS explicitly notes ADSP startup affects display | DSPs left disabled in diagnostic DTS; do not claim battery/charging support |
| Radio / audio | Pad has different board firmware/calibration and topology | No Pad firmware or audio topology is installed into the phone image |

Source links:

- [Phone reference DTS](https://github.com/sm8750-mainline/linux/blob/1f2047e8663eda76c8b172fd3e040e3b3fa17950/arch/arm64/boot/dts/qcom/sm8750-oneplus-dodge.dts)
- [Official phone overlay](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750/blob/d50b305f7da9e14715a25120a4ac7b1a4b8b97c3/kernel_platform/qcom/opensource/devicetree/oplus/dodge-23821-sun-overlay.dts)
- [Official touch overlay](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750/blob/d50b305f7da9e14715a25120a4ac7b1a4b8b97c3/kernel_platform/qcom/opensource/devicetree/oplus/tp/dodge-oplus-tp-23821.dtsi)
- [Official display variants](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750/blob/d50b305f7da9e14715a25120a4ac7b1a4b8b97c3/vendor/qcom/opensource/display-devicetree/oplus/dodge-23821-display-sun-overlay.dtsi)

## First hardware experiment (not yet authorized to execute)

1. Inspect collected stock headers/FDT and prepare complete matching recovery inputs.
2. Reproduce actual ABL DTBO overlay selection with the phone's stock DTBO and a
   positive stock-tree control. Adjust packaging identity only from that evidence.
3. Use one RAM-only probe with a bounded deadline. Observe USB disconnect/re-enumeration
   and capture actual kernel logs; Fastboot OKAY alone is not a successful boot.
4. Validate read-only UFS policy, memory map, restart deadline and recovery before
   enabling one further subsystem. No partition writes or dual-boot conversion.
