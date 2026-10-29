# Ultrawide mode selection review

r59 repeats strict S5KJN5 chip-ID0x38e5 at7-bit0x2d, runtime suspend and complete
sensor/CCI teardown. It does not stream or identify the stock HAL's selected
module file. Bounded read-only Android kernel history independently includes a
successful dodgeultrawide probe with0x38e5. Other failed/earlier probes include
0x805; their presence does not establish an ID conversion or a selected module.

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

All three slave-address fields contain8-bit0x5a. Their ID fields do not equal
the physical0x38e5. The retained sensor shared library has an S5KJN5 debug
marker and a GetSensorLibraryAPIs export; this alone does not explain which
module the HAL selects or whether it replaces any fields. Proprietary register
tables and executable contents are not published or installed by this review.

The pinned public vendor match path reads the chip ID, applies the configured
mask/shift and compares it with the supplied ID. Its OEM callback has an HP5
special case, not a demonstrated JN5 remapping. The separately reviewed
oplus_cam_sensor_match_id_pre/post callbacks do not establish such a mapping
either. Public source pin:
[OnePlusOSS d50b305f](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750/tree/d50b305f7da9e14715a25120a4ac7b1a4b8b97c3).
Relevant files are cam_sensor_core.c, drivers/oplus/cam_sensor_module/cam_link/
oplus_cam_sensor.c and the Oplus camera_extension cam_sensor_custom.c.

The staged public S5KJN5 v6 driver supports a four-lane D-PHY mode. The staged
generic SM8750 PHY and CAMSS path likewise do not yet supply a qualified C-PHY
configuration. The phone's custom vendor PHY register table is a separate
constraint. A D-PHY template cannot simply be selected because it is easier
to drive, and the L/S flags do not prove the physical module uses C-PHY.

Next establish the actual selected module/PHY mode from bounded stock evidence
or a source-backed field-selection path. Then implement a coherent sensor,
PHY and CAMSS graph for that mode, with exact resources and supported APIs.
Only a real frame with validated pixels followed by stop/runtime-suspend/
teardown and retained-feature regression can qualify camera capture. Keep the
default desktop camera-disabled and retain strict0x38e5 identification.
