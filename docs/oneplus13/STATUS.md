# 一加 13 适配状态

截至 2026-10-23，离线编译首版及实际下载产物复验通过；已按用户授权通过 root ADB 只读取证。**完整硬件适配尚未完成，未在手机启动任何实验镜像，也未修改手机。** 平板项目的功能表和安装脚本不适用于手机。

| 组件 | 状态 | 证据与边界 |
| --- | --- | --- |
| SM8750 平台内核和完整模块 | 离线通过 | Actions 39821954442；7.2.0-oneplus13-g7a81d184e309-cd25741ea7aea |
| 手机设备树 | 离线通过 | 编译、独立反编译、compatible 检查；尚未验证实际 ABL/stock DTBO |
| 实验性 RAM 镜像 | 离线通过 | Android v2 分段、initramfs 二进制身份、校验值和匹配模块检查 |
| ARM64 RAM 用户态 | 离线通过 | 实际 Image/initramfs 在 QEMU virt 到达 init 标记并正常关机；不模拟 SM8750 |
| Ubuntu 26.04.1 GNOME | 离线通过 | 构建 39809729390；下载复验 39812509439；GNOME Shell 50.1，782 个软件包 |
| USB NCM / ACM | 有源码线索 | 驱动及 RAM 配置已编译；真实枚举、网络和恢复期限待验证 |
| 显示 | 有源码线索 | 本机 AA569 量产面板已确认，原厂子树合并对照通过；DSC 1.2 native 422 / AP SPR，基线缺少 SPR 接管支持 |
| 触控 | 有源码线索 | 本机 S3910 HBP 布线与原厂驱动确认；隔离的 LBP 候选和主机解析检查已实现，Actions 编译待验 |
| GPU | 有源码线索 | SoC 驱动存在；手机固件及实际渲染未建立验证闭环 |
| Wi-Fi / Bluetooth | 有源码线索 | 手机布线、固件和校准需要独立确认 |
| 电量 / 充电 | 有源码线索 | 诊断设备树不启动 ADSP；没有充电可用结论 |
| 音频 / 传感器 / 蜂窝 / 相机 | 有源码线索 | 厂商源代码可供研究；尚未完成手机适配 |
| 持久安装 / 双系统 | 待调研 | 不提供手机分区、擦除或自动安装工具 |

内核实际下载复验为 [39823094330](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/39823094330)，重新验证了校验值、镜像结构、模块版本及 QEMU 启动。QEMU 日志没有 kernel panic，到达 ONEPLUS13_QEMU_INIT_OK 后显示 reboot: Power down。

唯一下一步：完成本机原厂输入的离线 ABL 校准和触控候选编译检查，继续查明并移植原生显示 SPR 链路。当前只读授权禁止任何 RAM 启动或刷写。

已确认：PJZ110、24 GiB、SM8750、Android 16 / PJZ110_16.0.10.501(CN01)、当前 A 槽、已解锁；boot/init_boot/vendor_boot/dtbo/vbmeta 与 FDT 两端 SHA-256 一致。原始备份只保留在私有主机目录，不上传。显示 SPR、真实调试通道、内核启动与物理触控仍未验证，不能开始分区安装或声称硬件可用。见 STOCK-CALIBRATION.md 和 NATIVE-INPUT.md。

设备状态：原厂 Android 持续运行；本项目只进行了明确目标的 root ADB 读取，没有重启、写文件、改设置或刷写。设备读取操作者：主 agent；独立审核 agent 未访问设备。离线候选正在开发。
