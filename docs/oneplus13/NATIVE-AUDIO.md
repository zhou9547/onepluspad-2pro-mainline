# Phone audio evidence and acceptance

Saved owner runtime FDT has two awinic,aw882xx_smartpa nodes, I2C990000 addresses
34/35, sound-channel0/1. This is a vendor family name, not a measured chip ID.
The codec path includes WCD939x and LPASS SoundWire. Do not substitute the Pad's
amplifier count, codec or gain settings.

Public dodge vendor reference5cdea50164c2c9435e8612da132396877acd8730 provides
a1792-byte aw882xx_acf.bin. Its four sections are indices0/1, Music/Receiver;
all CRC8 values, inner checksums and75-register section lengths pass an offline
parser compared to OnePlus vendor d50b305f7da9's AWINIC format. Inner headers
identify AW88461, although the outer header is the generic legacy format and
does not contain an authenticated hardware ID. The file is not owner-version
matched and no payload/register value is published or loaded on a phone.

The pinned kernel codec inventory has AW88081/88166/88261/88395/88399, but no
dedicated AW88461 filename. This alone does not establish register compatibility
or incompatibility. Resolve exact chip ID and vendor implementation before
selecting or adapting a driver; do not label an AW88261 node merely to bind it.

Next steps: inspect the original project's same-SoC AudioReach/ADSP graph and
exact official AW88461 support; identify phone backend clocks/format/slots and
firmware/topology versions. Keep power-up muted until an authorized experiment
can check clock order, PCM/DSP errors and amplifier state. No fabricated supply,
generic tuning file or increased gain will be used as evidence of working audio.

Acceptance is zero DSP/amplifier errors, verified parameters, playback/recording
with positive and silent controls, separate speakers/microphones and clean UCM
on a fresh installation. Speaker protection and gain policy remain unresolved.

Reference: [pinned public dodge vendor tree](https://github.com/TheMuppets/proprietary_vendor_oneplus_dodge/tree/5cdea50164c2c9435e8612da132396877acd8730).
