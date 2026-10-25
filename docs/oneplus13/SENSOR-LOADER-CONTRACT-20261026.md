# Phone sensor loader contract review

The extracted owner's phone `sns_reg_config` is byte-identical to the original
Pad project's pinned configuration text, SHA256
`475c964bc19126f88696c2917cc5ea1924f1e210deb9c21aab8edced6a79b989`.
Its six socinfo file names and the two property names match the existing narrow
hexagonrpcd shim. Reuse that shim and the original vendor/ODM file mapping;
do not implement a generic Android property service.

`review-sensor-loader.py` checks only saved host inputs. It preserves vendor
`json.lst` and ODM `json_list`, as the original project does. The vendor list has
133 occurrences,132 unique entries and one existing duplicate; seven named
files are absent in the source partition. The phone ODM list has20 entries,
all present. The tool records these facts without rewriting the ROM, inventing
missing files or treating enabled template names as populated sensor identity.
Five synthetic negative/positive input tests pass.

Matching configuration text does not prove the phone DSP reverse-RPC ABI.
The build of the shared ARM64 userspace and its8 hexagonrpc/7 libssc tests was
already accepted offline at Actions40198265425. That does not supply this phone's
per-unit registry/calibration, socinfo values or sample streams. The original
Pad mount matrix and measured sensor declarations are not phone defaults.

The original project reads the registry at first INIT_ATTACH_SNS. Its ADSP also
serves audio/battery/USB-C, so an attach must not be attempted with missing inputs
and ADSP must not be restarted to try another registry. No phone attach, sensor
daemon activation or stream was performed here. These prerequisites remain
separate from the later combined physical-orientation/accuracy owner session.
