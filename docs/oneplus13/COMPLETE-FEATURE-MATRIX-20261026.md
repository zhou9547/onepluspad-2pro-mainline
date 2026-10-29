# OnePlus 13 complete adaptation register

The target is complete phone support. It is not complete. A driver object,
enabled DT node, service process, PCM open or device inventory is not full
functional acceptance. Saved stock FDT templates do not establish populated
silicon. All testing remains temporary RAM boot; there is no installation or
flashing acceptance.

| Function | Current evidence | Remaining work |
| --- | --- | --- |
| Native display | r64 exact Actionsee214438 AA569/GNOME regression; owner previously confirmed manual rotation no longer logs out | Brightness range, artifacts, refresh modes, blank/unblank and sustained use |
| GNOME ordinary user | r64 Wayland/Mesa/Chinese/SSH/Dock regression; owner confirmed taskbar, Chinese and touch | Wider application, keyboard, scaling and sustained usability |
| GPU | r64 project Mesa pixel/compositor regression with exact phone firmware | Wider rendering/API workload, performance, stability and power |
| Touch | Owner confirmed usable touch and manual orientation behavior; retained device regression | Entire panel, coordinates, gestures, multitouch and palm behavior |
| WiFi | r64 exact-phone-firmware5GHz5240MHz and2.4GHz2437MHz authentication/DHCP/default route/LAN HTTP, radio policy checks | Roaming, resume, sustained traffic, Internet/TLS and UI coverage beyond these bounded checks |
| Bluetooth transfer | Owner confirmed run51 peer file receipt using inherited reference inputs; later component regressions | Exact phone firmware/address/power path review before new radio run; reverse transfer, reconnection and other profiles; A2DP/HFP unaccepted |
| Battery | run68 exact phone ADSP58/58 single start with battery capacity/voltage/current/temperature inventory; old telemetry used reference ADSP | Accuracy over time, charging policy and power consumption |
| CPU frequency | run66 two SCMI schedutil policies and CPU cooling devices after reviewed module delivery | Frequency transition accuracy, load/power and thermal behavior; no manual clock or voltage overrides |
| Charging / USB-C / PD | PMIC/ADSP services and tethered test transport; UCSI bound but deferred initialization with fixed peripheral role | Resolve role provider with independent recovery, then roles/current/PD/charging/peripherals; do not switch current recovery transport unattended |
| Thermal management | run63 48 readable temperature zones; run66 CPU/GPU/WLAN cooling devices registered | Trip policy and actual thermal intervention; controlled load only after review |
| Speakers / receiver | Owner confirmed top/bottom independently; r64 fresh separate-speaker/microphone correlation and real20/50/100% plus mute response, no clipped samples | Absolute loudness, long-duration dynamic protection, normal default activation and wider content; keep896 hardware ceiling |
| Microphones / headset / audio routing | r64 native microphone capture, restored controls and independent speaker correlation; explicit PipeWire speaker candidate follows system volume | Headset, wider routes, echo cancellation and ordinary default policy; raw test audio is deleted |
| Accelerometer / gyroscope / compass / light / proximity | r64 ordinary production startup without diagnostic warmup,32 samples left-up/vertical and Mutter1; earlier multi-pose raw data exists | Visible multi-pose automatic transitions on current image; other sensor streams/calibration and power |
| Haptics | Saved Android qcom-hv-haptics input and effective PMIH010x HV node; candidate has no matching node, AW86927 substitution held | Exact HV driver, motor/calibration/protection and bounded control before physical feedback test |
| IR transmitter / Hall / cover / ToF | Saved phone FDT and public IR driver map SPI5/MOSI53/L9B3.056V; see INFRARED-BOARD-REVIEW-20261029.md; ToF/Hall stock inventory only | Isolated IR pin/rail/waveform candidate and independent optical acceptance; ToF/Hall drivers and physical validation |
| Power / volume / alert keys | GPIO/power-key software nodes; input inventory only | Map actual events, short/long behavior and desktop integration |
| Cameras / flash | r62 S5KJN5 at7-bit0x2d, strict0x38e5 ID, runtime suspend and complete CCI/sensor teardown; upstream camera components compile offline | Resolved L/S three-trio C-PHY family via probe_intent OR; exact timing, phone custom PHY/CAMSS graph, real pixel capture/libcamera and flash; chip ID is not capture |
| Modem / mobile data / SMS / calls | Candidate MPSS remoteproc exists but disabled | Phone firmware, memory/transport/power and modem recovery; calls/IMS/emergency functionality unaccepted |
| GNSS | No functional acceptance | Modem/DSP/service transport and bounded location checks; DT absence does not mean hardware absence |
| NFC | Saved stock chipset label SN220T; no candidate integration | Actual controller/protocol identity, transport/power, userspace and bounded protocol test |
| Fingerprint / secure biometrics | Stock generic SPI software node, no candidate integration | Actual chip, trusted execution dependencies and userspace support; never overwrite enrollment/calibration |
| RTC / network time | r62 host clock bridge; PM8xxx RTC wakeup exposed with no alarm changes | Epoch/time policy and independently verified wake; no guessed offset or RTC write |
| Suspend / resume / idle power | Not accepted; awake-scope independent reset passes in r62, while idle counter behavior remains unresolved | Idle and suspend recovery, RTC wake, power and charging measurements; awake recovery does not qualify deep sleep |
| USB host / display / storage peripherals | USB gadget test link works | Physically attached peripherals and role switching later, after isolated theoretical checks |
| Internal storage / installation / updates | Block read-only RAM guard; repeated Android return checks | No install, partition, boot slot or OTA design is accepted; current scope prohibits writing them |
| Recovery / endurance | r64 Android return501.4s, seven matching baseline fields, clean kernel health and zero writes | Awake independent reset with zero host recovery requests qualified; idle/suspend/endurance remain open; historical failed-run stop flags preserved |

The retained acceptance above is bound to Actions40833999996 and sourceee214438,
with downloaded-artifact verification and r62 published host helper66756a58/parser e65db825. A newer diagnostic commit is not a
new accepted image. r64 verifies one real Iris AVC/NV12 frame with checked pixels/timestamp, runtime
suspend and full teardown under the awake guard. Desktop playback, VA-API and
long-duration/all-codec support remain unqualified.

`review-feature-gaps.py` counts effective compatible nodes only. Defaults keep
camera/video manual, MPSS disabled and unreviewed phone peripherals absent.
Stock template presence is never sensor identity or full functional acceptance.

## Deferred owner session

The owner is not operating the phone before19:00 on2026-10-29 and left it
left-side-up. Autonomous checks use that fixed pose; no physical transition is
claimed. A later attended session can cover visible automatic rotation, normal
loudness, UI/key behavior and externally observable peripheral output together.

## Autonomous work order

Preserve accepted desktop, both WiFi bands, Docker, audio, Chinese/SSH/Dock and
sensor startup in every relevant combined regression. Require the qualified awake
watchdog protection for Iris activation; require idle/suspend recovery before unattended suspend. Continue the
phone camera PHY/mode review, then GNSS, NFC, infrared, full USB roles, power and
remaining phone services according to owner priorities. Reuse pinned public
implementations after checking exact phone electrical and firmware identities.
Keep tests combined and bounded; no flashing, partition changes or installation.
