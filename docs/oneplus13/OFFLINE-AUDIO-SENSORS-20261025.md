# Phone audio and sensor offline increment, 2026-10-25

Superseding 2026-10-26 finding: the saved stock runtime FDT disables every
WSA884x/WSA883x speaker directly or by ancestry, including the WSA macro. Both
AWINIC smartpa nodes are enabled. The run42 candidate's WSA route is therefore
not justified by stock enablement. Its image is held against hardware reuse;
the six controls below describe that experimental route only, not the phone's
stock speaker route. No further WSA streams are justified by this review.

No phone operations are authorized or performed by this increment. The four
previous RAM grants are consumed. New hardware work requires a new owner grant.

## Audio route review

The saved run47 mixer dump shows WSA RX0/1 MUX and WSA_RX0/1 INP0 selecting ZERO,
with both SpkrLeft/SpkrRight DAC Switch controls off. The experiment changed only
the FE-to-BE boolean pair. Opening that FE route fixes the immediate open EINVAL,
but does not establish the six remaining macro/slave routing controls.

The local mainline q6apm/WSA/SoundWire source confirms that the WSA macro routing
and the codec's port_enable array govern separate parts of the path. A complete
route is therefore an outstanding configuration prerequisite. This is not proof
that all observed EIO or bus-clash errors are caused by the missing controls.

`tools/oneplus13/review-audio-route.py` parses saved controls, checks names, enum
choices and boolean arity, and reports an exact restoration value. It has no
apply command or device IO and always keeps the live-stream gate closed. Six
offline checks cover the actual fixture, missing codec control, wrong-board
enum, stereo arity, gain exclusion and refusal to equate route completeness
with permission to stream. It does not change any amplifier or DSP gain.

The sanitized fixture holds only seven generic route controls, not identifiers,
factory coefficients or speaker tuning. Run the reviewer with:

```sh
python3 tools/oneplus13/review-audio-route.py \
  --dump devices/oneplus13/test-fixtures/audio-mixer-incomplete.txt \
  --output /tmp/audio-route-review.json
```

Vendor review is pinned to OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750
at d50b305f7da9e14715a25120a4ac7b1a4b8b97c3; four audio source blobs were checked
against the Git tree. Vendor `qcom,swr-wsa-port-params` describes per-use-case
offset/lane pairs and cannot be copied byte-for-byte into mainline port fields.
Mainline/QRD references use yzddmr6/linux-sm8750-erhai at
7a81d184e3098624d4342d8f4eff5e23674bcc9f. No bus/clock/power workaround is added.

## Phone sensor inputs

Targeted read-only host extraction of the existing PJZ110 OTA vendor/odm EROFS
images recovered171 sensor-ROM files. All20 ODM index entries exist; the broad
vendor index includes seven filenames absent from the original vendor directory.
No files were fabricated. The phone indexes name BMI26x, AK09919 and TCS3720;
the existing OPD2413 Pad ROM registry is not a phone replacement. ROM files and
image/file hashes remain private on the host. Per-unit calibration and runtime
registry are not included and were not read from the phone.

## Board-independent userspace build

The original builder is reused, with one host preflight correction: native ARM64
does not require a qemu-aarch64 binfmt registration. Other hosts retain the
existing binfmt requirement. Normal Pad packaging behavior is unchanged.

Actions40198265425 succeeds on native ARM64 at
1743010bd9deb1220323acbb99913ca12513b994. Eight hexagonrpc unit/mock tests and
seven libssc delivery/encoding tests pass. The resulting hexagonrpcd, ssccli,
iio-sensor-proxy, libhexagonrpc and libssc ELF files were independently checked
as64-bit ARM64 and their hashes match the artifact manifest.

The downloadable archive contains only the private-prefix software binaries
and libraries. The reference Pad ROM, firmware and package install hooks are
excluded; phone ROM/calibration is not uploaded. This is an offline software
input, not an installable phone package or evidence of real SSC sensor streams.
Phone DSP compatibility, platform identity inputs, loader/index semantics and
RAM-only calibration/registry policy remain gates before activation.
