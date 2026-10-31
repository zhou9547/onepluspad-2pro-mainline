# Preserve the installed desktop and WiFi regression path

5 GHz is already working: r191 verified its control channel at 5240 MHz.
This continuation does not classify either WiFi band as unfinished RF work.
Remaining physical targets are GNSS real fix/start/stop, NFC physical tag,
real S5KJN5 pixels and USB peripheral enumeration with read-only I/O.

## Reproduced delivery defect

package-source-local.py copies the source desktop and WiFi helpers into
/usr/libexec with the oneplus13- prefix. ram-desktop-check.py still attempted
to import automatic-wifi-check.py from that installed directory. Merely
verifying the two installed hashes did not exercise this import boundary.

load_wifi_helper now selects oneplus13-automatic-wifi-check.py when the
checker itself has its packaged name. Source execution keeps the existing
source sibling. Missing packaged input raises FileNotFoundError even if an
unprefixed file exists; an old host overlay cannot satisfy this dependency.
The normal three bound-interface HTTP samples and combined acceptance
requirements remain unchanged.

## Offline validation and boundaries

Three new regression cases perform real imports from temporary directories:
prefixed success with an unprefixed trap, refusal of unprefixed fallback, and
the normal source import. WSL ran 745 full repository tests (five skips) and
587 phone-specific tests (one skip), both successfully. A Windows-wide run
failed on Linux-only dependencies and shell semantics; WSL is the relevant
environment and no phone was contacted by these tests.

r195 Actions 41159270428 succeeded in all five jobs; its exact three archive
digests, 66 installed runtime files, 120 firmware files and native GNSS with
18 dependencies were independently read back. The current change requires
its own Actions source-image milestone before replacing that image baseline.

## Combined round preparation

Use the original project's microphone-before-speaker regression order and
retain its qualified platform, ADSP, WLAN, sensors and desktop bringup.
Early chip-ID/native-video admission constraints still apply before WLAN
and sensor activation. All remaining adaptation goals share one RAM boot
with the mature desktop, audio, sensor, container, IR and suspend checks.

The private runner is under offline review. It must bind the exact source,
image, modules, scripts and unused ledger; verify active recovery timer
readback; attempt modem and policy cleanup despite failures; and confirm
the actual LAN receipt before any request to unplug USB. A new total bound
must be stated explicitly to the owner. Historical phone approvals, old
850/900-second windows and shutdown authority cannot be reused. There is no
new hardware result and no authorization to flash or persistently install.
