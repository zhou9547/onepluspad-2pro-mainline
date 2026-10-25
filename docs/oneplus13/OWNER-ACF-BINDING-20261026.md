# Saved owner ACF content binding

Re-reading the existing owner firmware metadata corrects an older review flag:
the saved owner measurement for the1792-byte ODM aw882xx_acf.bin is
941f23e9e315820a01170a97dbb0c88382c46a548993e5d2ca98c7619b1b1847.
The already saved reference file has exactly that length and SHA256. The
earlier acf-inspection.json predated this comparison and still said
owner_version_matched=false; that field is not the latest evidence.

review-owner-acf.py independently binds exactly one saved owner measurement.
Four synthetic tests cover matching data, changed bytes, duplicate measurements
and an unexpected source path. The actual matched file passes the current C
AW88461 preflight under host ASan/UBSan through profile-file-test.c. No register
payload, private metadata or firmware bytes are uploaded by this work.

This closes the saved ACF content-match question only. A named chip in the ACF
does not prove either physical amplifier's PID; static profile matching does
not establish independent factory calibration, DSP limiter behavior or dynamic
speaker protection. The draft writes a profile during probe after chip-ID read
and cannot be used as a read-only identification probe. Audio remains compile
and offline parser testing only, with streams disabled and WSA reuse held.
