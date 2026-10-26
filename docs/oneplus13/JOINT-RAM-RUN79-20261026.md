# Run79: joint RAM acceptance and remaining gaps

One bounded RAM session combined three new targets with the established platform
regressions. It automatically returned to Android in131.7 seconds with all seven
baseline samples matching. No flash, partition change, persistent installation
or manual recovery was used. Existing stop records remain preserved and this
single-use session is now sealed.

| Target | Actual result |
| --- | --- |
| Synthetic ARM64 RAM/wire failure cases | Both existing C tests passed on the phone under UID65534 with devices hidden/denied; the unit exited inactive. They used synthetic data and a fail-on-call FastRPC mock. |
| Exact camera metadata input | The staged fixed filename was actually opened read-only. This proves the input mapping, not camera operation or image capture. |
| Bounded reverse file service | One successful attach,28-second window,2594 successful invokes, zero write refusals/unsupported dispatches and clean service stop. |
| Display/GPU/desktop | One display activation, hardware pixel readback and ordinary-user desktop software checks passed. No owner visual observation was requested. |
| Platform/recovery | Platform health and observed block-device read-only checks passed;925 private data files and module policy were unchanged; automatic Android return and seven baseline comparisons passed. |

Before this boot, the same batch passed native ARM64 Actions40275291041:
14 release C tests,14 ASan/UBSan C tests and53 Python checks. Full exact-rootfs
QEMU exercised both synthetic binaries in the actual low-permission systemd
sandbox and reached its automatic deadline/reboot. The executed QEMU ramdisk was
unpacked to confirm the embedded helper, test archive and manifest bytes.

Production runtime ELF bytes matched the previous batch; the synthetic tests
were exported separately. The kernel, boot image, rootfs and phone recovery
deadlines remained unchanged. The added private camera input was not uploaded.

Run78 stopped before any reboot: an old property-only host transport rejected
the proposed battery query. It sent zero RAM boots and Android never changed.
Its stop was retained. The correction uses a separate exact six-second read of
stock battery status, without expanding the general transport interface; six
host fixtures cover its command, bounds and failure cases. Run79 then checked
battery health, charge and temperature before rebooting.

Missing lookups decreased from31 to30, all matched to saved requests:27 names
from the stock configuration list and three OEM/DSP probes. The camera metadata
input gap disappeared. The configuration list is unchanged; no '#' was removed
and no files or successful responses were fabricated.

Full file-service acceptance and sensor samples remain incomplete: the30 lookups,
dynamic-library loading/release semantics and DSP release acknowledgement are
still unresolved. RF/SAR policy, audio calibration/protection/backend routing,
haptics, suspend and USB role changes remain gated. Camera functionality is also
unqualified. This session does not reopen those paths or justify repeating the
targets already passed. Continue offline work on the remaining gates and batch
future qualified targets with platform and recovery regressions.
