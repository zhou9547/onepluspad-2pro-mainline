# SM8750 PLL 与 AA569 PHY 时序离线审查

2026-10-24。本轮仅增加公开源码审查、C 检查及独立 Actions，不改运行内核、
DTB、面板时序或镜像，不操作手机。不能作为硬件试启动放行。

参考原 Pad 平台固定内核 `7a81d184e3098624d4342d8f4eff5e23674bcc9f`
的 dsi_phy_7nm.c/dsi_phy.c，以及 OnePlusOSS 固定提交
`d50b305f7da9e14715a25120a4ac7b1a4b8b97c3` 的 dsi_pll_3nm.c、
dsi_phy_timing_v4_0.c、AA569 生产 DTS、dsi_panel.c、dsi_display.c。
所有下载文件均验证 Git blob SHA1 和 SHA256；不使用 EVB/其他面板参数。

## 已确认

SM8750 实际使用 V7.2 quirk，VCO 范围 600 MHz 至 5 GHz，19.2 MHz
参考时钟的两倍作为分频基数，18 位小数。原平台与厂商的分频结果及
V7.2 inverter 分段一致。标称 1.3632 GHz、其二倍和三倍均可精确表示，
对应分数分频的量化误差为 0 Hz。这只证明存在可表示的合法 VCO，
不证明 CCF 实际选择的整棵时钟树、实测晶振误差、PLL 锁定和最终 lane 频率。

检查编译原有 dec/frac、recalc、determine_rate、D-PHY v4 函数和厂商
dec/frac 函数，比较独立整数预期、阈值两侧、clamp、标称附近扰动和零速率。
Windows 主机明确使用 ARM64 的 64 位 unsigned-long 语义；Actions 在 ARM64
执行 ASan/UBSan。MMIO 读取使用受控桩，不会访问真实寄存器。

AA569 生产 DTS 的最终 wqhd_sdc_120 补充节点明确指定 14 字节时序。
厂商 parser 逐字节复制到 phy_timing_val，display 将其交给
dsi_phy_set_timing_params；主线 PHY enable 则调用通用 v4 计算。
两边字段到寄存器/数组位置映射已检查，以下按 CTRL 编号列出差异。

| CTRL | 字段 | 通用主线 | AA569 生产值 |
| --- | --- | --- | --- |
| 3 | clk_trail | 13 | 12 |
| 4 | hs_exit | 41 | 29 |
| 5 | hs_zero | 38 | 26 |
| 8 | hs_rqst | 8 | 11 |
| 12 | clk_pre | 40 | 36 |
| 13 | clk_post | 27 | 17 |

主线生成：`00 2c 0c 0d 29 26 0c 0c 08 02 04 00 28 1b`。
厂商生产：`00 2c 0c 0c 1d 1a 0c 0c 0b 02 04 00 24 11`。
相同字段不能消除其余差异；差异本身也不能证明主线值无效或解释历史黑屏。

## 尚未关闭

下一步追踪厂商 set_timing_params 到 V7.2 寄存器的完整提交路径、模式覆盖
和 PHY 时钟/半速接口约定，再判断是否需要严格限于 AA569 的覆盖机制。
不能直接把 DTS 字节复制进通用主线 PHY 驱动。ESC 使用 19.2 MHz 测试输入；
其真实运行速率、pixel/byte 的 CCF 共同分频选择仍需独立源码验证。
实际 burst/TE/MDP 调度、SPR 与资源接管、原生显式激活和物理显示仍未验收。
原生桌面打包保持禁用。前轮已验证的内核/模块/rootfs 组合保持原版本。
