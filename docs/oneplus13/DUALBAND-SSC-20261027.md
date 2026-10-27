# Joint 5 GHz and SSC metadata continuation

Baseline: `570428aeddf591b518112e66b239cf07a643f65a`, the complete Actions
image accepted by run91 for 2.4 GHz association, DHCP and LAN HTTP 200.
Run88's physical display/touch/GPU/desktop and Bluetooth receipt are historical
evidence. They remain regression requirements for a new candidate.

## WiFi

Private runtime credentials may select `band: "a"` for 5 GHz or `band: "bg"`
for 2.4 GHz. NetworkManager receives the matching band constraint. The verifier
then reads the actual link frequency with `iw dev <interface> link`; a missing,
ambiguous, wrong-band or failed observation stops before traffic acceptance.
Association, a matching actual band, IPv4/default route and interface-bound
LAN HTTP 200 must all pass. A successful 2.4 GHz connection is never reported
as 5 GHz acceptance. Credentials and raw link output are not published.

`oneplus13-wifi-radio-report.py` reads channel capabilities and regulatory
domains without requesting a scan or setting a country/SAR value. Its numeric
report distinguishes disabled, passive/no-IR and DFS channels. This is needed
to diagnose an invisible 5 GHz target before choosing a driver change. No
unproven firmware swap, channel-flag bypass or power-policy SET is introduced.
External DNS/ping/HTTPS diagnostics now require explicit runtime opt-in;
the current owner's default remains LAN HTTP only.

## SSC

Run81's saved stderr contains `g_value_set_boolean` / `G_VALUE_HOLDS_BOOLEAN`
assertions. The pinned libssc registers `available` as a string but its getter
writes a boolean. It similarly registers stream type/sample rate as strings
while returning uint/float. A phone-only patch corrects all three declarations.
The native regression compiles the actual sensor implementation and checks
false/true/false availability, numeric property reads and adjacent memory
canaries without QRTR, measurement commands or a device.

The original two libssc packaging patches and the one-way metadata send guard
are unchanged. This explains why the previous availability observation was
unreliable; it does not prove that all sensors or a mount matrix are correct.
The all-zero mount-matrix warning is separate and remains unresolved.

The complete-image workflow builds the isolated probe at the same integration
commit as the kernel/GNOME/Mesa. Release and ASan/UBSan each require the new
property regression, the policy test, real send-boundary rejection and original
delivery test. Packaging checks source identity and every archive entry, stores
the probe in `/usr/lib/oneplus13-ssc`, and verifies its actual SquashFS bytes.
It installs no sensor service, registry or measurement policy. Discovery still
requires separately reviewed RAM-only private registry/file-server staging,
one attach, a hard deadline, clean stop and the existing metadata-only wrapper.

## Joint hardware acceptance

Prepare one new single-use RAM plan after the Actions artifacts are downloaded
and their hashes verified. Combine 5 GHz association/DHCP/LAN HTTP, a 2.4 GHz
regression, guarded SSC metadata discovery and preserved-feature checks.
Do not start a separate phone boot for each target. Use the registered device,
per-connection RAM identity, immutable physical storage, staged recovery timers
and seven Android baseline properties. No flash or persistent installation.
No new hardware success is claimed by the source or compile checks.

Follow the original project's next sequence: independent WCD microphone
capture and SSC/accelerometer before ambient light/compass/gyro integration;
speaker playback still requires phone-specific protection and calibration.
