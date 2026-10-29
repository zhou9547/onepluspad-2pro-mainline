# Speaker absolute-volume comparison

The owner completed the r71 combined test successfully on source d872a04e:
Android returned after647.5s with seven matching baselines and zero partition
writes. Native Iris framework decoding, orientation, microphone, independent
top/bottom acoustic correlation, desktop volume steps/mute, Docker, both WiFi
bands, WiFi-SSH and the retained desktop checks all passed. These results are
retained independently of the later speaker-gain comparison.

For the absolute-volume check, the exact four-second stereo48kHz WAV generated
for the Linux desktop-volume test was copied temporarily into Android Music,
indexed by MediaScanner, opened with the system music player and played at
STREAM_MUSIC index160/160. The owner heard it and reports that Android is much
louder than Linux. The temporary media file was removed, the player stopped and
media volume was restored near its original user setting. No calibration or
personal media was read.

The Linux side used the same PCM waveform and amplifier test profile, but its
former896 control ceiling intentionally retained11.921875dB of profile
attenuation. The next reversible RAM candidate exposes the complete AW88461
control range up to1023. This removes that artificial ceiling attenuation while
retaining PipeWire's system-volume and mute controls.

The signed amplifier profile's dynamic protection and calibration are still not
qualified. The1023 candidate therefore requires a short, low-risk physical test
with both channels, monotonic system-volume changes, mute, and clip/fault checks.
It must not be described as a production/default gain policy until those checks
and stock dynamic-protection behavior are reviewed.

Separate from speaker validation, a first NFC candidate now targets the publicly
mapped I2C0 bus at address0x28 with IRQ GPIO75 and enable GPIO34. It uses the
upstream `nxp,nxp-nci-i2c` driver already present in the kernel module set. The
next RAM plan loads that driver and requires `/dev/nq-nci` before claiming a
bind. This proves neither NCI initialization nor tag discovery; the SN220T
secure-element path still needs a real protocol test.
