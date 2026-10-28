# Desktop sensors and speaker-volume candidate, 2026-10-28

## Hardware evidence retained

The owner-assisted 12-second posture window completed on image
`17ecf5425ad3b07aff53c3e328b5838a0ae20a12`. It collected 60 accelerometer
posture samples on one SensorProxy claim and produced actual `bottom-up`,
`left-up` and `right-up` transitions. The owner action was performed with the
screen not started, so this is sensor-direction evidence and not an automatic
display-rotation pass.

The same boot's independent two-amplifier acoustic fixture passed. Amp0 and
Amp1 each produced a response above the existing threshold on both capture
channels, with no clipping or amplifier fault. Earlier owner listening already
identified Amp0 as the top speaker and Amp1 as the bottom speaker. At the
fixed 640 test level both were audible but too quiet for ordinary listening.

## Desktop sensor runtime

The next image installs the reviewed 10-file native userspace and 922-file
text dataset only after the protected RAM ADSP is running. A one-shot root
service verifies the archive and adds the files to the RAM overlay. The
long-running file service then runs as UID 65534 with a closed-device policy
that permits only `/dev/fastrpc-adsp-secure`.

A reviewed udev rule owns that node by UID 65534, mode 0600, and supplies the
accelerometer, compass and gyroscope types to SensorProxy. The proxy runs as
UID 65534 and owns `net.hadess.SensorProxy` on the system bus. D-Bus and polkit
policies allow an active local desktop user to use the reviewed claim action.

The stack remains inactive until `qualified-bringup --all` has verified the
kernel, RAM overlay, physical-storage protection, recovery services and
powered ADSP. No boot-wide module autoload or persistent-storage service is
introduced. GNOME's orientation lock is then set to false. A bounded checker
requires at least three physical accelerometer orientations and at least two
Mutter logical-monitor transforms during the same 20-second window.

## Speaker volume

PipeWire remains the user-facing volume control. The UCM speaker device sets
both AW88461 channels to the driver's fixed RAM test ceiling, while the GNOME
software volume attenuates from that value. The previous ceiling was 768,
which leaves 23.9859375 dB of additional attenuation beyond the signed ACF
profile. The new candidate uses 896, leaving 11.921875 dB and making the
speaker about 12 dB louder at 100 percent.

The 896 ceiling remains below the signed profile and is retained only for the
RAM desktop. It does not implement or claim the stock dynamic speaker
protection graph. The existing 256 transport, 640 acoustic and amplifier-off
checks remain unchanged. Hardware acceptance must show that system volume and
mute affect playback, both speakers remain operational without clipping or
amplifier faults, and disabling PipeWire restores zero volume and powers both
amplifiers off.

## Network test correction

The previous 2.4 GHz stage stopped before an authentication attempt. Explicit
band credentials now choose an already cached BSSID from that band and pin
both the band and BSSID in the temporary NetworkManager profile. No new scan,
credential output, driver reset, channel override or power override is added.
The existing 5 GHz checks and post-connection frequency verification remain.

## Combined acceptance required

One source-current Actions build and one RAM boot must exercise the desktop
sensor stack, physical orientation actions, UCM/PipeWire volume and mute,
bounded microphone/acoustic cleanup, Docker bridge traffic, 5 GHz and 2.4 GHz
DHCP plus LAN HTTP, project Mesa/GNOME, the always-visible Dock, Chinese input,
SSH password login and clean return to Android. The output needs separate
runtime receipt for the desktop sensor and audio stages before any hardware
capability is marked accepted.
