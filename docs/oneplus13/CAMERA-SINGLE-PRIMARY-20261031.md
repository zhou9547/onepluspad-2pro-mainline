# Single primary camera diagnostic profile

The existing broad capture helper repeats the sensor stream and tries RDI1,
RDI2, a CAMSS bind retry and TPG. It remains the full-diagnostics default.
The new explicit single-primary profile provides a shorter, fixed path for
one combined RAM round; it does not establish real sensor frames.

It uses the existing phone path S5KJN5 -> CSIPHY1 -> CSID1 pad1 -> VFE1/RDI0
-> video0, 4096x3072 packed RAW10 pGAA. There is one 25-second stream attempt,
one discovery sweep across at most eight media nodes (60 seconds common,
six seconds each), eight-second configuration commands, no bind retry, no
RDI alternatives, no TPG and no sensor-test-pattern change. The exact 15-module
dependency closure from Actions modules.dep and the original policy SHA256
are required before policy mutation. Debug module replacement and preexisting
sensor/CAMSS/PHY ownership are rejected. Attempted module insertion is owned
before invoking modprobe; modules already present are not unloaded.

Fixed work/cleanup/output alarms are 660/330/30 seconds. The conservative
external helper allowance is 1035 seconds including five seconds for stream
unwind and ten seconds transport margin. These are exceptional ceilings,
not expected elapsed time or hard real-time guarantees. Kernel waits can
outlast userspace deadlines; independent host recovery is still required.
Cleanup topology reads share 48 seconds, six seconds each; unsuccessful
reads cannot prove graph absence. Cleanup expiry restores policy through the
existing finally, reports cleanup_pass=false and emits evidence under the
separate output alarm. Occupied trace probes refuse capture before streaming.

Success requires a successful, non-timeout primary stream, the exact negotiated
format, at least 15,728,640 bytes of plausible real sensor pixels, and every
trace/module/policy/media-graph cleanup check. TPG cannot qualify the sensor.
Offline lifecycle tests exercise the actual main try/finally, one failed and
one successful synthetic stream, owned traces, expiry receipts and policy
restoration. Synthetic pixels are test fixtures, never hardware acceptance.

The original Pad tree has no equivalent userspace camera capture helper. This
profile reuses the established phone CAMSS topology, existing cleanup, the
pinned modules.dep resolver and historical TPG/real-sensor evidence documented
in STATUS.md and CAMERA-TRACE-CONTINUATION-20261031.md. No kernel timing, sensor
register sequence, DT graph or default desktop enablement changes.

Before a physical run, bind the exact newly built Actions helper/modules and
fresh joint runner schedule, preserve the early display/deadline admission,
and combine camera with GNSS/USB rather than opening a camera-only boot. A
failed independent function may continue only after proven cleanup. Neither
this document nor offline tests renew an expired window or consumed ledger.
