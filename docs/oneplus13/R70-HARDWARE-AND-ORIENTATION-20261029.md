# r70 hardware result and upright-axis candidate

The source-bound mixed build40885554785 on83768fc completes successfully. Its
downloaded kernel, SSC and complete RAM archive match GitHub SHA256 digests.
Independent byte verification covers the boot sections, matching module release,
72 qualified firmware files, rootfs, sensor runtime, audio/GStreamer helpers,
boot arguments and qualified DTB identity.

The combined RAM round returns Android with matching Android baselines and zero
partition writes. Fixed-AU GStreamer negotiation now succeeds through the guarded
phone V4L2 H264 decoder. Pixels, PTS, NV12 layout, pipeline NULL teardown,
automatic Iris runtime suspend, module unload and video-node removal all pass.
This accepts one bounded 320x240 synthetic framework frame; generic movie/codec
playback and sustained sessions remain open.

The40-second physical pose collection works:156 samples correlate SensorProxy
and Mutter without restarting GNOME Shell. Left-side-up maps to transform1 and
right-side-up to transform3. Physically upright with the earpiece at the top is
reported as `bottom-up` and transform2, which directly explains the inverted
portrait. The SSC data already supplies handset X/Z axes, so the candidate adds
only a udev pitch inversion (`1,0,0; 0,-1,0; 0,0,1`) after SensorProxy's SSC
matrix. It is expected to change upright/bottom-up without exchanging left/right;
this expectation requires a fresh physical test. No global panel transform or
fixed orientation lock is used.

Native microphone capture, quiet speaker tone and two-channel acoustic response
now pass after display startup. The prior display-policy false rejection is no
longer observed. The later desktop software-volume test did not execute because
it remained after Docker and both WiFi bands: fewer than its required78 seconds
remained in the fixed600-second recovery deadline. The host stopped rather than
extend the timer, and the phone returned automatically. Audio absolute loudness,
stock dynamic protection, system-volume curve and mute still need combined
validation in the next candidate. No success is inferred from earlier stages.

Both WiFi bands, DHCP, LAN HTTP, Docker bridge/NAT and WiFi-SSH identity checks
pass before the stop. Camera remains at strict S5KJN5 ID/teardown plus compile
inputs; no camera frame exists. NFC/GNSS/IR, complete USB host role and suspend/
power/endurance remain open. Preserve the halted single-use ledger.
