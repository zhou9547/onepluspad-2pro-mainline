# Camera trace continuation, 2026-10-31

5 GHz WiFi is already qualified historically at 5240 MHz in r191. Keep
both WiFi bands as regressions. Remaining adaptation goals are GNSS real
fix/start/stop, NFC physical tag, a real S5KJN5 frame and USB peripheral I/O.

## Reproduction and correction

A temporary-directory trace fixture reproduces KeyError('mode') from
stream_trace_stop(stream_trace_start()). This finally block runs before
stream-attempt records, further RDI attempts and the diagnostic TPG fallback.
The exception can therefore hide relevant capture failure diagnostics.
It does not prove that the historical live traceback had this same cause.

The kprobe state now includes mode. Each successfully defined probe is
explicitly enabled; global tracing_on alone did not enable those events.
Setup appends definitions and teardown disables/deletes only owned probes,
preserving unrelated kprobes. An existing reserved camera event rejects
setup instead of taking it over. Partial setup failures run the same
teardown; read failures still tear down, and cleanup errors remain visible
and fail overall camera cleanup. The function-tracer fallback is retained.

Primary reference reviewed: Linux Documentation/trace/kprobetrace.rst,
https://github.com/torvalds/linux/blob/master/Documentation/trace/kprobetrace.rst
The reference documents per-event enable and selective deletion. The original
Pad/reference trees contain no equivalent userspace camera trace helper.
No sensor power sequence, CCI driver, C-PHY timing, firmware or DTB changes.

## Offline verification and hardware boundary

Six regression cases cover mode/count/readback, event enable/disable/delete,
preexisting ownership, partial enable failure, teardown continuation after
an error, read error cleanup and the function-tracer fallback (the first
case checks several related lifecycle assertions). Thirteen camera tests
and the complete 584-test suite pass with one unrelated suite skip.

Real sensor init still failed with CCI -110 in r191. TPG pixels remain only
downstream diagnostics. This correction permits usable evidence collection;
it does not establish a real frame or any new hardware success.

Before hardware: independently verify the exact Actions image, finish the
combined runner/plan, remove or source-bind private debug module selection,
and budget NFC protocol/cleanup beyond its RF observation time. Run GNSS,
NFC, camera and USB in one approved RAM round with the preserved-feature
gate, current healthy WiFi CLI and explicit physical-assistance cards.
No old runner, consumed ledger or shutdown approval is reusable.
