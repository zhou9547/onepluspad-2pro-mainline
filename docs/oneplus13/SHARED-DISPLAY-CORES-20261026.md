# Shared display dependencies in the guarded RAM rootfs

run67 booted the guarded matching-module rootfs and started the exact phone ADSP
once from offline. Display preflight passed, but activation failed; Android
returned automatically in70.9s and all seven baseline samples matched. No
display/GPU/desktop acceptance is claimed for run67.

The complete media/audio/radio dependency-denial policy also covers two shared
display prerequisites: `cec` and `ubwc_config`. Exact modules.dep, module indexes
and host kmod dry runs reproduce both denials. There are no panel softdeps in
the pinned archive. Loading CEC alone leaves UBWC denied; the emulator caught
this before another phone boot. The repeated false line in the failed log was
one matching grep result followed by the complete load plan, not two unknown
modules. Earlier CEC-only QEMU runs40224673685/40225224431 failed and do not
qualify the candidate.

Pinned source7a81d184e3098624d4342d8f4eff5e23674bcc9f shows CEC's module init
registers its generic software core, not a hardware adapter. UBWC exports a
static SoC configuration database and has no module hardware initialization
function. Its SM8750 table is preserved; no parameters are synthesized.

The RAM helper checks exact module/release and original policy hashes, empty
module dependency fields, read-only physical blocks, overlay marker and active
recovery services before a single attempt. Both modules must initially be
unloaded. After both visibly register with no CEC adapter, exactly their two
install-deny lines become dependency no-ops in the RAM overlay. All other
peripheral denial bytes and the panel/MSM explicit activation policy remain.
An attempted or partially failed load is never retried or unloaded.

Bound CEC SHA256:69c2bafd5315b52d253d0f26c0f8a5351d7bf940f61ee5a242b637483ca42659.
Bound UBWC SHA256:96c8350913e8e271aed91a6586726d2061eaea6d23b03922c6050a969c685a1d.

Seven synthetic tests cover identity/dependency/policy/storage/service failures,
adapter creation, missing registration, no retry and second-load failure.
Actions40226313784 passed native ARM64 gates, actual ARM64 kmod/core registration
and unchanged SquashFS handoff/deadline. The artifact digest/ZIP CRC and exact
candidate rootfs identity were independently verified after download.

run68 then passed one explicit AA569 activation, Adreno GPU pixel readback,
ordinary-user Wayland/project Mesa/Settings software acceptance, CPU/input/
battery/thermal inventory and final kernel-health gates with the exact phone
ADSP and graphics firmware. No radios or audio/sensor streams were enabled.
Android returned automatically in93.6s with all seven baseline samples equal.
Visible display, physical touch, full rendering workloads and endurance remain
unaccepted. The software-only desktop result deliberately leaves combined WiFi
acceptance false; there was no WiFi operation in this isolated run.
