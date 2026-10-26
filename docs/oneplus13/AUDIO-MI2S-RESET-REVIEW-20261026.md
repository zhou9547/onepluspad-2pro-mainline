# Saved phone MI2S and reset review

Host-only review, no amplifier load or stream. The running phone chip identity,
owner-matched protection/tuning and machine topology remain open. The successful
AW88461 object compile is not hardware acceptance.

Saved owner runtime FDT SHA256:
`5a121983d6836aff2d8f8ebf3e6ef05db70d26548c2ab0a5037dc5f878714b6b`.
The active sound card's `qcom,sec-mi2s-gpios` phandle resolves to its secondary
MI2S pinctrl container and then four active TLMM groups: GPIO121 clock,
GPIO123 word select, GPIO122 data0, GPIO124 data1. The saved enabled AW nodes
use I2C addresses 0x34/0x35, channels 0/1 and reset pins GPIO2/GPIO164.
This traces actual phandles rather than choosing a similarly named LPI group.
It does not establish the DSP backend number, data-line direction or clock rate.

Both official vendor AW882xx variants at
`OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`
commit `d50b305f7da9e14715a25120a4ac7b1a4b8b97c3` physically assert reset low,
delay 1 ms, release high and delay 2 ms. Relevant paths:

- `vendor/oplus/kernel/audio/codecs/aw882xx/aw882xx.c`
- `vendor/oplus/kernel/audio/codecs/aw882xx_v1.13.0/aw882xx.c`

First file SHA256:
`e01ec4c153cc8f505f67b11944611656e1d47d34b147572f52922ea6587f95df`.
Second file SHA256:
`c8c212f1b6206cef2ae8cd615e6d22f3e8b15e34595750b2c461c259b12623bd`.

The mainline draft uses `gpiod_set_value_cansleep(reset, 1)` for logical
assertion and `0` for release. Preserving the vendor physical sequence therefore
requires active-low descriptor semantics. The downstream legacy `reset-gpio`
flags must not be copied unaltered to `reset-gpios`: the vendor used the raw GPIO
API, while the new driver uses logical values. No phone DT has been generated
or enabled by this review.

`review-mi2s-reset.py` repeats the saved-FDT phandle and actual source-function
checks, including ancestor status. `audio-draft/check.py` regenerates power
tests from actual driver functions. Actions40214539084 passed ARM64 ASan/UBSan
parser controls, 19 I/O fault points and kernel-object/API compilation against
phone kernel pin7a81d184e309. Artifacts were independently downloaded and hashed.
No module is installed in the phone image or referenced by its DT.

The additional community OnePlus13 source review at
`skb8/linux-sm8750` commit `1bc596dc166f320c012e6f4883d7fba041e82504`
contains downstream research notes and a different panel revision. Those notes
are research leads only; their template inventory is not owner-device identity
or a replacement for enabled-ancestor review. No panel/radio/calibration values
from that board were applied.
