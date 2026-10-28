# Speaker and sensor joint candidate

The owner prioritizes speakers over conflicting sensor work. Temporary RAM
testing is authorized for this session; no flashing or persistent installation.
Existing display, touch, project Mesa/GNOME, dual-band WiFi, Bluetooth transfer
components, battery, Chinese desktop and SSH must be preserved.

Both stock AWINIC devices returned chip-ID register00=0x2308 using their already
selected, read-only sysfs register accessor. No selector/register or calibration
write was performed. The stock driver reports v1.15.0.3, matching the reviewed
[official OnePlus implementation](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750/blob/d50b305f7da9e14715a25120a4ac7b1a4b8b97c3/vendor/oplus/kernel/audio/codecs/aw882xx/aw882xx.c).
The supplied C.93 payload verifies against its package metadata and is identical
to the earlier extracted payload. The generic ACF matches the saved owner hash;
its provenance and proprietary status are recorded beside the file.

The source build now includes an AW88461 module, still blocked by the explicit
peripheral policy. It is not an automatic boot driver. The separately derived
speaker test card uses two channels, owner GPIO2/164 reset with translated
active-low semantics, the actual I2C990000 controller, and owner 4mA secondary
MI2S pin states. Every unrelated DT property and memory reservation is compared
before and after serialization. The published qualified base DTB is unchanged.

The first graph is 48kHz/stereo/S16_LE: that is supported by both CPU port and
codec and uses a 1.536MHz bit clock. Android's 24bit endpoint remains a separate
draft. The graph uses the original project's pinned AudioReach macros and no
tablet TDM/WSA wiring or gain. Maximum attenuation is the default. The temporary
ALSA test control is capped256, adding at least72.1459dB attenuation below the
matched profile. Desktop automatic ALSA activation is disabled until playback,
protection and a complete UCM profile are qualified.

The explicit RAM checker first loads the exact kernel's dependency closure,
requires both IDs and maximum attenuation, and opens only two seconds of digital
zero. It samples actual amplifier clock/power/fault state twice, then requires
PCM completion, route restoration and both amplifiers off. Read-only driver
status exposes only bounded health registers, not a general register interface.
This can qualify a silent transport path, not audible playback or dynamic
thermal/excursion protection. Rootfs contains the checker, topology and ACF so
Actions can reproduce the candidate without an old binary overlay.

Sensor work stays metadata-only in this round. The light fallback is removed
from the shared Pad recipe and applied only to the phone probe. Returned UID
candidates are capped16. Numeric lookup counts, default-only flags and attribute
availability distinguish an empty query from an unavailable candidate without
publishing UIDs or vendor strings. An actual protobuf event with17 UIDs is fed
into the production receive callback and rejected before an attribute request.
Both release and ASan/UBSan suites pass. The reverse service now records stop
and attach evidence even when its metadata callback fails.

The previous nonempty/exhaustive light-discovery claim exceeded retained output
and is corrected in STATUS, TECHNICAL-DEBT and the original evidence JSON.
Android's fused-light name is a research lead, not proof of the SSC flags or of
a necessary new fusion algorithm. Accel/gyro/mag samples, physical axes, light
response, ordinary-volume speaker playback and listening remain unaccepted.

Before hardware: the actual AArch64 amplifier object compiles with W=1 and
warnings as errors; parser checks reject1023 malformed controls; real power
functions pass19 injected I/O failures plus timeout/fault/cancellation/default
attenuation controls. Three graphs compile/decode. Native ARM64 Actions and a
single combined RAM test remain the next gates.
