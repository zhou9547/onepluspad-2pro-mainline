# Original-project USB peripheral comparison, 2026-10-31

## Concrete missing path

The reference integration was inspected at
[4cab38c79b24548e0afba29c6c710230c3692e31](https://github.com/yzddmr6/onepluspad-2pro-mainline/tree/4cab38c79b24548e0afba29c6c710230c3692e31).
Its kernel pin is erhai/v0.5,
2693a61eee1622611c8024d095eb7f476df48881. The phone retains
7a81d184e3098624d4342d8f4eff5e23674bcc9f plus its phone patches.

The important reference change is
[d9383c7269f626e3fa752d2396fd0d1716103826](https://github.com/yzddmr6/linux-sm8750-erhai/commit/d9383c7269f626e3fa752d2396fd0d1716103826),
power: supply: qcom_battmgr: USB VBUS for sinks on the OnePlus Pad 2 Pro.
It adds the following path in drivers/power/supply/qcom_battmgr.c:

1. Subscribe to PMIC notifications, then enable AP permission 17 and OTG switch 18.
2. Receive OTG-enable notification 0x50 for an attached sink.
3. Set boost current property 64, then enable VBUS property 24.
4. Disable property 24 after OTG-disable notification 0x51.

UCSI retains the data role. A freezable worker handles the supply requests.
AP17/SW18 are preparation, not the complete VBUS supply implementation.
The phone r220 tested those two permissions only: it did not exercise 24/64.

The reference
[README](https://github.com/yzddmr6/onepluspad-2pro-mainline/blob/4cab38c79b24548e0afba29c6c710230c3692e31/README.zh-CN.md#L122-L123)
reports direct USB-C-to-A adapter operation powered by the tablet, two
successful USB-stick insertions/mounts, and NTFS desktop filename write/read.
UAS disks remain untested there. These are the reference project's reports,
not acceptance results for the phone.

## Phone evidence

r220 completed all 12 combined phases in one RAM boot at guest uptime
259.04 seconds. Native host/source, a partner, xHCI/root hubs and exact
AP17/SW18 ACTIVE were observed for 60.522 seconds. No external peripheral
or storage block appeared, and no media bytes were read. Firmware cleanup
ended RESTORED with independent AP17/SW18 zero reads; Android's seven
baseline keys matched. See R220-HARDWARE-RESULT-20261031.json.

The archived effective phone runtime DT and all 22 inspected phone DTBO
entries specify PMIC OTG source 0 and boost-current limit 1250 mA. Thus the
current limit has phone provenance; it need not be borrowed from the Pad.
This is not a voltage measurement and does not prove the failure's root cause.

USB_STORAGE and BLK_DEV_SD are built in; USB_UAS, EXFAT_FS and NTFS3_FS
are enabled as modules. The observed failure precedes external-device
enumeration, so filesystem changes cannot yet explain or fix it.

## Integration boundary and next step

Retain the working phone kernel and all existing functions. Do not upgrade
the entire kernel or import Pad calibration to obtain this one supply path.
The new separate, default-off, GET-only diagnostic for properties 24/64
shares serialized transport, exact reply matching and timeout poison,
without widening the established 17/18 setter or adding a general setter.
It exposes two root-readable attributes only when the immutable boot parameter
qcom_battmgr.oneplus13_otg_supply_read=1 is explicitly present. Only the
manual USB joint-test alternative adds it; default/parent images reject it.
Reading attributes manually is required;
ordinary boot generates no added requests. The exact notification decoder
is tested offline but is not yet connected to a supply worker.

The property wire has no transaction identifier. Timeout poison prevents
reuse after an ambiguous request; it cannot identify a delayed duplicate
successful response during a subsequent request for the same property.
This read-only diagnostic does not prove remote freshness or supply rollback.

No explicit vendor GET24/GET64 call or successful phone firmware readback
has been found. A generic GET helper does not prove those properties readable.
A reversible supply candidate must first observe VBUS24=0 and save the
actual current64 value; unreadable/failed baselines mean zero new SETs.
Current restoration must use the saved value, not an assumed 1250 mA.

A later bounded supply candidate needs exact owner32778/type2/opcode7,
16-byte notifications and full 32-bit 0x50/0x51 matching. The historical
notification low-byte mask must not admit 0x150 as 0x50. Subscribe and arm
before physical attachment; bind service epoch and local event generation.
Detach, deadline and service loss permanently cancel the boot's enable
eligibility. Current-setting failure must prevent boost enable. These phone
requirements differ from the reference's persistent operating policy.

The reference source alone does not authorize or qualify phone supply
mutation. Bind the exact new image and combined USB/GNSS/camera plan before
testing; retain the owner's explicit NFC skip. No partition/media writes.

## r221 phone diagnostic result, 2026-11-01

One reviewed combined RAM round now establishes manual GET24=0 and GET64=0.
Both succeeded, with the old lease IDLE/unused/clean before and after.
No USB setter/cable change was requested; GNSS/camera continued after the
clean diagnostic and Android returned with seven matching baseline keys.
This addresses the earlier unknown readability, but proves neither mutation
rollback nor electrical supply or external-device I/O. Save actual current0,
never substitute1250 as the restoration baseline. The wire freshness limitation
still applies. See R221-HARDWARE-RESULT-20261101.json.
