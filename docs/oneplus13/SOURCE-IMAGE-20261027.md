# Fresh source image build

Run `oneplus13-source-image.yml` (or the `oneplus13-current-image.yml` entry
point) at this branch. Kernel, Ubuntu GNOME and A830v1 Mesa build in parallel;
the image job combines only products of that same workflow and commit. No old
Actions image or kernel artifact is an input. The source lock restores the
SPI-controller-compatible touch driver and the two ADSP patches used in run88.
Ubuntu uses the signed snapshot in ubuntu.json; kernel and Mesa sources and
patches use their recorded immutable pins. This is a functional rebuild, not a
promise that build timestamps and compressed bytes match yesterday's image.

Local native ARM64 equivalent, in a disposable build VM:

```sh
bash tools/oneplus13/source-image.sh kernel
bash tools/oneplus13/source-image.sh rootfs
bash tools/oneplus13/source-image.sh mesa
bash tools/oneplus13/source-image.sh assemble
```

`out/oneplus13-source-image` contains the matched SquashFS; kernel output is
`out/oneplus13`, and desktop handoff/QEMU evidence is in
`out/oneplus13-source-desktop`. GNOME, settings, screen keyboard, touch driver,
Mesa, WiFi authentication and Bluetooth OBEX components are retained. Modules
are bound to the newly compiled kernel release. Unqualified audio, camera and
sensor streams are not newly enabled.

Qualcomm firmware is proprietary executable input, not Linux source code.
The public image intentionally excludes owner-specific signed firmware,
display profile, ABL memory calibration, identities and network configuration.
Final per-device RAM packaging consumes these existing verified inputs locally.
They must never be uploaded into Actions, Git, logs or build artifacts. A claim
that the public source tree alone can compile those private/proprietary inputs
would be false. The reproducible portion is the complete system software build;
the final hardware-specific image additionally needs the private local inputs.

Local packaging, on Linux with SquashFS tools and root permissions:

```sh
sudo python3 tools/oneplus13/package-source-local.py \
  --kernel /build/source-kernel --desktop /build/source-desktop \
  --rootfs /build/source-image --private-inputs /private/phone-data \
  --output /private/fresh-ram-candidate
```

The private data manifest (`ONEPLUS13_PRIVATE_DATA_V1`) binds every firmware
file, the 176-byte checked display profile, calibrated DTB, boot addresses and
the compatible public DTB hash. No historical kernel, rootfs or package overlay
is accepted by this packaging step. It verifies that the public components
share a source commit and passed the complete rootfs QEMU handoff/deadline.
The output includes matching modules, fresh Mesa, authentication/OBEX services
and the qualified firmware; the boot image includes the matching native module
closure. An explicit RAM-only `oneplus13-qualified-bringup --all` starts the
previously qualified desktop, touch, radio and Bluetooth path; `--wifi` selects
only the automated network test. Neither command flashes or installs anything
persistently. Calibration compatibility is refused when the public DTB changes.

Build success and QEMU checks do not prove hardware WiFi. The next acceptance
uses the newly built image in temporary RAM: association, DHCP/route and an
interface-bound HTTP response from an owner-supplied private endpoint. HTTPS is
diagnostic. No phone flashing, partition changes or persistent installer.
