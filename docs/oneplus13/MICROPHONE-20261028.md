# Native microphone and acoustic-test preparation

This adds a separate manual RAM boot artifact. The default speaker-only boot
image remains byte-for-byte unchanged by the alternative-image builder within
each fresh source build. The qualified256-level checker and default volume0
are retained. The new driver ceiling is640 for a separate bounded acoustic
test: it adds at least36.026dB attenuation to the profile, and the fixed -18dBFS
signal stays at least54dB below that profile's full-scale signal. Neither image enables the audio modules or
desktop audio automatically. No partition is written.

The owner C.93 runtime DTB identifies WCD939x reset GPIO101, V8I L2 at1.2V for
PX, HUMU L15 at1.8V for buck/RXTX/IO, BOB1 for microphone bias supply and2.7V
for all four microphone bias settings. The inherited public tree incorrectly
assigns PX to the1.8V regulator and sets microphone biases to1.8V. The
alternative changes only WCD supplies/biases, sound-card model/routes and
the existing WCD capture link, in addition to the unchanged speaker derivation.
The pinned binding explicitly describes PX as a1.2V supply. Other regulators,
clocks, display, radio, storage and reserved-memory properties are retained.

The original phone mixer XML identifies AMIC1 through ADC1 and AMIC5 through
ADC4. Its handset/speaker capture settings use ADC6 and TX DEC84. The phone
XML SHA256 isc60219a7d06ddd9d219c3d9526b78051bd2014bb073e0749afe835871af5cd4c.
The downstream ChMap/SWR_MIC4/9 values are not copied: mainline WCD939x
maps ADC1/4 through its own SoundWire switches, matched to the original
project's SWR_MIC0/3 route. The selected SM8750 TX node falls back to the
sm8550 implementation with LPASSv11 data; its widgets are TX SWR_INPUT0..11,
not the older LPASSv9 TX SWR_ADC widgets.

The combined AudioReach graph retains the qualified Secondary MI2S SD1 S16_LE
48kHz stereo playback and adds MultiMedia3 / TX_CODEC_DMA_TX_3 S24_LE48kHz
stereo capture. The device link explicitly overrides the machine driver's
S16_LE default to S24_LE. Both graphs compile/decode using the existing pinned
BSD-3-Clause AudioReach macros. Native driver dependencies total33 modules.

The explicit capture checker requires the alternative DT model, exact kernel,
unchanged module policy, active RAM guard/deadline and read-only physical
storage. It preflights and saves every control before changing the route,
records two seconds to RAM and restores controls in reverse order on failure
or success. Raw audio is deleted. Published output is limited to counts,
levels and clipping statistics. A nonzero PCM result does not establish
physical microphone response, speaker audibility or dynamic protection.

Hardware validation completed in Actions40677232016 with source2457ac35. The
checker ran after successful native capture using the unchanged640 ceiling and
a fixed-18dBFS duplicated1000/1500Hz stereo fixture, with20ms ramps. It
captured the fixture once with both amplifiers muted, once with only Amp0,
once with only Amp1 and once with both. Independent captures eliminate reliance
on `arecord` flushing a live output file.

Amp0's1kHz response passed both nearby microphones at77.4x and9.27x over the
matching muted control. Amp1's1.5kHz response passed the required gate at
94.9x on one nearby microphone and6.86x on the other; at least one valid
near-field microphone is required. Both simultaneous responses passed. Neither
capture clipped. No gain increase, raw-audio retention, persistent service or
partition write occurred. Volumes, routes and capture controls restored, and
all amplifiers stopped. Human listening, ordinary desktop playback and dynamic
speaker protection remain separate acceptance.

References are the pinned kernel's
`Documentation/devicetree/bindings/sound/qcom,wcd939x.yaml`,
`sound/soc/codecs/wcd939x.c`, `lpass-tx-macro.c`,
`sound/soc/qcom/sc8280xp.c`, and the original project's
`packaging/erhai-audio/tree/usr/share/alsa/ucm2/Qualcomm/sm8750/OnePlus-Pad-2-Pro/HiFi.conf`.
