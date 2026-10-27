# Owner-authorized qualified hardware data

The owner explicitly authorized publication of the firmware and calibration on
2026-10-27, excluding credentials, keys, personal data and device identifiers.
These 74 payloads are the unchanged hardware data used by the successful run90
RAM WiFi/HTTP acceptance, except that old `/chosen/bootargs` were removed from
the calibrated DTB. The packager generates new image hashes and session
parameters; no old test session, network configuration or USB serial is needed.

- 58 ADSP files: the phone's verified signed stock firmware, retained under the
  historical `qcom/sm8750/erhai` path required by the qualified DT. That directory
  name does not mean these bytes were taken from a tablet.
- Four GPU files: verified phone stock firmware (including product-signed ZAP).
- Nine WLAN/Bluetooth files: the exact previously qualified legacy reference
  set. These are deliberately not relabeled as new phone-stock radio firmware.
  Source provenance and hashes are in `packaging/firmware-manifest.json`;
  ROCKNIX extra-firmware is pinned there at
  `2b7207cfcb80c53c09dc6e04165789ecaf2d3348`.
- `display-profile.bin`: the validated 176-byte AA569 SPR data profile.
- `calibrated.dtb`: the qualified ABL/memory/device tree for the owner's
  **PJZ110 24 GB** variant, compatible only with the public native DTB hash in
  `manifest.json`. It contains no serial-number or MAC-address properties.
- `boot-geometry.json`: boot header address geometry, not a unique identifier.

Firmware remains proprietary data; the original vendor terms apply. Inclusion
does not relicense firmware under the repository's GPL. No raw partition images,
factory identity stores, persistent WiFi settings or cryptographic private keys
are included. Firmware signatures/certificates are public verification data,
not private signing keys. Every payload has a size and SHA-256 in the manifest.

This dataset reproduces the qualified experimental RAM configuration. It is not
a generic image for other RAM variants and does not qualify audio, cameras,
sensor streams, suspend or a new SAR transport. It does not authorize flashing.
