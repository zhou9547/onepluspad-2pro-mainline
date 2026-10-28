# Container networking and remaining Pad feature comparison

The previously tested image source54fdf46f has NF_CONNTRACK, bridge,
br_netfilter, veth, xt_addrtype and xt_conntrack. It lacks NF_NAT, NF_TABLES
and NETFILTER_XTABLES_LEGACY. In this pinned v7.2 kernel, IP_NF_IPTABLES is
a compatibility symbol: IP_NF_IPTABLES_LEGACY controls the actual ip_tables
evaluator. The former alone cannot provide a usable legacy firewall.

The phone fragment now explicitly enables both legacy IPv4/IPv6 tables and
Ubuntu's iptables-nft backend, NAT/masquerade, connection tracking, required
matches, bridge/veth, namespaces, cgroups, seccomp and overlayfs. The resolved
olddefconfig and delivered modules.tar.gz are checked together; absent
modules fail the build. NFT counters are built into nf_tables in this kernel,
so the obsolete NFT_COUNTER option is deliberately not used.

Docker, iptables, nftables and iproute2 are preinstalled. Docker/containerd
remain stopped at boot during phone qualification. The owner can explicitly
start docker.service. This avoids introducing a bridge and forwarding policy
before the joint regression. No firewall-disable or host-network workaround is
used. Overlay2, IPv6 traffic, Swarm and rootless Docker need separate tests.

The manually invoked ram-container-check.py runs a real private Docker daemon
with VFS storage in isolated PID/mount/network namespaces and RAM storage.
It imports the delivered native static BusyBox instead of pulling an image.
It checks legacy filter/NAT rules, Docker bridge HTTP between containers,
embedded DNS, off-bridge masqueraded HTTP and peer-to-published-port HTTP
with userland-proxy disabled. The peer has no route to the container subnet.
The outer phone network rules and USB/WiFi remain outside the namespace.
Namespace destruction and bounded service termination clean up on failure.
Hardware acceptance requires an actual combined phone test; source presence
and a successful build alone do not establish working Docker.

References: [Docker firewall behavior](https://docs.docker.com/engine/network/packet-filtering-firewalls/),
[Moby dependency checks](https://github.com/moby/moby/blob/master/contrib/check-config.sh),
and the actual pinned Linux Kconfig/Makefiles.

## Comparison with the original Pad project

Reviewed the original project's README and docs/SENSORS.md, display/power,
audio, and sensor packaging. The established order is platform/display/input,
radio/USB, audio/sensors, then power/time/app integration. Tablet calibration,
amplifier settings and storage installation must not be reused for the phone.

| Original feature | Phone evidence / remaining work |
|---|---|
| Display, GPU, ordinary GNOME | Retained; project Mesa production assertion fix, Chinese session and SSH passed |
| WiFi, Bluetooth, USB NCM | Both WiFi bands passed; BT power/OBEX present, peer receipt still needed |
| USB host/storage/DP | Driver support present; exact phone peripherals and DP need owner-connected hardware |
| Microphone | Pad WCD939x routes exist as reference; phone topology and capture not qualified |
| Speakers | Two AW88461 IDs and silent SD1 PCM passed; add bounded nonzero PCM before audible/manual profile qualification |
| SSC accelerometer/gyro/compass | Three-second vector samples passed; continuous proxy, physical axes and self-contained registry delivery remain |
| Ambient light | Standard default/all-UID lookup empty; investigate owner HAL's wise_rgb data ABI |
| Video decode | Pad Iris integration exists; phone board/firmware and decoded-frame comparison remain |
| Backlight/power key/suspend | Phone panel differs; keep suspend blocked until phone-specific recovery tests |
| Battery/thermal/RTC | Battery readings retained; phone power/thermal/time behavior still requires measurement |
| Containers | New explicit dependency closure and isolated real-engine test; not part of earlier qualified image |

The Pad itself does not qualify camera, fingerprint, Waydroid, full Snap
confinement, stock fast charging or dynamic speaker protection. These must not
be described as simple missing imports. Persistent dual boot is outside the
owner's RAM-only, no-flash authorization.
