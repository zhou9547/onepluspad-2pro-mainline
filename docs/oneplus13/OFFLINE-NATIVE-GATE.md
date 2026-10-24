# 原生显示离线检查，2026-10-24

本轮按用户“先理论验证，再测试”的要求进行。没有连接手机执行命令，没有
ADB/Fastboot 查询、重启、RAM 启动或分区操作。以下修复属于源码和主机验证，
不是新内核已经在手机工作，也不是不会变砖的保证。

用户随后明确批准独立分支上传和 Actions 离线构建。源码提交
`d624154c9548304f92712ea7e1f716fd98fe1150` 已上传；
[第一轮 GNOME/QEMU](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40051767501)
成功，验证新增 kmod 策略、完整 HTTP 分块交接和恢复计时器。
这一轮使用原 c2e659 内核与新 rootfs，不能冒充新内核组合的结果。
[新 ARM64 构建](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40051765091)
已经通过，包含内核、模块、设备树和八项 C ASan/UBSan 检查。
桌面工具及工作流在提交 `2957513a3ae1437cdc99ec1e2a9b525ef22d2ec6`
固定新内核附件；[新内核 GNOME/QEMU 组合验证](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40054456226)
也已通过。两轮的源码与产物来源分别记录，不能相互替代。

## 当前判断

上次默认 RAM 桌面已进入 systemd/GDM/GNOME，但用户观察仍黑屏。默认 DTB
关闭 MDSS，只提供继承的 simple-framebuffer；这不能证明原生 AA569 链路已启动。
本轮发现的身份和自动加载问题是原生候选的确定性阻塞/控制缺口，尚不能当成
上次默认桌面黑屏的已证实根因。触控、WLAN 和 GPU 仍没有完成真机验收。

## 已修复

1. `start-native-display` 与内核 SPR 不能继续仅检查根 compatible 中的
   `oneplus,dodge`。ABL 实测将它改成 `qcom,sun*`。两处改为严格匹配
   编译时 native model + handset + dodge/SM8750，或已经观察到的完整
   `Qualcomm Technologies, Inc. Sun MTP,dodge` + handset + qcom,sun。
   泛化的 Sun、13R、Pad、错误 SoC、缺失身份均拒绝。内核仍要求 DPU
   compatible、显式 SPR opt-in、MDSS reset 和准确 catalog，没有放宽 MMIO 门槛。
2. 桌面 physical-platform 也补上 native 编译时 model 和明确的 SM8750 条件，
   继续保留 Gunyah、VMID3、无绑定驱动的边界。
3. 完整 rootfs 的 `modules.alias` 确实包含 AA569 面板和 SM8750 DPU 自动匹配。
   新 rootfs 安装 blacklist + install `/bin/false` 策略，阻止常规别名、显式和
   依赖加载。blacklist 单独不足以阻止显式加载，依据是
   [kmod 原始手册](https://github.com/kmod-project/kmod/blob/master/man/modprobe.d.5.scd)。
   这不是阻止 root 直接 insmod 的安全边界。该策略已在新 ARM64 rootfs 的
   QEMU 会话中实际验证，仍不代表物理显示启动通过。
4. `package-desktop.py --native-xml` 现在在读取输入前拒绝打包；诊断 helper
   也拒绝在桌面 RAM session 中启动。原生桌面暂时关闭，不能把旧镜像当作
   符合手动启动要求的新候选。
5. QEMU 观察器新增实际 kmod 检查：先确认模块存在，再验证普通显式加载及
   两条 OF 别名没有加载显示模块；成功标记成为交接验收的必要条件。
   新流程已在上述两轮 QEMU 通过；新内核组合单独验证，不继承旧结果。

## 原项目与厂商对照

原项目的 `erhai-physical-platform` 提供 model/chassis 和早期 Gunyah 导出处理
方法，`init-ncm` 提供 RAM overlay/switch_root 思路；手机继续使用自己的
身份、网络地址及恢复边界。重新取得固定内核提交
`7a81d184e3098624d4342d8f4eff5e23674bcc9f` 的真实稀疏 Git checkout，
应用原有七份手机补丁后执行 C 检查；没有在 Windows 编译 ARM64 内核。

[原项目板级 DTS](https://github.com/yzddmr6/linux-sm8750-erhai/blob/7a81d184e3098624d4342d8f4eff5e23674bcc9f/arch/arm64/boot/dts/qcom/sm8750-erhai.dts)
使用双 DSI 和 KTZ8868 背光，不能搬到手机单 DSI AA569 OLED。
重新下载并按 Git blob 核对一加源码固定提交
`d50b305f7da9e14715a25120a4ac7b1a4b8b97c3` 的生产面板、DSI 解析器、
Oplus 电源控制及 SPR packing 源码。生产面板重新提取的 150 个开屏包、
1736 字节与归档原机 FDT 完全相符；未读取当前手机。

实际 C 回调与厂商定义核对了 VDDIO→VDDR→VCI 上电顺序、反向断电、
1/3/3/10 ms 等待及物理 reset 高10/低5/高30 ms。DSC 检查覆盖全部
128 字节 PPS，保留物理 bpp=128 Q4 和编码分组 bpp=256 的区别。
1363200000 bit/s/lane 和 6800 us 预算来自生产模式，没有套用平板参数。

## 通过和未通过必须分开

| 检查 | 本轮结果 | 范围 |
| --- | --- | --- |
| Python / 实际 shell 测试 | 48项通过 | 主机执行；包含13个 native 身份用例 |
| native 身份实际 C | 13个用例通过，OF引用收放平衡 | 真实 guard + OF fixture，无寄存器访问 |
| 面板 C | 150开屏包、3关屏包、149初始化故障点及8供电故障控制通过 | 替代 GPIO/供电/DSI I/O |
| DSC C | 128字节、错误 bpp/原始基线负例和 RGB 控制通过 | 固定内核真实函数 |
| DSI 时钟 C | 固定模式、6旧路径和10无效控制通过 | 请求和计算，不是实际 PLL 频率 |
| DPU C | 96组厂商/RGB数学、寄存器和 PPB 重放通过 | 替代 MMIO |
| 命令预算 C | 261组预算、新状态/OPP/ICC/溢出控制通过 | 不测真实传输完成时刻 |
| SPR profile/runtime C | 解码、所有管线UDC预检、地址、3轮PM、格式/flush/reset控制通过 | 替代 MMIO，非硬件PM循环 |
| 新 ARM64 内核/模块构建 | Actions40051765091通过 | 本轮 SPR 源码、8项 C ASan/UBSan；下载后复核36个清单文件 |
| 新 rootfs + kmod + QEMU 完整交接/恢复 | Actions40054456226通过 | 固定 d624154c 新内核；HTTP分块、实际kmod、systemd/GDM、180秒截止及重启 |
| DSI 批处理、PLL取整、继承显示接管与物理输出 | 未闭环 | 不得从主机测试推断 |

主机 C 本轮使用 Zig 0.14.1 提供的 Clang Windows 工具链，启用
`-Wall -Wextra -Werror`；没有 ASan/UBSan，JSON如实记录 false。
GitHub Actions 的八项 C 检查已使用 GCC + ASan/UBSan 通过，完整 ARM64
内核/模块构建通过。Windows 本地报告与 Actions 报告分开保留。

新内核 release 为 `7.2.0-oneplus13-g7a81d184e309-c963dc1c909ec-pcd4948652e86`。
下载复核覆盖 native 身份 guard 哈希、默认 initramfs 不含私有 SPR、九个显示
依赖模块的 AArch64/vermagic、native DTB 七个反例。组合 QEMU 验证的恢复期限
为180秒；手机候选的900秒绝对期限保持不变。QEMU virt 不模拟SM8750显示硬件。

## 命令调度差异仍需审查

生产开屏序列有150包，其中137包 flags 为0x40、13包为0，形成13个批组。
厂商 `dsi_panel_create_cmd_packets()` 根据 `MIPI_DSI_MSG_BATCH_COMMAND`
设置 `last_command`，再经 `dsi_host_transfer_sub()` 提交。当前 AA569 驱动逐条
调用 `mipi_dsi_dcs_write_buffer()`；固定内核 `dsi_host.c` 的发送路径每次
添加一条命令后触发 DMA，并等待该次完成。相同 payload、顺序和显式延时
不证明两者的总线间隔、批组边界和接管行为等价。
这项检查只确认调度差异，没有测量物理时序，也没有据此修改面板命令。

## 继承显示的另一项待核查问题

归档真机日志中 simpledrm 在约0.079秒注册，约0.198秒发生未使用时钟和电源域
清理。当前 simple-framebuffer 节点没有 clocks、power-domains 或供电引用。
固定内核的
[simpledrm 源码](https://github.com/yzddmr6/linux-sm8750-erhai/blob/7a81d184e3098624d4342d8f4eff5e23674bcc9f/drivers/gpu/drm/sysfb/simpledrm.c)
依据节点中的这些资源保持固件显示链路。缺少引用是一个资源生命周期缺口，
但日志没有证明具体哪条显示资源被关闭，不能据此断言它就是黑屏根因。
暂不添加全局 ignore_unused 参数，也不猜测面板供电以反复试机。

## 下一步及真机门槛

新源码 ARM64 构建、ASan/UBSan、下游来源固定、刷新 rootfs 和新内核 QEMU
组合检查已经通过。继续参考厂商和原项目，审查原生手动启动路径的跨
switch_root 交接，闭环命令批处理、PLL取整及显示资源接管后再解除打包封锁。
离线构建成功不关闭物理显示、触控、WLAN、GPU的验收项。

不得把旧 native 镜像用于新实验，也不得直接从 GNOME 黑屏跳到修改面板参数
后反复试机。下一次真机测试必须先有具体、已复核的候选和未决风险清单。
