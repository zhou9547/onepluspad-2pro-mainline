# Independent wireless work package

## Evidence, 2026-10-24

Mainline platform remains7a81d184e309; public OnePlus modules/device tree remains
d50b305f7da9. Saved owner runtime FDT selects qcom,cnss-peach. That pinned vendor
main.c maps it to PEACH_DEVICE_ID; cnss_utils/cnss_common.h defines17cb:110e.
The pinned kernel wifi7/pci.c supports WCN7860/110e, but only hardware major2;
this is source matching, not a live PCI enumeration/revision measurement.
Do not copy another phone fork's7850/1107 claim without checking actual evidence.

The owner FDT's six supply references and per-consumer requests are:

| Consumer | Phone regulator | Requested uV min/max |
| --- | --- | --- |
| io | F L3 | 1800000/1800000 |
| io12 | F L2 | 1200000/1200000 |
| aon | D S4 | 876000/1036000 |
| dig | F S5 | 876000/1000000 |
| rfa1p2 | I S7 | 1312000/1340000 |
| rfa1p8 | G S3 | 1860000/2000000 |

IO/IO12 request30000uA. Stock uses TLMM16 WLAN enable, PM8550VE_F GPIO3 BT
enable, PCIe0 PERST102 and WAKE104. The Pad's minimum852000uV AON/DIG cannot
be blindly copied: pwrseq bulk_get/enable does not replace stock consumer voltage
requests. Candidate constraints must retain this phone's requested range.
PCIe PHY supplies, pin states and shared-rail impact still require exact review.
No foreign board file, address, calibration or SAR limit may be substituted.

One reviewed non-root SSH metadata query matched the saved Android build.
All three queried vendor firmware paths returned DIR_UNAVAILABLE, meaning missing
OR inaccessible to that account. It does not prove firmware absence. The query
completed within2048 bytes; no root command, binary transfer or device mutation.
The independent auditor never connected. Do not silently escalate or retry it.

The matching .501 OTA catalog entry was found, but two stored official
OPlus downloadCheck links returned responseCode2306 with no download body.
No full OTA was downloaded and no firmware version match is established.
Keep this failed lookup evidence private; find a current public source or an
exact owner-provided local copy rather than using another board's firmware.

## Scope and acceptance

Prepare an isolated WLAN tree and compiled driver checks; keep display/touch
and the default diagnostic tree separate. Verify six rails, load constraints,
GPIO polarity/PMIC identity, PCIe/reset/wake/PHY and normal IOMMU isolation.
Keep the RF stack modular so a future test can establish USB diagnostics first.
PCIe host/PHY are early-boot platform components, so the standalone candidate
requires a separate bounded RAM experiment with recovery; it is not a default.

Use the original project's firmware-selection and SAR implementation only after
comparing its inputs to this phone. The kernel's WCN7860/hw2.0 path requires a
coherent firmware and exact board match. Hardware major, board ID and BDF choice
must remain explicit unresolved evidence until measured. Do not bypass revision,
regulatory or calibration checks to manufacture wlan0. Do not enable radio TX
before matching the stock board/region/power inputs.

Acceptance is actual PCIe/MHI/firmware-board logs, valid scan/association/DHCP/DNS,
2.4/5GHz80MHz traffic, reconnect and stable owner address. Compilation alone is
not Wi-Fi support. Bluetooth needs a separate UART/firmware/address and real
peripheral/reconnect test. No radio operation is authorized in this read-only phase.

## Compiled candidate scope

sm8750-oneplus-dodge-wlan.dts is independent of native display/touch. PMU graph
retains the pinned Erwin BSD-3-Clause attribution. It uses phone consumer minimums,
30mA IO system-load/HPM (debtD11), WLAN16 at16mA/pull-up, stock2mA PCIe pins and
F/SID5 BT-enable3 power-source1. Unlike the active stock pin state, pinctrl does
not assert output-high: the upstream sequencer owns output level. Its inherited
GPIOD_ASIS behavior preserves the boot value; no assumption that RF is off follows.
ATH12K, PCI power sequencing and the WCN sequencer are modules. No new initramfs
loader or WLAN firmware is included. The original diagnostics do not auto-load
these modules. PCIe host/PHY still probe early in this standalone DTB.

CI checks six exact rail min/max constraints, GPIO polarity/SID, pin drive/bias,
PMU graph, RF_CLK1 graph, IOMMU map and isolation from other candidates, with six
bad-input controls. Reference PHY/RF clock choices remain explicitly unproven.
Successful compilation must not be reported as link, firmware or radio support.

## Actual artifact verification

Actions39989714579 /7a896783193864d0cce159e49994971ffcc55e80 succeeded.
Actual artifact12517159870:59776599 bytes, SHA256
39c7b1c65c3cc673b387a64f89493729f72a6cb730d1369166a2d78fbeec3c8c.
CRC,33 manifest files, CI hashes, actual resolved modular RF flags, all six
bad-input controls and seven AArch64/vermagic module inspections pass locally.
The four WLAN-related modules are ath12k, ath12k_wifi7, pci-pwrctrl-pwrseq and
pwrseq-qcom-wcn. Default/touch DTBs remain byte-identical to badf9e; native display
checks and seven controls also pass. All four phone DTBs passed fresh offline
stock positive control, six overlays and15-bank protected memory checks.
No wireless firmware, board file, address, SAR value or manual auto-loader was
added. PCIe/PHY/firmware/radio operation remains untested.
