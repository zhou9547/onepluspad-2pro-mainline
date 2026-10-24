# AA569 固定生产 PHY 时序候选

本轮继续离线移植，不操作手机。前轮发现通用 D-PHY v4 计算与 AA569
生产配置的六项差异，本轮完成厂商提交路径审查并实现严格限定的候选。
十项实际 C 检查的 ARM64 ASan/UBSan、完整内核/模块构建以及匹配的
GNOME/QEMU 交接已通过。独立 ARM64 工具套件 61 项通过，无跳过。

进一步复核发现原 DSI host power_on 忽略 PM 获取失败，时钟失败路径还可能
留下 PM/OPP 引用。第十补丁改用 resume_and_get，严格按取得的资源逐项回收。
实际上电函数新增 rail/PM/九个时钟操作/引脚选择失败注入。最终内核提交
`33db9f38935f5cbdebbd00612c9360d1a7c99e80` 的
[Actions40065006440](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40065006440)
包含第九、第十补丁，已通过并下载校验。

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

## 共同的时钟树与资源接管

`check-clock-tree.py` 编译固定源码中的 divider 和 pixel RCG 回调，使用明确的
回调图夹具，不模拟完整 CCF 或真实硬件。两种 PLL mux 路径都能保留
1.3632 GHz lane / 170.4 MHz byte，并精确生成 181.76 MHz pixel：直接 bitclk
经 PHY /5、RCG 2/3；半速 bitclk 经 PHY /1、RCG 4/15。底层 pixel divider
未设置 SET_RATE_PARENT，不能据此把物理 PLL 已锁定视为已验证。

同一检查执行原 command TE 配置函数，覆盖 interface/pingpong、缺少时钟和
不支持 pingpong 的拒绝路径。夹具以 19.2 MHz、120 Hz、3200 行得到 count=50、
start=3168、rdptr=3169、height=6400；这些是寄存器计算，尚未测量物理 TE。
[Actions40065992683](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40065992683)
通过 66 组 PLL 对照、CCF/TE ASan/UBSan 和 61 项 ARM64 工具测试；下载附件
中的十一份公开固定源文件及本地/ARM64 结果已复核。

固定平台 `msm_drm_kms_init` 在 kms_init/hw_init 之前调用
`aperture_remove_all_conflicting_devices`。原生路径沿用此资源接管流程；
没有添加 ignore_unused、猜测电源依赖或跨驱动保活。此源码顺序不能证明
真机 ABL framebuffer 已成功交接，也不能诊断历史默认 framebuffer 黑屏。

## 显式 RAM 桌面入口与验证界限

新增 `/usr/libexec/oneplus13-native-display --check/--activate`，没有自动服务。
入口核对候选/内核/根文件系统版本、私有交接清单和 SPR CRC、手机身份、
RAM overlay、块设备只读、诊断 USB、保护服务、实际 timer D-Bus 截止时间、
模块版本及全局加载阻断。剩余恢复时间必须超过 60 秒，截止不得超过启动后
900 秒。显式激活持有 flock，先保留一次尝试标记，再依序加载 panel/msm；
失败不自动卸载、重试或修改恢复期限。旧暂存助手仍是不可执行数据。

ARM64 测试覆盖真实 flock 和模拟加载失败后的禁止重试，不加载实际显示模块。
匹配 rootfs 的最终
[Actions40066356160](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/40066356160)
验证 QEMU 中真实 systemd/busctl/kmod 接口、实际安装助手哈希、公开根文件系统
缺少私有参数时拒绝入口、数据交接及 180 秒恢复。VM 没有手机 USB，故 USB
active 响应使用夹具；观察时钟固定为零以检查接口，生产剩余时间判定另有
单元测试。前轮 VM 因运行过慢、剩余不足 60 秒而正确拒绝，生产阈值未放宽。
QEMU 未执行真实模块激活，手机的 900 秒恢复本轮未测试。

默认 native 打包仍在读取输入前拒绝。新增显式 `--prepare-native-offline`，只在
提供匹配内核、rootfs、助手及已下载复核的离线证据后组装私有 RAM 候选；
不是试机或刷写授权。私有参数不发布，实际加载/PLL/TE/DSC/SPR/物理画面
仍待授权后的独立验收。触控、WLAN 的板号/BDF/SAR/认证和真实收发、GPU
认证与渲染也未验收；独立项通过后才组合。音频等次要外设继续推迟。

匹配的新 rootfs 已下载逐项复核：458252288 字节，SHA256
`18126c23eff6004a45a8ab4d5c8cb120890c2c7cfab9c7d34f8e3dfad9e577cf`。
私有 RAM 候选已在 Git 之外组装，八项文件校验和 boot 各段独立回读通过，
公开 QEMU 控制流程逐项一致。私有镜像未启动、未刷写，不随公开证据打包。

## 随后单独授权的一次现场验收

上述离线结果之后，机主授权一次独立原生显示 RAM 验收，并要求动态检测，
避免无谓等待 900 秒。实际只发送一次 RAM boot、一次显式激活；手机约
50 秒进入 systemd，真实预检通过，模块加载返回。DPU atomic check 随后
报告性能检查 `-7`，故主机结束观察并请求提前恢复。约 135.4 秒确认回到
原厂 Android；抽查系统指纹、槽位、解锁状态和 vbmeta 摘要前后一致。
未刷写、未改分区，临时主机防火墙规则已移除。900 秒后备期限未改动，
本轮没有等到该期限触发，也不能据此保证所有死锁均可恢复。

机主回复时手机已经回到 Android；没有独立确认实验 GNOME 画面。该候选
未通过显示验收，禁止将“模块返回成功”记成点亮，也不重复启动它。

离线复查发现旧预算夹具以 1 GHz 作为成功用例上限，未绑定实际设备树。
固定平台 MDP OPP 最高为 575 MHz，而当前全宽下限叠加 105% 和 125/102
预算后达到 711529412 Hz。此路径可独立复现拒绝，不足以排除其他后续
问题。下一轮必须把实际编译 DTB、真实 topology 和 plane split 纳入同一
检查，参考原项目及厂商双 mixer 资源分配后修复；不得抬高 OPP 绕过限制。
此前的“离线证据允许组装”只证明旧检查通过，并未覆盖此实际速率约束。
当前候选不再具备再次试机资格；进一步硬件测试需要新的候选与授权。
