# OnePlus 13 status

This is an offline bring-up project. No phone has been connected or booted.
The Pad's support table and installation instructions do not apply to this phone.

| Component | State | Evidence / limitation |
| --- | --- | --- |
| SM8750 platform | Source available | Pinned reference kernel in device source manifest |
| Phone DTB | Source available | Adapted from index986's pinned OnePlus-13-WIP board |
| Kernel / modules | Pending build | Dedicated Actions workflow |
| RAM diagnostic image | Pending build | No persistent installer; all discovered block devices read-only |
| USB NCM / console | Pending hardware | Build checks cannot prove enumeration |
| Display | Pending hardware | Firmware framebuffer reference; no phone panel initialization |
| Touch | Driver port required | S3910 vendor HBP node does not imply a mainline driver exists |
| GPU | Pending hardware | SoC driver present; phone firmware closure not established |
| Wi-Fi / Bluetooth | Pending hardware | Phone wiring and firmware need device-specific confirmation |
| Battery / charging | Pending hardware | No charging support claim; ADSP not started by diagnostic profile |
| Audio / sensors / modem / camera | Pending port | Pad board configuration cannot be reused |
| Persistent install / dual boot | Not enabled | Requires stock recovery set, partition evidence and hardware validation |
| Ubuntu 26.04.1 GNOME userspace | Building | Separate native ARM64 workflow; no phone firmware or default credentials |

Next: compile and inspect the candidate through GitHub Actions, then collect the
phone's stock FDT and boot metadata before any device experiment.

The source comparison and first hardware experiment are documented in HARDWARE.md.

Device state: user-owned phone; untouched. Operator: user only.
