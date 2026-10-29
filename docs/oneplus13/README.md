# OnePlus 13 / 一加 13 原生 Linux

适用一加 13（dodge / SM8750）。当前可临时进入 Ubuntu GNOME；只使用 RAM 启动，不刷写、不修改分区、不持久安装。

截至 2026-10-29，最新已下载复核并完成联合回归的完整镜像来自提交 `5f37a1da`，
[Actions 40824286846](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40824286846) 的五个任务全部成功。
内核、Mesa、SSC 使用自托管 ARM64 编译机，rootfs 与完整镜像组装使用 GitHub ARM64 runner。
较新的源码提交可能包含下一轮候选；以 [STATUS.md](STATUS.md) 区分已验收与待验收版本。

## 已有真机证据

- AA569 原生显示、Adreno 830/Mesa 与 GNOME Wayland；用户已确认中文、触摸和任务栏可用，手动横竖屏不再重新登录。
- 精确手机固件下的 5 GHz（5240 MHz）和 2.4 GHz（2437 MHz）认证、DHCP、默认路由和局域网 HTTP。
- Docker IPv4 bridge、DNS、NAT、端口发布；内核和交付模块包含 legacy iptables 与 nftables 所需依赖。
- 中文环境、OpenSSH、普通用户会话和 Dock；保留蓝牙、电池等检查。
- 麦克风采集和上下两只扬声器独立信号相关性；桌面音量 20%、50%、100% 声学幅度递增，静音生效，本轮无削波。
- 普通启动下的传感器与当前左侧朝上姿态，Mutter 变换为 1；无需诊断预热。
- 超广角 S5KJN5 严格芯片 ID、runtime suspend、传感器与 CCI 卸载；尚未采集图像。

r62 在 490.2 秒内恢复 Android，七项基线一致，内核健康检查通过，分区写入为零。
扬声器绝对响度、长期保护、无人值守条件下无法进行的可见多姿态旋转验收仍未完成。
芯片 ID、设备节点、编译成功不等于完整硬件功能。

## 继续适配

硬件视频客户端已从源码构建并通过原生 ARM64 自检，但 Iris 真实解码尚未激活。
r62 使用该镜像和公开的临时看门狗探针，已验证保持一个 CPU 运行时的独立硬件恢复，主机未发起重启；闲置和休眠恢复仍未验收。下一轮视频测试使用独立、固定时限的清醒看门狗保护。
摄像头已通过原厂 probe_intent 与模块 ID 的合并关系，定位到 L/S 三路 C-PHY 配置；接下来补齐手机专用 PHY、传感器模式和采集通路。
GNSS、NFC、红外、完整 USB OTG/USB-C、电源管理和更多手机专用服务尚未完成。

进度与限制见 [STATUS.md](STATUS.md)、[TECHNICAL-DEBT.md](TECHNICAL-DEBT.md)、
[功能表](COMPLETE-FEATURE-MATRIX-20261026.md) 和 [硬件依据](HARDWARE.md)。

## 从源码构建

在 Actions 运行 **OnePlus 13 current image from source**。
`use_server=true` 将内核、Mesa、SSC 分配到已配置的自托管编译机，其余任务仍在 GitHub runner 运行；
不使用编译机时关闭该选项。QEMU 为可选诊断，默认关闭。下载 `complete-ram-image-<commit>` 并核对清单。
本机 Linux 构建入口为 `tools/oneplus13/source-image.sh`，按 kernel、rootfs、mesa、assemble、complete 阶段构建。

完整镜像包含精确来源的内核、模块、固件、Ubuntu GNOME 用户态和 SHA256 清单。
摄像头、视频是独立的手动 RAM 候选，默认桌面不自动加载这些实验驱动。
产物不是持久安装包；不要刷写任何分区。

## 来源和隐私

- 平台内核：yzddmr6/linux-sm8750-erhai，固定提交见 `devices/oneplus13/source.json`。
- 手机板级资料：sm8750-mainline/linux，index986，BSD-3-Clause。
- 一加公开源码：OnePlusOSS 的 SM8750 devicetree/modules。

保留原始版权、许可证与补丁来源。构建只使用经过审核和哈希绑定的 qualified-data 白名单；
网络凭据、个人数据、原始私有记录、私钥和未审查数据不进入仓库。
