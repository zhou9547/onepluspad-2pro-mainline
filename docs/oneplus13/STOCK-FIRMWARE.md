# Matching stock firmware for the priority boot path

Owner priority is native display, networking, touch and booting GNOME. The
existing images are RAM diagnostics, not a persistent desktop installation.
Current phone access remains read-only; no reboot or boot/flash test is allowed.

The owner's saved/current build is PJZ110_16.0.10.501(CN01). Root metadata gives
exact sizes/hashes for graphics firmware and WLAN modem/ODM inputs. Public
Lineage firmware, its two older BDF revisions, and Pad/ROCKNIX data do not match
the owner WLAN pair; do not substitute them. Three ordinary graphics firmware
files match, but the signed zap differs from the public reference.

The matching official OTA catalog record has size8975091784 and MD5
6bd2956979795c267a062462ad7fc50f. Earlier downloadCheck2306 responses were caused
by missing client headers. With documented okhttp/3.12.12 and
userId=oplus-ota|16002018 headers, the official gate returns302 to its official
CDN. No phone identifiers or credentials are needed for this public download.

Prepare a separate Actions extraction job: pin the external payload tool source,
read only vendor/odm/modem partition ranges, verify complete partition SHA256
against payload metadata, extract only the needed generic OTA firmware, and
require exact equality to observed owner hashes before making a firmware bundle.
Signed URLs must remain inside the process; a loopback-only range proxy may
refresh expiring CDN signatures. Do not download or transfer firmware from the
phone. Do not include private SPR coefficients or per-unit calibration.

The selected Go tool4cc6ef94039470d659e4199c67f76d8962280023 has uint64 payload
offsets and HTTP ZIP support; build it with its pinned go.sum/Go1.26.0, use its
verification mode and independently check partition sizes/hashes. A reviewed
Python alternative used uint32 offsets and was rejected for this >4GiB OTA.
No extracted partition image belongs in the final firmware artifact.

Matching files do not establish active board ID, SAR correctness, firmware
authentication or working radio/display. Keep those hardware checks explicit.
The eventual GNOME handoff and storage/install design remain separate work.

Extraction run40001494126 (c60d1cd) failed before payload metadata: the official
gate resolved, but CDN TLS handshakes timed out on the Azure westus2 ARM runner.
No partition or firmware mismatch was observed, and no bundle was produced.
The next controlled test uses macOS Actions networking, with an eight-byte
exact-range TLS preflight before the payload tool. TLS verification remains on;
there is no longer timeout or unconditional network retry workaround.

Sources: [OTA client header documentation](https://github.com/0x8008/otapulse-web),
[pinned extraction tool](https://github.com/xishang0128/payload-dumper-go/tree/4cc6ef94039470d659e4199c67f76d8962280023).
