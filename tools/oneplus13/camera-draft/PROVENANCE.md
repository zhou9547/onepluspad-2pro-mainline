# Camera component source staging

These are public mailing-list changes by their original authors, preserved
with their original signoffs and source URLs/hashes in sources.json. Codex
prepared the selection, source-bound builder and isolated workflow; this is
not an upstream merged camera implementation or a claim of phone testing.

The first native W=1/-Werror build found an unused local left by the external
PHY conversion. A separate Codex correction removes that single declaration;
the original23 patches retain their hashes. The compiler gate stays enabled.

The sequence is X1E PHY v13 (two patches), CAMSS external PHY v12 (six),
Kaanapali v15 (eight), then SM8750 v6 (seven). All23 apply with fuzz=0 on
fresh affected source files from the actual phone kernel pin. Native object
compilation remains a separate gate. The source discussions contain unresolved
review/dependency comments; preserving the series is not an assertion that
those concerns disappeared. Driver SPDX notices remain authoritative; binding
files retain their original dual-license notices.

SM8750 support here covers RDI transport, CSID980, VFE980, TPG and standalone
CSI PHY support. It does not add the phone's populated sensor driver, board
power/clock/lane graph, ISP processing, autofocus/OIS or a libcamera pipeline.
Generic S5KJN5 capture reported by the patch author does not identify a sensor
in the owner's phone. The saved phone FDT additionally selects a custom
ultrawide PHY sequence; do not replace that with a generic sequence silently.

The builder also compiles the existing isolated AW88461 draft and runs its
synthetic parser/power failure checks against the same kernel configuration.
This supplies neither missing factory calibration nor dynamic protection.
No phone DTS, service, firmware, data, module installer or boot image is
generated, and no running candidate is overwritten.
