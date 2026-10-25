# Platform module delivery and fixed USB role

Run63 found no cpufreq policies. Run64 read the actual driver links and bounded
logs: 16430000.mailbox was unbound and SCMI base-channel setup was deferred.
The actual kernel config has QCOM_CPUCP_MBOX=m and QCOM_SOCINFO=m. Both modules
already existed in the delivered matching archive but had no explicit late
load after the early coldplug phase. SCMI CPUFreq/perf and mailbox transport
were built in. The fixed source's CPUFreq driver accepts perf power domains,
so CPU nodes without clocks do not justify a speculative DT change.

Pinned kernel: yzddmr6/linux-sm8750-erhai at
7a81d184e3098624d4342d8f4eff5e23674bcc9f. The original source files were fetched
again and matched the saved source text. qcom-cpucp-mbox.c supports the
x1e80100 fallback used by the existing SM8750 DTS. No addresses, frequency
tables, voltages or CPU domain mapping were changed. The original module
dependency plans have no extra modules. Their SHA256 values are:

- CPUCP: 4dab6a2c2fc28bef13c88eaf70243b4f5593b0ab8fbb460b348688a11b165c7d
- socinfo: 9cd5af54d74926d3cd737b667c97ddf906d7b2af754d647af3ede1ab7a8ffb85

The RAM prerequisite script requires exact release/hash bindings, the active
guard/deadline, read-only hardware blocks and valid CPU/cpuss/aoss temperatures.
It loads only these existing modules, with bounded userspace waits. It does
not restart firmware, change USB role, set CPU clocks/voltages/governors or
apply a stress workload. After loading it requires two SCMI policies and the
socinfo sysfs identity file. Identity values/serials are not copied to reports.

Run65 refused the prerequisite before either module loaded: ADSP-backed battery
temperature legitimately returned ENODATA before ADSP startup. Android returned
in73.4s, seven baseline samples matched. The actual thermal shell function now
has five saved-filesystem tests: pending battery may pass only with valid CPU
temperatures; missing CPU data, absent CPU sensors, malformed data or >=70C
refuse activation. Readable non-CPU temperatures also retain conservative bounds.

Run66 passed prerequisites and the ordinary-user desktop/GPU/new-network/BT
component/battery regression. Two schedutil SCMI policies appeared:
384000..3532800kHz and1017600..4089600kHz, with cpufreq-cpu0 and cpufreq-cpu6
cooling devices. Android returned automatically in148.6s, seven baseline samples
matched; no flash, recorded partition writes or manual recovery. This establishes
policy and cooling-device registration, not frequency-transition accuracy,
thermal throttling under load, power efficiency or sustained stability.

UCSI is a separate open issue. Run64 has a bound UCSI auxiliary device, an empty
Type-C class and PPM init stopping after deferred retries. The candidate fixes
DWC3 dr_mode to peripheral while retaining a usb-role-switch graph. The pinned
UCSI path requires a role-switch provider, whereas DWC3 role registration is in
its DRD path. This is a source-supported explanation requiring later targeted
validation, not evidence of a missing compiled UCSI driver. Do not turn on dual
role or restart/reshuffle ADSP merely to obtain a Type-C entry during unattended
tests: the current USB device transport is also the recovery control path.

SCMI sysfs bus name in the pinned source is scmi_protocol. The initial inventory
looked under scmi and therefore its empty binding list was not negative evidence;
the tool/test fixture now use the actual bus name. Run66 policy/cooling files
independently establish the registered CPUFreq driver.
