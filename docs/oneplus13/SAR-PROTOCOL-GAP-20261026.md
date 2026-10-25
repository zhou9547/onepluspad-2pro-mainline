# Phone SAR protocol review and the Linux integration gap

This is a pinned-source/host-only review. It issues no radio command and does
not select a power limit or qualify RF activation.

Vendor tree d50b305f7da9e14715a25120a4ac7b1a4b8b97c3 contains
`qca-wifi-host-cmn/os_if/linux/qca_vendor.h` and
`wmi/inc/wmi_unified_sta_param.h`. Both document USER limits in steps of
0.5dBm. The QCA selector values distinguish BDF profiles0..4, NONE5, USER6
and V2 profile-index mode7. V2 indexes0..11 are not half-dBm values.
Omitted band/chain/modulation selectors apply to all supported values.

The saved stock wifisar script's fallback80 under USER6 is therefore a nominal
request field corresponding to40dBm. This is NOT evidence of actual transmit
power, a valid phone limit or a safe replacement policy. Firmware/BDF limits,
other controls, active policy and acknowledgements remain distinct. Do not
convert the fallback into a Linux default or assume request success implies
effective enforcement. The saved ODM lacks the optional wifisar.cfg, but that
does not exclude runtime overlays.

The vendor `wmi/src/wmi_unified_sta_tlv.c:send_sar_limit_cmd_tlv()` emits the SAR
fixed parameters, array of row TLVs and `WMI_SAR_LIMITS_CMDID`; rows carry band,
chain, modulation, limit value and validity bitmap. It also has a GET command
and a response decoder, needed to distinguish send status from active limits.
Vendor version/flag conversion and capability parsing are separate gates.

Kernel7a81d184e3098624d4342d8f4eff5e23674bcc9f registers
`ath12k/wifi7/hw.c:ath12k_ops_wifi7` (48 explicit callbacks), assigns that table
to the device and has no `set_sar_specs` callback. The pinned common WMI header
names SAR limit command/tags, but the inspected common `wmi.c` has no sender
using that phone command. It does have an ACPI BIOS SAR table path. That BIOS
table ABI is not evidence of the phone's QCA USER/V2 policy integration.
Do not claim that merely lowering ordinary txpower reproduces per-chain,
per-band/modulation or dynamic phone SAR policy.

`review-sar-request.py` interprets a saved structured request only. It rejects
mixed power/index namespaces, unknown selectors, unsigned overflow, invalid
profile indexes, unknown options and duplicate/overlapping row domains. It
never creates a command/wire payload, opens a socket or claims effective power.
Eight host tests bind the0.5dBm interpretation and refusal cases. No phone
firmware, calibration, private identifier or network credential is published.

Next engineering work: establish effective phone policy/capabilities and
firmware response semantics, then implement the appropriate kernel/userspace
power path with exact phone firmware/BDF/regdb selection and bounded failure
handling. First radio activation must wait for that joint review. Historical
network/BT behavior remains real evidence from reference inputs, not a phone
RF acceptance substitute.
