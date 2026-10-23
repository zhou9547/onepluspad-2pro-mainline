# 一加 13 适配状态

截至 2026-10-23，离线编译首版及实际下载产物复验通过；已按用户授权通过 root ADB 只读取证。**完整硬件适配尚未完成，未在手机启动任何实验镜像，也未修改手机。** 平板项目的功能表和安装脚本不适用于手机。

| 组件 | 状态 | 证据与边界 |
| --- | --- | --- |
| SM8750 平台内核和完整模块 | 离线通过 | 最新 Actions 39892351557，源码 d337d2f4bea9；7.2.0-oneplus13-g7a81d184e309-c8c417595c712 |
| 手机设备树 / ABL 离线校准 | 离线通过 | 原厂底树2/覆盖层5对照；全部六个 DTBO 条目隔离合并通过；实际 ABL 启动未验证 |
| 本机 v4 启动三件套 | 离线通过 | 主机生成、AOSP 工具与独立解析回读；按本机96/8/96 MiB容量检查，无 AVB 签名、未刷写 |
| 实验性 RAM 镜像 | 离线通过 | Android v2 分段、initramfs 二进制身份、校验值和匹配模块检查 |
| ARM64 RAM 用户态 | 离线通过 | 实际 Image/initramfs 在 QEMU virt 到达 init 标记并正常关机；不模拟 SM8750 |
| Ubuntu 26.04.1 GNOME | 离线通过 | 构建 39809729390；下载复验 39812509439；GNOME Shell 50.1，782 个软件包 |
| USB NCM / ACM | 有源码线索 | 驱动及 RAM 配置已编译；真实枚举、网络和恢复期限待验证 |
| SPR / DSC 参数转换 | 离线通过 | 私有 SPR 四模式与主机 ARM64 仿真一致，7组/33字与公开厂商C一致；完整 PPS 已解码回读；17项本地主机检查通过 |
| 显示接管 | 有源码线索 | AA569 DSC1.2 native422 / AP SPR 已确认；DSI预计算参数、DSPP资源预留、SPR/UDC生命周期与面板驱动尚待接入 |
| S3910 LBP 候选模块 / DTB | 离线通过 | 14 项主机检查、C解析器 ASan/UBSan、实际ARM64模块/版本核验；GPIO/SPI电气配置对照；物理触控未验证 |
| GPU | 有源码线索 | SoC 驱动存在；手机固件及实际渲染未建立验证闭环 |
| Wi-Fi / Bluetooth | 有源码线索 | 手机布线、固件和校准需要独立确认 |
| 电量 / 充电 | 有源码线索 | 诊断设备树不启动 ADSP；没有充电可用结论 |
| 音频 / 传感器 / 蜂窝 / 相机 | 有源码线索 | 厂商源代码可供研究；尚未完成手机适配 |
| 持久安装 / 双系统 | 待调研 | 不提供手机分区、擦除或自动安装工具 |

内核实际下载复验为 [39823094330](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/39823094330)，重新验证了校验值、镜像结构、模块版本及 QEMU 启动。QEMU 日志没有 kernel panic，到达 ONEPLUS13_QEMU_INIT_OK 后显示 reboot: Power down。

最新构建为 [39892351557](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/39892351557)，全部编译、14项主机检查、C解析器 ASan/UBSan 和 QEMU 通过。完整附件在主机下载后再次检查 ZIP CRC、20个清单文件、ARM64触控模块、vermagic和实际DTB电气参数。QEMU只验证ARM64用户态，不验证手机。

下一步开发：把已核对的 native422 DSC 参数接入 DSI，并实现 SPR 的 DSPP资源预留/REGDMA生命周期，再接面板。下一步真机门槛仍是由用户后续安排一次有现场恢复条件的限时 RAM 引导，先验证真实 USB 调试、内存与恢复期限；当前只读授权禁止执行它。不能把当前候选用于日常安装。

已确认：PJZ110、24 GiB、SM8750、Android 16 / PJZ110_16.0.10.501(CN01)、当前 A 槽、已解锁；boot/init_boot/vendor_boot/dtbo/vbmeta 与 FDT 两端 SHA-256 一致。原始备份只保留在私有主机目录，不上传。显示 SPR、真实调试通道、内核启动与物理触控仍未验证，不能开始分区安装或声称硬件可用。见 STOCK-CALIBRATION.md 和 NATIVE-INPUT.md。

设备状态：Android持续运行；本项目只进行了明确目标的 root ADB 读取，没有重启、写文件、改设置或刷写。设备读取操作者：主 agent；独立审核 agent 未访问设备。构建与本轮离线校准已结束，无设备任务在运行。后续硬件操作不在本次授权内。
