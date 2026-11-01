# Direct USB storage milestone

The r228 combined RAM round qualifies one directly attached USB storage device
with NTFS read-only I/O. The exact image is source
`d0c8d20ee66ca73397f8c1abf6b915b9d05a8678`, Actions
[41258076551](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/41258076551).
Boot SHA256 is `e4809cfd064fc4688a88e54b62a38c3bf753708bc5a54024a6a0a0f7b6c278bb`.
See [the sanitized result](R228-USB-HARDWARE-MILESTONE-20261101.json).

The phone observed real Type-C host/source and its exact DWC3/xHCI root hubs,
then set current64=1250 and VBUS24=1 through the fixed kernel supply lease.
A real external USB storage node appeared. An ancestry- and descriptor-checked
O_RDONLY read returned 4096 bytes. The same verified USB block was mounted
read-only through an inherited descriptor; a 4096-byte regular-file prefix was
read and the filesystem unmounted successfully. No media bytes, filenames,
digests or volume identities are published.

The bound driver restores 24->64->18->17. All four actual saved zero values
were read back, the lease ended RESTORED/used1/clean, and actual device/sink plus
the UDC returned after reconnecting the PC cable. The two filesystem modules
loaded by the probe were removed; preexisting modules and the module policy
were preserved. Android returned with all seven baseline properties equal,
one RAM boot and zero reported partition writes. There was no firmware UNKNOWN.

All 13 planned phases completed. After USB cleanup the same boot attempted
GNSS and a real camera frame, then repeated actual 5 GHz association at 5220 MHz
and HTTPS HTTP 200 with certificate result 0. GNSS still returns START
GeneralError46 with clean STOP, and camera still produces no real frame with
clean teardown. NFC remains owner-skipped.

## Runtime delivery and physical timing

The tested supply helper and filesystem module helper are now installed as
manual-only, source/hash-bound peripheral runtime files. Their function bodies
match the hardware-tested overlay; the export adds only license/shebang lines.
The ordinary boot has no supply opt-in and nothing automatically runs these
helpers. Their RAM configuration must contain the exact image's module hashes.

The operator card requests an actual cable swap. A live host/source observation
gates supply start; chat acknowledgement is an observation, not a power-control
grant. This avoids losing the unchanged 120-second arm lease while a chat reply
is in flight. The same principle waits for actual device/sink on cable return.
The 120-second active lease, poison-on-error behavior and exact saved-value
restore remain unchanged. No DWC3 role write substitutes for physical attachment.

NTFS requires its delivered module. The probe loads only the two fixed,
hash-checked exfat/ntfs3 modules, after verifying the exact no-automount and
read-only udev rule. Ownership is recorded before insertion so a timed-out
insertion still has cleanup. Mount uses ro/nosuid/nodev/noexec, checks the
mount's device number and read-only state, and retains the pinned descriptor
through unmount. Unknown unmount or module removal halts later targets.

## Remaining scope

This is bounded direct-storage qualification. Expansion docks/hubs, USB HID
events, media writes, other filesystem formats and default automatic OTG
policy remain unqualified. The owner intends to try an expansion dock next.
Exfat module loading is tested; exfat filesystem I/O is not.

The firmware wire still lacks transaction IDs, so exact readback does not prove
reply freshness. A future repackaged image needs its own source/image-bound
evidence; this hardware result must not be relabeled as testing that image.
