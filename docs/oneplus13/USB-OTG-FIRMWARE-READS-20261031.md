# OnePlus 13 USB firmware gate observation

The combined r207b RAM round completed in 288.55 seconds and returned to
Android with seven baseline properties matching and zero partition writes.
Camera chip-ID, modem preservation and 5 GHz control checks passed. This
does not qualify real camera frames. GNSS event registration returned
InvalidArgument before start. NFC RF acceptance is skipped at the owner's
request because no physical tag is available.

For USB, real xHCI and root hubs existed before the cable swap. Detaching
the computer caused UCSI to report device/sink, partner absent and xHCI
removal. Connecting the OTG drive produced no observed partner or peripheral.
Device role and cleanup were confirmed before Android recovery. Therefore
controller creation alone is insufficient evidence of a working OTG path.

## Protocol source and scope

OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750 at
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3 documents separate legacy USB
GET 0x32 / SET 0x33 properties AP_ENABLE 17 and OTG_SWITCH 18 in
vendor/oplus/kernel/charger/v2/charger_ic/oplus_hal_adsp.c and .h.
The soccp branch instead uses OEM SET 0x300 / GET 0x301 and properties
12/13. These are different protocols, not interchangeable alternatives.
No blind OEM fallback or SET is implemented.

The new kernel interface exposes only root-readable 0400 attributes on
oneplus,dodge: oneplus13_otg_ap_enable and oneplus13_otg_switch. It does
not query automatically and has no store method. The existing battery
client and request mutex are reused; notification enable now takes the
same mutex. Optional reads have their own completion and error state,
with a spinlock protecting pending lifecycle and response publication.
Exact response matching checks owner, type, length, opcode, property,
firmware result and boolean value. Late optional responses cannot complete
ordinary battery requests. Timeout or a service loss after UP disables
optional reads for the rest of that boot, because no transaction ID exists.

The USB helper reads these two fixed attributes once before role testing.
Each cat has a three-second subprocess timeout; missing/error/invalid values
remain unknown. The new plan must include the additional six-second budget.
Kernel operations are not guaranteed to obey host wall-clock timeouts.
No gate is changed and this candidate does not claim to fix OTG electrical
behavior. Live legacy support must be established before designing a
separately reviewed, bounded switch lease and verified rollback.

An independently reviewed Android read observed otg_switch=0. Absence of
soccp output in that bounded observation does not prove the property absent.
Raw device data and identities remain private.

## Offline qualification

Eight actual-header GCC ASan/UBSan cases, eight inventory cases and 23 USB
regressions pass. Those tests do not establish firmware compatibility,
electrical OTG support or physical enumeration. Full kernel/Actions build,
exact artifact readback and a fresh reviewed joint plan precede another
temporary RAM round. Existing consumed ledgers remain consumed.
