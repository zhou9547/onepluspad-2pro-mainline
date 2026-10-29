# Ultrawide mode selection review

r59 repeats strict S5KJN5 chip-ID0x38e5 at7-bit0x2d, runtime suspend and complete
sensor/CCI teardown. It does not stream or identify the stock HAL's selected
module file. Bounded read-only Android kernel history independently includes a
successful dodgeultrawide probe with0x38e5. Other failed/earlier probes include
0x805. The source/board relationship below now explains the ID conversion;
the exact L/S supplier remains unresolved.

The retained C.93 ODM D/L/S module files use Parameter Parser V5.6.1
(2501071548). Their CRC32 footers, four section bounds,60-byte root symbols,
16-byte reference records and referenced array bounds were checked locally.
The724-byte sensorDriverData root and416-byte resolution records yield the
following **inferred schema**, not an authoritative Qualcomm API:

| Template | ID field at root+68 | Resolution records | PHY flag/lane field |
|---|---|---|---|
| D | 0x30e0 | 11 | D-PHY /4 lanes |
| L | 0x805 | 21 | C-PHY /3 trios |
| S | 0x805 | 21 | C-PHY /3 trios |

All three slave-address fields contain8-bit0x5a. The saved full stock FDT gives
CCI0 sensor1 `probe_intent=0x30e0`. The public vendor function
`oplus_cam_sensor_match_id_pre()` reads that property and executes
`sensor_id |= probe_intent` immediately before matching the hardware ID.
Consequently D remains0x30e0 and fails the physical0x38e5 comparison, whereas
both L and S become `0x805 | 0x30e0 = 0x38e5`. This explains the previously
unresolved mismatch and selects the inferred three-trio C-PHY template family.
It does not select L versus S, qualify timings or prove frame capture.
`review-camera-board-map.py` now checks the exact probe_intent and reports
this relationship; missing/changed values are rejected. A fresh run against
the saved complete stock FDT passed all four sensor graph checks.

The retained sensor shared library has an S5KJN5 debug marker and a
GetSensorLibraryAPIs export. Proprietary register tables and executable
contents are not published or installed by this review.

The pinned public vendor match path reads the chip ID, applies the configured
mask/shift and compares it with the supplied ID. Its OEM callback has an HP5
special case. The relevant JN5 adjustment is the separate pre-match OR operation,
not that OEM callback or the post-match compatibility read. Public source pin:
[OnePlusOSS d50b305f](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750/tree/d50b305f7da9e14715a25120a4ac7b1a4b8b97c3).
Relevant files are cam_sensor_core.c, drivers/oplus/cam_sensor_module/cam_link/
oplus_cam_sensor.c and the Oplus camera_extension cam_sensor_custom.c.

The staged public S5KJN5 v6 driver supports a four-lane D-PHY mode. The staged
generic SM8750 PHY and CAMSS path likewise do not yet supply a qualified C-PHY
configuration. The phone's custom vendor PHY register table is a separate
constraint. A D-PHY template cannot simply be selected because it is easier
to drive. The L/S fields plus the source-backed ID match establish the candidate
family, while their layout remains an explicit schema inference.

Next implement a coherent sensor,
PHY and CAMSS graph for that mode, with exact resources and supported APIs.
Only a real frame with validated pixels followed by stop/runtime-suspend/
teardown and retained-feature regression can qualify camera capture. Keep the
default desktop camera-disabled and retain strict0x38e5 identification.

## L/S sequence comparison

A second offline pass checks the exact retained L/S files, all section bounds,
CRC32 footers, reference bounds and724-byte sensor roots. It compares the21
416-byte mode records and resolves each mode's56-byte register-setting rows,
including optional fields, data arrays, operation and delay references before
comparison. Both the mode records and all21 resolved setting sequences agree.
The two power sequences agree as well. This is still an inferred V5.6.1 layout;
it does not establish that all nested metadata or extension blocks are equal.

The four selector rows at root+572 each write the known S5KJN5 test-pattern
register0x0600. They agree between L/S, but are not initialization sequences.
The separate root+564 candidate sequence contains54 setting rows in L and49
in S and differs after reference resolution. Do not use the common mode tables
to infer a common complete initialization, bypass supplier selection, or copy
the public D-PHY initialization into this19.2MHz C-PHY phone. Proprietary
register values and module contents remain private; this comparison does not
program the phone or activate the camera graph.
