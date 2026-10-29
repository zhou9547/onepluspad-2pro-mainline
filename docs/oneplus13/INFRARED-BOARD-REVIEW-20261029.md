# Phone infrared board mapping

A bounded rc-core SPI source candidate and disabled board fragment are now in
`tools/oneplus13/infrared-draft`. They have not been compiled or tested. The
driver requires the exact voltage and rejects the current incompatible L9B
constraint; the fragment is not included in the phone DT. See the
[source-only batch](SOURCE-ONLY-BATCH-20261029.md) for implementation and gaps.

This is an offline stock-board and public-source review. No infrared transmission,
power vote, pinmux change or functional acceptance has occurred.

The saved phone runtime FDT identifies the emitter as SPI, not PWM:

| Resource | Phone evidence | Mainline mapping / remaining work |
| --- | --- | --- |
| Controller | GENI SE at `0xa94000`, IRQ358, wrapper1 SE5 | `spi5` in the pinned SM8750 tree; its I2C sibling must remain disabled |
| Child | `oplus,kookong_ir_spi`, chip select0, mode0, max5MHz | Vendor sends encoded carrier bits over MOSI; no proprietary command protocol is shown in the public driver |
| Active pin | GPIO53, `qup1_se5_l1`,6mA, bias disabled | Mainline names its mux `qup1_se5`; select only GPIO53, not the generic four-pin SPI group |
| Sleep pin | GPIO53, GPIO function,2mA, bias disabled | Explicit sleep state required; do not touch neighboring pins |
| Supply | `consumer_ir_core` uses `pm_humu_l9`, RPMh resource `ldob9`, exactly3056000uV | Board `vreg_l9b_2p9` currently allows2960000..3008000uV; a separate reviewed candidate must account for the higher voltage and shared consumers |
| Carrier | Public core accepts20..60kHz, default duty divisor3 | Stock SPI runs5MHz and encodes a carrier in its bitstream; mainline `ir-spi` instead uses16bits/carrier cycle, requiring waveform/clock review |

The pinned kernel has `drivers/media/rc/ir-spi.c` with the standard rc-core/LIRC
transmit interface. Reuse is preferable to the vendor's global misc-device core
if the board power, exact GPIO mux encoding and generated waveform agree.
Its required `irda_regulator` supply must be mapped explicitly; do not accept a
dummy regulator. The generic driver's default50% duty differs from the vendor's
one-third duty and must not be mistaken for stock settings. A populated node or
successful SPI transfer alone cannot establish infrared optical output.

Keep the default phone tree unchanged. First build an isolated disabled board
candidate, check shared rails and pin ownership, then combine bounded probe,
teardown and existing-feature regressions in a later RAM session. Physical output
will still need an independent receiver or owner observation.

## Pinned primary sources

OnePlusOSS `android_kernel_modules_and_devicetree_oneplus_sm8750`, commit
`d50b305f7da9e14715a25120a4ac7b1a4b8b97c3`, GPL-2.0-only:

- `vendor/oplus/sensor/kernel/oplus_consumer_ir/oplus_ir_spi.c`, SHA256
  `248dafc2bd316d1039403e65877393a83e8ca0b3a3776c3a284e3f96ebd4b9c9`.
- `vendor/oplus/sensor/kernel/oplus_consumer_ir/oplus_ir_core.c`, SHA256
  `33ebd71364431165be57e9bae9489c5da3d21cd59926367dc948ebe7bb93aaa0`.
- `vendor/oplus/sensor/kernel/oplus_consumer_ir/oplus_ir_core.h`, SHA256
  `7ffeb12603d0951f25f9ce77dc4601042be61d38f59c02fb927e28a36d265217`.

Platform pin `7a81d184e3098624d4342d8f4eff5e23674bcc9f`:
`drivers/media/rc/ir-spi.c`, `drivers/pinctrl/qcom/pinctrl-sm8750.c`,
`arch/arm64/boot/dts/qcom/sm8750.dtsi`, and the attributed phone regulator DTS.
Raw stock FDT and private records remain local; this document publishes only
reviewed hardware-resource facts.
