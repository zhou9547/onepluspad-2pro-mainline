# Separate S5KJN5 chip-ID RAM candidate

This candidate is for one explicit controller/sensor probe and teardown. It does
not provide a media capture pipeline. The default desktop and microphone boot
images remain separate artifacts. The camera image uses the same source-built
kernel, initramfs and rootfs, with a separate session nonce and a camera boot flag.

The saved C.93 phone graph identifies ultrawide cell1 as CCI0/master0, PHY1,
resetGPIO178,19.2MHz MCLK0 and chip-ID0x38e5. CCI0 registers0xac7b000 and IRQ426
match Hangxiang Ma's public resource series. Pin113 is SDA and114 is SCL;
pin89 carries MCLK0. The candidate contains only CCI0/master0 and one camera
client at7-bit address0x10. CAMSS, CSI PHY and streaming commands are absent
from the test protocol. The sensor driver retains its standard streaming API,
but this tree supplies no capture pipeline and the probe helper never calls it.

The C.93 camera regulator list provides PM8010m L4 at2.2V, L5 at1.8V,
L7 at2.8V and V8i L1 at1.0V. The existing qualified tree gives L1i a1.0?1.2V
range with no phandle/consumer. Only the separate camera tree adds a phandle
and narrows that unused regulator to1.0V. The two upstream1.0V sensor votes
(VDDD and VDDM) share it: this is an explicit inference from the phone's single
digital supply, not a measured schematic connection. The optional1.2V I/O
supply is absent for the phone's1.8V I/O arrangement. No PMIC input-parent
wiring is invented; RPMh regulator inputs remain firmware managed.

The derivation starts from the hash-qualified microphone/speaker tree. Exactly
three existing nodes gain/change properties: CAMCC and CAMBIST MCLK gain
phandles, and unused L1i gains its phandle and1.0V ceiling. Eighteen additional
nodes carry CCI, pinctrl, regulators and the sensor endpoint. Every other
property and memory reservation is compared with the microphone tree.

The normal kernel compiles S5KJN5 and CCI as modules. Media policy denies the
sensor, and an exact CCI policy entry prevents controller autoload. The manual
helper requires the protected RAM overlay, read-only physical storage, the
current kernel/module hashes, the original module policy, active absolute
watchdog services, the camera boot flag and the exact live camera wiring.
It runs before wireless or desktop sensor services start. It requests no frame,
checks that the driver bound after its own chip-ID check, waits for runtime
suspend, removes both sensor/controller modules and verifies the target vanished.
Any failed phase stops new hardware work and returns to Android within the
original joint-run deadline. It never renews that deadline.

Successful probe will establish sensor identity/power/I2C and teardown only.
The phone's explicit dodge-ultrawide PHY differs from generic SM8750, while the
staged upstream generic PHY currently implements D-PHY only. The correct lane
mode, custom timing, sensor mode/PHY agreement and a real frame remain separate
work. Ordinary display/orientation, audio, WiFi and Docker regressions are tested
in the same RAM boot after a successful camera cleanup.

Public sources retain original authors, licenses and hashes in
`tools/oneplus13/camera-draft/sources.json`. The original S5KJN5 v6 register tables
are unchanged; the local compatibility patch only removes two unused V4L2 callback
arguments for the pinned kernel. Original CCI messages and the separate exact-pin
resource rebase are likewise retained.
