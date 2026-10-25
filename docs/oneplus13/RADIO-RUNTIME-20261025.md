# Desktop radio runtime, 2026-10-25

Run51 returned to Android in221.5s with seven sampled baseline keys matching,
no partition writes or manual recovery. The owner confirms the peer received
the Bluetooth test file. This accepts one real pairing/file-transfer path,
not every Bluetooth profile or long-duration throughput.

WiFi automatic acceptance stopped at the scan request. NetworkManager logs
show failure to D-Bus activate wpa_supplicant. Independent host inspection of
the actual SquashFS confirms the executable, system activation file and systemd
unit are absent. The run did not reach password authentication, DHCP or traffic.
The later postcheck timed out at the device-query phase and requested recovery.

The original desktop builder starts from pinned Ubuntu Desktop ISO layers.
The separate phone builder starts from Ubuntu Base and uses an explicit seed
with --no-install-recommends. Having NetworkManager installed does not prove
that its recommended WiFi authentication service or GNOME file sender exists.
The phone seed now explicitly includes wpasupplicant, iw, bluez,
gnome-bluetooth-sendto and bluez-obexd. The rootfs verifier checks every seed,
the actual ARM64 networking/client ELF files and supplicant/OBEX activation
contracts. This changes only the phone build; normal Pad assembly is preserved.

An additive RAM overlay is separately prepared against the same signed Ubuntu
snapshot. Its14 package SHA256 values are bound to authenticated indexes; the
working BlueZ core is excluded. Three ARM64 software startup checks pass in
QEMU. On a private host D-Bus, the actual ARM64 supplicant acquires its service
name and answers the manager Interfaces property, with no wireless interface.
This verifies software readiness, not real radio authentication.

The next RAM plan delivers these components and checks the supplicant service
before the explicit WCN module probe. Automatic WiFi checks the supplicant bus
endpoint, device state, one scan, target authentication, IPv4 default route and
interface-bound HTTPS. Owner WiFi GUI regression is offered only after automatic
acceptance. Raw diagnostics and credentials are excluded from public results.
Eight offline fake-process checks cover timeout, absent target/service,
unavailable device, secret-file cleanup, log privacy and failed HTTPS.

Interaction postchecks reuse the already collected WiFi result rather than
repeating device queries. A wireless timeout skips the interaction window and
requests early recovery; serious kernel errors halt further runs. The existing
RAM/storage guards and recovery deadlines remain. No new phone run is authorized
by this document. A refreshed complete-rootfs Actions build is required before
claiming that a new base image has passed its runtime verifier.
