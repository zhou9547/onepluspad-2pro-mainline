# Phone WiFi SAR wire support draft

Codex implements a transport-free codec under GPL-2.0-only. It is a new phone
adaptation component, not a power policy, driver integration, or radio acceptance.
No sockets, device operations, firmware commands or phone files are accessed.

The protocol is pinned to OnePlusOSS/
android_kernel_modules_and_devicetree_oneplus_sm8750 at
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3. `sources.json` records exact public
file hashes. The build fetches these public sources, preserves their license
headers, and compiles the actual extracted `send_sar_limit_cmd_tlv` function
with a fake transport as an independent byte-for-byte oracle. Its original
copyright and license remain in the fetched source and generated oracle.
No private firmware, calibration, identifiers or credentials are included.

QCA vendor USER=6 and V2=7 map to WMI USER=7 and V2=8. QCA NONE=5 disables
SAR; this codec rejects it. BDF selectors are translated explicitly. The
single-message encoder validates every row before modifying output; the
decoder rejects extra/truncated rows, unknown bands, duplicates and disabled
or unsupported selections. GET values are half-dBm limits, including when
the selection is V2; they must not be compared directly to V2 profile indexes.
Result parsing returns the actual firmware result separately from parser
success. Capability versions remain unmodified, including unknown values.

The vendor TLV table spells the GET row tag differently from its enum. The
codec uses numeric tag710, cross-checked against the enum and the kernel tag;
it does not silently copy that spelling mismatch into a driver.

Still required: ath12k WiFi7 integration, firmware capability/response collection,
serialization across queries and firmware restart, exact phone BDF/regdb and
firmware delivery, a phone-specific effective policy, enforcement before scans,
and current-rootfs scan/authentication/DHCP/verified-HTTPS acceptance. Earlier
run66 network traffic used reference inputs and cannot substitute for this.
The current phone candidate and all prior stop ledgers remain unchanged.
