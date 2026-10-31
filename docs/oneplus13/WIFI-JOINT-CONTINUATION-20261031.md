# 5 GHz delivery and joint continuation, 2026-10-31

The owner resumes adaptation, prioritizes 5 GHz and requests combined testing
and preservation of qualified features. The previous candidate is published
at `09abb36db05967bea129b55c54ea2e529d73b066` and Actions 41100212379
completed successfully. Local review commit `eed8d308` has the same tree.
Historical r191 directly confirms a 5240 MHz control channel. This history
does not qualify a newly changed image or renew a consumed hardware ledger.

## Source changes

- `qualified-bringup --wifi` retains platform/ADSP initialization and the
  qualified firmware, WLAN module order and RF policy, but no longer waits
  for FastRPC, SensorProxy and accelerometer availability. Those exact sensor
  steps remain in `--all` before the desktop starts. A sensor service failure
  must not prevent the independent WiFi control path.
- The installed WiFi CLI checks the complete bounded kernel history before
  every command. Previously this guard was supplied only by a private host
  overlay. The package manifest now binds all ten WiFi/desktop prerequisite
  runtime files; final SquashFS verification compares their delivered bytes
  with the same checked-out source. Both actual-band and IPv4/route/HTTP
  checks, country transition refusal and private credential handling remain.
- USB storage selection excludes phone UFS `sd*` devices by requiring USB
  ancestry and the read-only block flag. Directory enumeration has a 128-entry
  budget; regular-file reads are limited to 4096 bytes before allocation,
  without following symlinks or accepting FIFOs. An existing touchscreen
  input node cannot qualify an external HID; HID enumeration itself no longer
  counts as tested event I/O. Cleanup still restores the device role, and the
  result is initialized even if host inventory fails.
- USB diagnostics read Type-C roles, partner presence and ADSP state before
  host mode, after switching and after restore. No Type-C policy, VBUS or
  firmware restart is introduced.
- Python GNSS duration now matches the native client's 5–180 second range
  and rejects invalid durations before launching the process. The preceding
  exact NotSupported fallback still needs real GNSS start/fix/stop evidence.

## Reference review

The original Pad's checked-out `sm8750-erhai.dts` explicitly routes role
notifications through PMIC GLINK after ADSP starts. Its `pmic_glink.c` uses
the `msm/adsp/charger_pd` service for the generic compatible. The phone's
qualified tree already has the generic PMIC GLINK compatible and dual-role
connector; the phone configuration already enables PMIC GLINK/UCSI. Thus an
offline ADSP in r191 is a useful observation to collect in the next round,
not sufficient evidence for copying the Pad's connector, mux or power data.

Original reference: `yzddmr6/linux-sm8750-erhai` board DTS and
`drivers/soc/qcom/pmic_glink.c`; original-project ordering is recorded in
`UPSTREAM-ORDER-COMPARISON-20261026.md`. No qualified DTB, kernel patch,
firmware, calibration or Pad integration is changed in this milestone.

## Joint acceptance requirements

After an exact Actions image has been downloaded and independently checked,
review a fresh one-use plan for both WiFi bands, GNOME/GPU/touch/Bluetooth,
audio and sensors, plus GNSS/NFC/camera/USB diagnostics. Keep the independent
recovery deadline, RAM-only execution, physical-storage protection and seven
Android return checks. Obtain current-chat start confirmation for that plan;
never run an archived `--run-once` or reuse its approval. USB cable removal
requires a fresh challenged WiFi control path, then an operator card.

No new phone operation has been performed by this source milestone. Build
and unit results are offline qualification, not hardware acceptance.
