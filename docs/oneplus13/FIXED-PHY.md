# AA569 固定生产 PHY 时序候选

本轮继续离线移植，不操作手机。前轮发现通用 D-PHY v4 计算与 AA569
生产配置的六项差异，本轮完成厂商提交路径审查并实现严格限定的候选。
本地十项实际 C 检查和 53 项工具检查通过，ARM64 构建与组合验证待完成。

## 厂商与平台依据

OnePlusOSS `d50b305f7da9e14715a25120a4ac7b1a4b8b97c3`：生产
AA569 DTS 的 wqhd_sdc_120 提供十四个字节；dsi_panel_parse_phy_timing
逐字节复制；dsi_phy_set_timing_params 调用 V7.2 timing_val，要求长度 14，
复制 lane_v4 后设置 is_phy_timing_present；PHY enable 因此跳过通用计算。
V7.2 enable/commit_phy_timing 将每个值写入对应的 CMN_TIMING_CTRL_0..13。
没有位移或单位换算。动态刷新路径存在覆盖行为；本候选不提供动态刷新。

原 Pad 平台固定内核 `7a81d184e3098624d4342d8f4eff5e23674bcc9f`
的 V7.2 D-PHY writer 使用相同十四个寄存器位置。第九补丁只在既有
AA569/SM8750 host 绑定且 DSI0、四 lane、native422、非 video/C-PHY/bonded、
HS 上限 1363200000 时标记请求。失败先清空请求，避免遗留栈值。

PHY 侧还要求配置指针为 SM8750、PHY0、standalone D-PHY、bitclk 精确
1363200000 且 ESC 非零；不匹配在 MMIO 之前拒绝。正常路径保留原计算。
固定路径使用公开生产值：`00 2c 0c 0c 1d 1a 0c 0c 0b 02 04 00 24 11`。
shared clk_pre/post 同步设置为 0x24/0x11，维持 V4/V7.2 半速 byte interface，
供 msm_dsi_phy_enable 返回后复制给 host；不是只更改 PHY 而遗漏 host。

## 验证范围

check-fixed-phy.py 编译实际选择器、原 D-PHY 时序计算及原寄存器写入语句，
检查十四值一致、七种错误请求不写寄存器/不改输出、三十三个普通速率
结果不变，并确认选择器位于 enable 的首次 MMIO 前。clock 检查还执行
实际 host 请求函数，七种不匹配路径清零并拒绝固定配置。

公开证据保留厂商完整源文件及 Git blob/SHA256。禁止把固定表当作
可任意速率复用的通用 PHY 标定；本功能仅为隔离 native DTB 的实验候选。
不会改变 default/touch DTB 或原 Pad 面板行为。物理输出未验证。

## 持续工作

继续验证共同 pixel/byte 时钟树、TE/MDP 调度和显示资源接管，再实现显式
原生桌面激活。原生桌面打包尚未开放，不能由编译通过推断可安全试机。
触控、无线和 GPU 仍需完成组合及最终硬件验收；音频等次要外设继续推迟。
