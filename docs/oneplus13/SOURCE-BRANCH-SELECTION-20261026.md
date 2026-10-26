# Source branch selection

`oneplus13-platform-handoff-20261026` contains the latest public WiFi and
platform gates, but its tree is a thin overlay. A kernel build on that base
failed because core public inputs such as `tools/oneplus13/package.py`,
`tools/oneplus13/verify.py`, device source pins and C tests were absent.

`oneplus13-bringup` contains the complete kernel/userspace source tree. The
`oneplus13-run88-current-image-v2-20261026` branch therefore starts from
`oneplus13-bringup` and overlays the latest platform handoff tree plus the run88
acceptance changes.

This combination preserves the complete compilable source baseline while
retaining the newest public WiFi qualification and exact-image assembly logic.
No private data is included in either overlay.
