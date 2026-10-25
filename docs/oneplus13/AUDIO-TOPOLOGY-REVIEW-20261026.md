# Effective audio topology review

This increment corrects a handed-over experimental WSA route. It is not a
speaker implementation or evidence that every disabled template device is
physically absent. Stock runtime enablement and measured hardware identity
must be checked separately.

The saved owner runtime FDT, already pinned by SHA256
5a121983d6836aff2d8f8ebf3e6ef05db70d26548c2ab0a5037dc5f878714b6b,
contains8 WSA884x/WSA883x template nodes. None is effectively enabled, after
checking every ancestor. The WSA macro at6b00000 is disabled. Both AWINIC
smartpa nodes are effectively enabled. The handover run42 candidate instead
enabled2 WSA884x speakers and a WSA playback DAI link. No new phone query was
used for this finding; full stock FDT and factory data stay private.

`review-audio-topology.py` reports enabled counts rather than treating node
presence as wiring evidence. Its optional quarantine requires the exact
disabled-stock WSA/two enabled AWINIC pattern,2 candidate speakers on a single
SoundWire controller, and one playback link referencing both phandles. It
refuses another link referencing either speaker. It disables only that
controller and its two speaker nodes and removes the one playback subtree.
Every other property and memory reservation is compared before serialization
and again after read-back. The LPASS macro clock provider is retained.

The private candidate packaging preserves the tested kernel, initramfs,
rootfs, Mesa, boot-header addresses and command line byte-for-byte. Only the
quarantined DTB, its header length and boot-image digest change. It never
enables an AWINIC driver, copies gain/tuning, opens PCM or changes a partition.
The resulting candidate is eligible only for reviewed nonaudio RAM regression;
audio remains unsupported and the old WSA-enabled hash is blocked from reuse.

Six offline tests include disabled ancestors, disabled/unknown root status,
unchanged unrelated properties/reservations, refusal of an active stock WSA,
missing pairs and additional DAI references. An ARM64 Actions job independently
compiles synthetic DTS controls with dtc, runs the real reader/quarantine CLI,
decompiles the result and checks a protected display property. Fixtures are
clearly synthetic, contain no board calibration and are not deployable DTBs.

Next speaker work must use the actual AWINIC Secondary MI2S path, the pinned
vendor/community AW88461 implementation, exact silicon confirmation and
owner-matched speaker protection. The old WSA mixer-control review cannot
substitute for those gates. No WSA streaming retry is planned.
