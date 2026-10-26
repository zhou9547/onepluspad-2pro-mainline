# Saved phone input registrations and peripheral gaps

Host-only review of the saved Android input inventory, cross-checked against
the saved runtime DT and complete ancestor status. There are no new phone
queries, device writes or peripheral controls. Registration is stronger than
an unselected template but is not raw chip identification or functional testing.

| Saved Android input | Matching phone DT / evidence | Current candidate |
| --- | --- | --- |
| qcom-hv-haptics | Effective qcom,hv-haptics under PMIH010x, corresponding SPMI sysfs input path and advertised force-feedback capability | No matching compatible node; no accepted phone feedback |
| tof8801 | Effective ams,tof8801 plus corresponding I2C input registration | No matching node; no range/laser operation accepted |
| oplus,hall_tri_state_key | Virtual input registration | Does not identify the actual Hall silicon or prove candidate event mapping |
| oplus_fp_input | Virtual input registration and effective generic oplus,fp_spi node | No matching node; generic registration does not select a fingerprint vendor or solve trusted dependencies |

The available AW86927 module belongs to the inherited reference-board build.
It is not an implementation of the phone's PMIH010x HV haptics. The current
373-rule peripheral policy does not claim to deny every haptics module, so the
private runner additionally forbids AW86927 at guard, bring-up and final health.
There is no new haptics DT node or actuator activation. Never substitute a driver
by filename or copy reference-board motor voltage/frequency/calibration values.

Phone haptics needs review of the exact HV driver, supply/motor constraints,
calibration/protection and input integration before a bounded effect. ToF needs
its own identity, driver/firmware and emitter/control review. Hall events and
fingerprint trusted integration remain distinct tasks. Physical feedback,
range targets, magnets/key movement and biometric interaction are deferred to
the combined owner session only after those software prerequisites pass.
