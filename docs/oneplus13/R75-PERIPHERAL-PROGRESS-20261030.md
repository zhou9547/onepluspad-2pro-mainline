# r75 modem, NFC, suspend and peripheral-source progress

This note records source and RAM evidence collected on 2026-10-30. It does not
upgrade any untested feature to hardware acceptance.

## Verified RAM results

The combined quiet r74b boot at source `f86a1bfe` passed the strict S5KJN5
chip-ID probe and teardown, one native Iris AVC/NV12 frame with clean decoder
teardown, NFC controller binding and start/stop, the read-only peripheral
matrix, Android return and all baseline properties.

The NFC path loaded the exact `nfc`, `nci`, `nxp_nci` and `nxp_nci_i2c`
modules after removing only their four temporary RAM deny entries. The
controller bound at I2C `1-0028`, driver `nxp-nci_i2c`, GPIO75 edge IRQ212,
and created `nfc0`. A generic-netlink transaction changed `nfc0` from
`powered=false` to `powered=true`, started polling with mask254, then issued
stop polling and device down. Controller startup is verified; no physical tag
was present, so tag discovery remains unqualified.

The reviewed C.93 modem set contains48 files and 74,867,650 bytes. The MDT
header, hash segment, split lengths and load spans match the saved 246 MiB
MPSS carveout and512 KiB modem-DTB carveout. On the phone, remoteproc entered
`running` with firmware `qcom/sm8750/oneplus/dodge/modem.mdt`. GLINK exposed
`IPCRTR`, `SSM_RTR_MODEM_APPS` and the RPMsg control endpoint. `qrtr-tun`
loaded and created `/dev/qrtr-tun`. MPSS then returned to `offline`; full
history health remained clean.

One RTC-woken memory-suspend test completed. `CLOCK_BOOTTIME` advanced14.334s,
`CLOCK_MONOTONIC` advanced0.103s, and the RTC alarm woke the same RAM session.
A32-second Gunyah safety timeout was armed across the sleep and visibly
disarmed after resume. The first coordinator stopped only because it required
the watchdog sysfs state to change instantly in the same shell; the receipt
shows the transition completed. The source helper now waits five seconds for
that transition and the next combined round must repeat this acceptance.

## Source candidate in this change

- Default review-tree composition adds NFC and enabled-but-non-auto-boot MPSS.
  IR and DWC3 OTG remain isolated RAM candidates because the first OTG boot
  caused Windows NCM DHCP loss before the host-role phase.
- The DWC3 host candidate defaults to device and changes `dr_mode` to `otg` so
  debugfs can switch roles. It must be controlled over Wi-Fi after the adapter
  is moved from the recovery cable.
- IR uses SPI5, CS0, GPIO53, one-third-duty38kHz waveform and the exact
  `3.056V` L9B vote. L9B's maximum is raised from3.008V while its minimum and
  other consumers remain unchanged.
- `qmicli`, `qrtr-tools`, ModemManager, `v4l-utils` and `ir-keytable` are
  installed in the next rootfs.
- NFC and modem start services are enabled. IR remains manually gated until
  optical output is observed.

## Remaining physical acceptance

- Put a real NFC tag at the phone during a bounded poll and retain the target
  attributes.
- Run qmicli LOC through QRTR, start the location engine, inspect satellites and
  obtain a real position report.
- Observe IR emission with an independent receiver or camera.
- Insert the USB-C adapter and storage/mouse after the role switch; retain
  enumeration and I/O evidence.
- Repeat suspend/resume and deep-idle cycles, then measure long-term power.
- Complete supplier-specific S5KJN5 initialization, CAMSS/CSID/VFE/C-PHY graph
  and a real camera IOSM/RAW frame.
