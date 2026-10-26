# Phone WLAN transport and exact firmware delivery

The current isolated phone candidate still has its radio nodes and modules
disabled. Historical run66 networking used reference inputs. It is not a
current phone-specific WiFi acceptance.

A subsequent bounded Android **GET-only** query reports QCA SAR capability5,
documented as TAS (standalone WLAN time averaging), legacy selector NONE with
zero rows, and unresolved CTL grouping. Vendor translation can also map unknown
legacy firmware selections to NONE. Neither that empty reply nor absence of the
optional wifisar.cfg proves disabled/unlimited RF power. The raw replies remain
private; no SET, scan, file write or reboot was requested, and seven Android
baseline properties matched. This is the reason to audit TAS lifecycle/firmware
policy before attaching the legacy V2 API to phone RF admission.

The first dormant transport's native ARM64 checks and actual kernel object
compilation passed Actions40316488478. The subsequent decoder change accepts
OFF/empty GET as an observation, preserves SET-to-NONE refusal, and has15 codec
plus29 actual-driver groups passing host release and ASan/UBSan/LSan. Native
verification for that follow-up remains separate.

Follow-up native Actions40318336080 passed15+29 groups in both release and
sanitized configurations and the four actual kernel objects. Because embedding
SAR state changes `wmi_base` layout, a further gate recompiles the complete
common/WiFi7 family and its two relocatable composite links. Four leaf objects
are not a safe replacement for that family rebuild, module modpost or runtime
qualification. No compiled object is installed on the phone.

Complete common/WiFi7 compilation and relocatable linking then passed native
Actions40319212570 with warnings as errors. The full phone build has an explicit
`wifi-transport-only` input to include this dormant integration, preserve all
new sources in the resulting phone-kernel.patch, and produce matching Image
and modules. This does not install a cfg80211 policy, firmware or automatic
SAR caller, and is not permission to activate the resulting WLAN DTB.

An exact-source audit also found a version-name discrepancy: the pinned WMI
capability extractor passes `active_version` directly, WMA/HDD retain it, and
the sequential host SAR_VERSION_5 maps to QCA5; the firmware enum names raw4
SMART_TX and raw5 TAS. The QCA API documents QCA5 as TAS. Do not use the vendor
API label alone to choose one firmware policy or assume this public source
exactly describes every proprietary component on the running Android image.
The raw WMI observation, effective firmware policy and TAS/SmartTx lifecycle
remain necessary. The audited57 WMI/header files contain the history command
definitions in the separate firmware API but no corresponding WMI C sender;
three WMA/HDD files were additionally checked for capability propagation.

The new dormant SAR integration binds kernel7a81d184e3098624d4342d8f4eff5e23674bcc9f.
It hooks actual WMI capability, nested EXT2 flags and response receive paths.
The internal API serializes bounded GET or V2 SET/result/GET observations.
Timeout, unexpected/duplicate reply or detach closes the instance across SSR;
there is no automatic policy replay. It has no production caller, cfg80211
callback, default limit or RF admission. Observed V2 indexes and GET half-dBm
values remain separate. Host tests execute this actual C code with synthetic
transport, and native kernel compilation is a separate gate.

The firmware name mapping is supported by two independent pinned loaders:

| Exact phone OTA input | Pinned ath12k name | Reason |
| --- | --- | --- |
| amss20.bin | amss.bin | Main firmware request name |
| phy_ucode20.elf | m3.bin | Vendor `cnss_pci_load_m3` selects PHY_UCODE_V2 for PEACH major2, copies its entire bytes into M3 memory and passes address/size; mainline requests m3.bin for the same transfer |
| aux_ucode20.elf | aux_ucode.bin | Auxiliary firmware V2 selection and mainline auxiliary loader |
| peach/bdwlan.elf | board.bin | Actual Android selection was observed; API1 requests board.bin, then QMI detects ELF magic and downloads as ELF |
| peach/regdb.bin | regdb.bin | Actual Android selection was observed; API1 plain regdb fallback |

The vendor loader is pinned to OnePlusOSS modules/device-tree commit
d50b305f7da9e14715a25120a4ac7b1a4b8b97c3. No input is patched, padded or repacked.
No board-2.bin/firmware-2.bin is included that could override these files.
The original project also installs separate amss/m3/aux firmware, but its
reference bytes and board aliases must not replace the phone's verified inputs.
The host-only staging tool verifies the existing nine-file extraction contract
and copies only these five files below an **inactive** directory. It neither
installs firmware nor changes any candidate or phone.

Remaining before usable phone WiFi: effective phone USER/V2 policy and its
dynamic inputs, appropriate kernel/cfg80211 policy enforcement and replay
admission, current-rootfs firmware/delivery verification, then one reviewed RAM
test covering scan, authentication, DHCP/default route, certificate-verified
interface-bound HTTPS and desktop/platform/recovery regression. Do not treat a
successful SAR parser or observation API as effective-power qualification.
