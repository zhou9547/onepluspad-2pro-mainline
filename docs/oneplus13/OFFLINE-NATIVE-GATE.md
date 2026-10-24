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
完成后，桌面流程将固定该新附件，再运行一轮组合验证。

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
   这不是阻止 root 直接 insmod 的安全边界，也不声称已验证当前 ARM64 rootfs。
4. `package-desktop.py --native-xml` 现在在读取输入前拒绝打包；诊断 helper
   也拒绝在桌面 RAM session 中启动。原生桌面暂时关闭，不能把旧镜像当作
   符合手动启动要求的新候选。
5. QEMU 观察器新增实际 kmod 检查：先确认模块存在，再验证普通显式加载及
   两条 OF 别名没有加载显示模块；成功标记成为交接验收的必要条件。
   新流程尚未运行，旧 QEMU 结果不能继承为这一检查的通过证据。

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
| 新 ARM64 内核/模块构建 | 待执行 | 旧构建不覆盖本轮 SPR 源码 |
| 新 rootfs + kmod + QEMU 完整交接/恢复 | 第一轮通过 | 原固定内核；新内核组合待运行 |
| DSI 批处理、PLL取整、继承显示接管与物理输出 | 未闭环 | 不得从主机测试推断 |

主机 C 本轮使用 Zig 0.14.1 提供的 Clang Windows 工具链，启用
`-Wall -Wextra -Werror`；没有 ASan/UBSan，JSON如实记录 false。
GitHub Actions 中的新检查保留 GCC + ASan/UBSan 和完整 ARM64 构建要求。

## 继承显示的另一项待核查问题

归档真机日志中 simpledrm 在约0.079秒注册，约0.198秒发生未使用时钟和电源域
清理。当前 simple-framebuffer 节点没有 clocks、power-domains 或供电引用。
固定内核的
[simpledrm 源码](https://github.com/yzddmr6/linux-sm8750-erhai/blob/7a81d184e3098624d4342d8f4eff5e23674bcc9f/drivers/gpu/drm/sysfb/simpledrm.c)
依据节点中的这些资源保持固件显示链路。缺少引用是一个资源生命周期缺口，
但日志没有证明具体哪条显示资源被关闭，不能据此断言它就是黑屏根因。
暂不添加全局 ignore_unused 参数，也不猜测面板供电以反复试机。

## 下一步及真机门槛

先运行新源码的完整离线内核构建和 ASan/UBSan，取得新 release/模块/DTB，
再重新固定下游工具的来源和哈希；不得覆盖旧 manifest 冒充新构建。
然后刷新 rootfs，在 QEMU 中实测新增 kmod 策略、交接及恢复，审查原生手动
启动路径的跨 switch_root 交接，闭环命令批处理和接管时序后再解除打包封锁。

不得把旧 native 镜像用于新实验，也不得直接从 GNOME 黑屏跳到修改面板参数
后反复试机。下一次真机测试必须先有具体、已复核的候选和未决风险清单。
