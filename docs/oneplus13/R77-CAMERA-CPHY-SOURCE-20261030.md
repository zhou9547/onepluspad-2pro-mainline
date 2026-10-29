# r77 S5KJN5 C-PHY capture candidate

## Stock route evidence

Read-only Android boot and camera logs were captured while the stock ultrawide
camera streamed. They identify the installed module at CCI0 address `0x2d`,
physical chip ID `0x38e5`, and the following active hardware path:

| Item | Stock value |
| --- | --- |
| Camera | `dodgeultrawide` |
| Sensor | Samsung S5KJN5 |
| CCI | controller 0, bus 0, 7-bit address `0x2d` |
| Receiver | CSIPHY1, CSID1, IFE1 |
| PHY mode | C-PHY |
| Trios | 3 |
| Lane assignment / enable | `0x210` / `0x2a` |
| Mode | 4096x3072, 30fps |
| Logged data-rate class | `6085485713` |
| Settle count | 45 |

The public phone C-PHY rate table has a 2.8Gsps entry. The capture candidate
uses a 1.4GHz link-frequency property because the Linux driver converts that
value to the 2.8Gsps symbol rate. The C-PHY timing is 38ns prepare and 300ns
preamble, yielding settle count45 under the reviewed vendor formula.

## Source changes

The main kernel build now applies the hash-locked public SM8750 CAMSS/PHY patch
series, adds the public OnePlus ultrawide C-PHY register table adapter, and adds
the reviewed S5KJN5 driver with a three-trio callback contract. The sensor
driver advertises only three data lanes and reports the C-PHY link frequency and
timing through `get_mbus_config`.

A separate DTB derivation creates:

- six CSIPHY provider nodes, with the real camera connected to CSIPHY1;
- the SM8750 CAMSS node with all 13 register ranges, ten interrupts, PHY,
  clock, SMMU, interconnect and power-domain resources;
- a sensor endpoint -> CSIPHY1 -> CSID1 -> IFE1 media graph;
- the phone's existing 0.88V and 1.2V PHY rails and 1.0V sensor core rail.

The graph exists only in `boot-camera-capture-ram-experimental.img`. The default
desktop DTB and USB recovery path are unchanged.

`boot-camera-gnss-ram-experimental.img` combines the capture tree with the
manual MPSS node and C.93 firmware archive. This permits one RAM session to
capture a sensor frame, start MPSS, run QMI LOC/NMEA acquisition and stop MPSS
without adding a second reboot for each target.

## Verification boundary

The clean fixed-pin component build compiles CAMSS, CSID/VFE, S5KJN5, CCI and
the phone C-PHY PHY with `W=1` and `Werror`. The WSL offline suite passes510
tests with one environment skip. The generated graph round-trips through the
FDT parser and the capture helper rejects short or uniform frames.

These checks do not prove that the sensor produces pixels. The public driver's
supplier-specific initialization sequence remains a hardware risk. Camera
capture is qualified only if the RAM helper reports a frame of at least
4096x3072 RAW10 samples with varied pixel values, the stream stops, all camera
modules unload, the media graph disappears, and the existing desktop/network
regressions remain intact in the same boot.
