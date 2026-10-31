# OTG identity and diagnostic correction

The r211 combined RAM round completed in 93.22 seconds. Its firmware-gate
inventory returned both attributes unavailable. That older helper merged
missing files, read errors and timeouts, so the result does not establish
which condition happened. No role change or cable swap occurred in r211.

The existing desktop/physical-platform and aa569_spr_machine() already
document that ABL replaces the compiled root identity. The optional OTG patch
checked only of_machine_is_compatible("oneplus,dodge"), including its sysfs
visibility predicate. This hides both files under the known physical identity.

Reuse the existing strict SPR predicate:

- Compiled: exact native-display OnePlus 13 model, handset, both
  oneplus,dodge and qcom,sm8750.
- Physical: exact Qualcomm Technologies, Inc. Sun MTP,dodge model,
  handset and qcom,sun.
- Generic Sun, tablet, other phone, absent model/chassis and missing compatible
  are rejected. Device-tree node references are released on all paths.

All three OTG gates use this predicate: visibility, read callback and filtering
of late optional replies. Root-only 0400 attributes, GET protocol, common
serialization, response checks and timeout poison remain. No SET or automatic
firmware request is added. Actual-C sanitizer tests compile the function from
the patch; this is still offline evidence, not proof of firmware GET support.

The Python observation preserves values, unavailable and complete and
adds per-attribute status: missing, stat_error, not_regular, read_error,
timeout, invalid_value or ok. Device presence and bound-driver presence
are reported separately; unknown inspection is null. Exception strings and
firmware stderr are not exported. Reads keep the fixed path, fixed two names,
one attempt each and three-second child deadlines.

Next hardware observation must establish that the attributes are visible and
return valid values. Switch leasing, safe restore and physical USB I/O remain
open; this correction does not justify a firmware write.
