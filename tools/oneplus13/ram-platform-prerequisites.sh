#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-only
# RAM diagnostics only. Caller binds these two existing modules to the image.
platform_thermal_gate() {
    local sys=$1 zone value kind critical=0
    for zone in "$sys"/class/thermal/thermal_zone*; do
        kind=$(cat "$zone/type") || return 1
        case "$kind" in
            cpu-*|cpuss-*|aoss*)
                value=$(cat "$zone/temp") || return 1
                critical=$((critical+1));;
            *)
                # ADSP battery telemetry may legitimately be pending at this stage.
                value=$(cat "$zone/temp" 2>/dev/null) || continue;;
        esac
        test "$value" -ge -50000 && test "$value" -lt 70000 || return 1
    done
    test "$critical" -gt 0
}

platform_main() {
set -eu
: "${PLATFORM_KERNEL_RELEASE:?}"
: "${CPUCP_MODULE_SHA256:?}"
: "${SOCINFO_MODULE_SHA256:?}"
test "$(uname -r)" = "$PLATFORM_KERNEL_RELEASE"
systemctl is-active --quiet oneplus13-ram-guard.service
systemctl is-active --quiet oneplus13-ram-deadline.timer
for device in /sys/class/block/*; do
    case "${device##*/}" in ram*|zram*|loop*) continue;; esac
    test "$(cat "$device/ro")" = 1
done
platform_thermal_gate /sys
base=/lib/modules/$PLATFORM_KERNEL_RELEASE/kernel/drivers
test "$(sha256sum "$base/mailbox/qcom-cpucp-mbox.ko" | cut -d' ' -f1)" = "$CPUCP_MODULE_SHA256"
test "$(sha256sum "$base/soc/qcom/socinfo.ko" | cut -d' ' -f1)" = "$SOCINFO_MODULE_SHA256"
# No firmware restart, bind/unbind, USB role changes, clock or voltage values.
timeout -k 1 8 modprobe socinfo
timeout -k 1 8 modprobe qcom_cpucp_mbox
for attempt in $(seq 1 8); do
    test -e /sys/devices/system/cpu/cpufreq/policy0/scaling_driver && break
    sleep 1
done
test -e /sys/bus/platform/devices/16430000.mailbox/driver
count=0
for policy in /sys/devices/system/cpu/cpufreq/policy*; do
    test -d "$policy"
    test "$(cat "$policy/scaling_driver")" = scmi
    minimum=$(cat "$policy/scaling_min_freq")
    maximum=$(cat "$policy/scaling_max_freq")
    test "$minimum" -gt 0 && test "$maximum" -ge "$minimum"
    count=$((count+1))
done
test "$count" = 2
test -r /sys/devices/soc0/soc_id
echo PLATFORM_PREREQUISITES_READY
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then platform_main; fi
