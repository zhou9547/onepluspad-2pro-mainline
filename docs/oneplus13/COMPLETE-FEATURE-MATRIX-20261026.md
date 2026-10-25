# OnePlus 13 complete adaptation register

The target is complete phone support. It is not complete. A driver object,
enabled DT node, service process, PCM open or device inventory is not full
functional acceptance. Saved stock FDT templates do not establish populated
silicon. All testing remains temporary RAM boot; there is no installation or
flashing acceptance.

| Function | Current evidence | Remaining work |
| --- | --- | --- |
| Native display | Prior visible-display owner evidence; repeated explicit AA569 activation | Visual artifacts, brightness range, blank/unblank, rotation, refresh modes and sustained use |
| GNOME ordinary user | run58 active Wayland user session, project Mesa, Settings process and application bus | Visual usability, scaling, on-screen keyboard and UI interaction |
| GPU | Adreno 830/Mesa 26.2.3 4×4 pixel readback and compositor mappings | Wider rendering/API workload, performance, stability and power |
| Touch | Native input device; run50/51 real touch-down counts | Entire panel, coordinates, gestures, multitouch and palm behavior |
| WiFi | run55/58 full bound IPv4 HTTPS on previous network; run61/62 full acceptance on replacement network; run62 desktop and three HTTPS probes jointly pass | UI regression later; bands, roaming, resume, sustained traffic and hotspot mode |
| Bluetooth transfer | Owner confirmed run51 peer file receipt; component regressions | Reverse transfer, reconnection and other profiles; A2DP/HFP are not accepted |
| Battery | Repeated capacity/voltage/current/temperature/status inventory | Accuracy over time, charging policy and power consumption |
| Charging / USB-C / PD | PMIC/ADSP services and tethered test transport exist | Roles, current negotiation, charging limits, thermal response and peripherals |
| Thermal management | Candidate has enabled TSENS software nodes | Driver readings, cooling devices and trip policy; controlled load only after review |
| Speakers / receiver | Stock enables two AWINIC nodes; WSA branch quarantined; AW88461 offline object compile and synthetic tests pass | Actual amplifier identity, clock/pin/MI2S route, owner-matched protection/tuning, gain policy and recovery gates before any stream |
| Microphones / headset / audio routing | No accepted phone capture/playback path | Codec/DMIC/MI2S endpoints, topology and PipeWire policy; independent stream review first |
| Accelerometer / gyroscope / compass / light / proximity | Phone ROM extracted; board-independent userspace CI passes | Owner registry/calibration, phone identity and loader semantics, one attach gate; streams and physical orientation unaccepted |
| Haptics | No functional acceptance | Exact actuator/driver, power constraints and bounded control before physical feedback test |
| IR transmitter / Hall / cover / ToF | No functional acceptance; vendor software clues require effective-node and identity review | Actual devices and electrical limits, driver/API integration, physical targets or magnets later |
| Power / volume / alert keys | GPIO/power-key software nodes; input inventory only | Map actual events, short/long behavior and desktop integration |
| Cameras / flash | No candidate camera pipeline or sensor nodes in software review | Identify populated sensors independently of stock templates; clocks/power/CSI/ISP/firmware/libcamera; flash safety review |
| Modem / mobile data / SMS / calls | Candidate MPSS remoteproc exists but disabled | Phone firmware, memory/transport/power and modem recovery; calls/IMS/emergency functionality unaccepted |
| GNSS | No functional acceptance | Modem/DSP/service transport and bounded location checks; DT absence does not mean hardware absence |
| NFC | Stock software node, no candidate integration | Actual controller identity, transport/power, userspace and bounded protocol test |
| Fingerprint / secure biometrics | Stock generic SPI software node, no candidate integration | Actual chip, trusted execution dependencies and userspace support; never overwrite enrollment/calibration |
| RTC / network time | RAM-only host clock bridge, monotonic recovery deadline preserved | Independent boot time and trusted network time policy, explicit RTC effects review |
| Suspend / resume / idle power | Not accepted | Prove independent wake/recovery before any unattended suspend; timers alone do not prove wake |
| USB host / display / storage peripherals | USB gadget test link works | Physically attached peripherals and role switching later, after isolated theoretical checks |
| Internal storage / installation / updates | Block read-only RAM guard; repeated Android return checks | No install, partition, boot slot or OTA design is accepted; current scope prohibits writing them |
| Recovery / endurance | Multiple bounded boots recover automatically; seven baseline samples per run | Sampling is not a full partition audit or a guarantee against all failures; no new test after recovery/health failure |

`review-feature-gaps.py` checks only aggregate compatible-node counts with all
ancestor statuses. The current quarantined DT has no AW nodes, no camera pipeline,
NFC or fingerprint integration, and disables MPSS. Those are substantive open
adaptation tasks, not merely a pending owner click. The stock camera tree contains
many simultaneously enabled software templates; do not choose a sensor from
their presence alone, repeating the former WSA mistake.

## Deferred owner session

The owner is not operating the phone during the autonomous window. Accumulate a
single later acceptance session covering visible desktop/display, actual touch,
WiFi UI after automatic network success, key behavior, Bluetooth reverse transfer
and any ready external-peripheral tests. Audio listening, microphone recordings
and physical sensor motion join that session only after their independent
identity, protection, calibration and recovery prerequisites pass. Suspend is
not a substitute for such prerequisites, even with an owner present.

## Autonomous work order

First finish regression of the quarantined nonaudio image and asynchronous
NetworkManager gates. Keep the separately verified new rootfs distinct from
the old hash-bound RAM image. Then resolve the AW/MI2S and phone sensor loader
prerequisites offline, and research unimplemented peripherals against pinned
phone/community/vendor sources. Each candidate needs its own theoretical,
build and recovery evidence before a bounded combined test. Do not rerun a
successful test solely to consume the authorization window.
