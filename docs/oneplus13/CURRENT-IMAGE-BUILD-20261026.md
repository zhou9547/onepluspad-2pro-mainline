# Current complete source-built RAM image

See [SOURCE-IMAGE-20261027.md](SOURCE-IMAGE-20261027.md) for the current build.
The source-image workflow now includes the owner-authorized, scrubbed firmware
and calibration and emits `complete-ram-image-<commit>`. It does not download
historical Linux images or require local private build inputs. Credentials and
physical device identifiers are excluded. QEMU is optional, off by default.

Actual run90 WiFi/HTTP acceptance passed; new CI artifacts are not falsely
relabeled as that test. These are experimental temporary RAM images, never
flash or repartition instructions. Audio/camera/sensor streams remain gated.
