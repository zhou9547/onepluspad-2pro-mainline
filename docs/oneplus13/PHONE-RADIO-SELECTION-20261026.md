# Phone radio selection and remaining RF gates

A bounded passive Android boot-log read now shows the effective WLAN selection:
`peach/bdwlan.elf` and `peach/regdb.bin` are found in `/odm/etc/wifi/peach/`
and downloaded by CNSS. Their logged lengths are125328 and24278 bytes. These
are the exact phone OTA files already independently matched to stock hashes.
The log reports HW_XPA=1, CalDB=0 and that a separate calibration database is
not required by this BDF. This is actual selection evidence, not a guess from
the filename or a fallback that happens to let a driver boot.

Android also runs a separate wifisar service in response to its vendor SAR
property. One vendor driver line reports a SAR-flag parsing failure; that line
alone does not establish which later power policy was applied. The mainline
loader's ability to download an ELF board file does not reproduce this service
or establish the phone's effective transmit-power envelope.

The exact saved ODM wifisar script and SAR XML were extracted without execution.
The XML uses vendor command146 with selector/spec/band/chain/modulation/power/
power-index fields. The script reads its runtime property and an optional
wifisar.cfg, which is absent in the verified saved ODM; its fallback values
must not be converted into assumed phone safety limits. Absence in that image
does not prove absence of a runtime overlay or of other HAL power controls.
Pinned vendor SAR source confirms the separate user-defined/index selectors.
The pinned vendor API now establishes USER half-dBm units and a distinct V2
profile-index namespace. Effective firmware policy/acknowledgements and
Linux-facing enforcement remain open; see SAR-PROTOCOL-GAP-20261026.md.

Pinned ath12k source supports ELF-versus-binary board download and uses a256KiB
WCN7860 board limit. Exact/default board-2 and board.bin/regdb fallbacks exist;
they must not be used to force unverified board/power selection. WLAN/BT remain
disabled in the current isolated candidate until exact firmware, board,
regulatory and SAR/power paths are jointly reviewed. Earlier scan/HTTPS and
owner Bluetooth-receipt observations remain historical functional evidence
using reference inputs, not phone-specific RF acceptance.

This collection performed no scan, firmware load, service control, reboot or
device-side write. Android baseline matched before/after. Raw boot logs and
per-unit values remain private. Bluetooth's effective firmware/address/power
selection is still unresolved; no new radio acceptance is claimed.
