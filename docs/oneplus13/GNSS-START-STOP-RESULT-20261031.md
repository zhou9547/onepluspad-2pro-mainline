# Rejected GNSS start with acknowledged stop

The r210 exact Actions image (4b99b29aa8660084e84e9558aa33f531dd022025,
run 41190113030) completed its temporary RAM test in 92.22 seconds. Android
returned with all seven baseline properties matching. One RAM boot and zero
partition writes were recorded. Camera chip-ID, 5 GHz control and MPSS checks
passed; camera frames were not tested.

The AFW identity corrected the former Register Events rejection. The next
request, LOC START, returned QMI GeneralError (46). Native stop_ready then
confirmed successful STOP before emitting LOCATION_SESSION_STOPPED nmea=0.
The native exit remains 1 because START did not succeed. Python incorrectly
required exit 0 for cleanup and caused the runner to recover before the USB
read-only observation stage. GNSS start/fix acceptance remains false.

The collector now accepts cleanup for this narrow case only: exit 1, no process
timeout, no STARTED or NO_SESSION marker, exactly one well-formed STOPPED marker,
and exactly the observed start-result GeneralError line on stderr. Timeouts,
crashes, duplicate or contradictory markers, other errors and failed STOP do not
qualify. Successful engine acceptance still requires START plus clean STOP and
a real satellite fix. No native firmware operation or time budget changes.

Twenty-two collector tests pass, including the observed failure and negative
controls. This is a control-flow correction requiring a new exact image/plan
and independent runner review before another combined RAM boot. NFC is skipped
at the owner's request; real camera frames, GNSS and USB physical I/O remain open.
