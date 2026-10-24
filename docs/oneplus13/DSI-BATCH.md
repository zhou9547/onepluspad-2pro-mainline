# AA569 整组 DSI 提交（离线）

2026-10-24。本轮没有手机操作。九项实际 C 的 ASan/UBSan、完整 ARM64
内核/模块构建及诊断 QEMU 在 Actions40058811743 通过；新模块的 GNOME
刷新和完整切根/恢复在 Actions40059533734 通过。全部附件已下载复核，
分组字节/资源调度的离线检查通过，仍不能据此宣称物理屏幕可用。

内核代码提交 `092f346445e4a8ac130de7cd310fd4d55d6c6167`，桌面组合
提交 `d431263f1d4cb7f08cd1efee84283091d1c53854`。新 release 为
`7.2.0-oneplus13-g7a81d184e309-c963dc1c909ec-p9d4dfb6d82d6`。

## 参考与适用范围

- 平台及原 Pad 内核：yzddmr6/linux-sm8750-erhai，固定提交
  `7a81d184e3098624d4342d8f4eff5e23674bcc9f`。
- 厂商：OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750，
  固定提交 `d50b305f7da9e14715a25120a4ac7b1a4b8b97c3`，
  `vendor/qcom/opensource/display-drivers/msm/dsi/` 下的
  `dsi_panel.c`、`dsi_display.c`、`dsi_ctrl.c`、`dsi_ctrl_hw_cmn.c`。
- 公开 AA569 生产命令仍使用既有 JSON；150 包原始字节和 SHA256 未改。

厂商解析把 0x40 转为“组未结束”，FETCH_MEMORY 路径累积带 MSM 头的命令，
只在终包提交 DMA；相应时钟/资源也持有到组尾。FIFO、非嵌入和双链路广播
存在不同规则，本实现不套用 Pad 双 DSI 行为。普通主线逐包路径始终置 LAST。
名义单链路生产开屏为 13 组，DMA 共 1216 字节，最大组 312 字节。
唯一 120ms 等待在终包后。字节和边界等价不等于电气或时序已经验证。

## 实现

第八补丁增加可选 `mipi_dsi_transfer_batch`，一次传入完整消息组，全部完成
返回 0；缺少 host 实现返回 EOPNOTSUPP，绝不逐包降级。消息显式携带 channel
和 LP/HS，不修改共享 mode_flags。没有跨调用的 pending 标志或待发长度。

MSM 分组入口仅接受已绑定 AA569 的 SM8750 DSI0、非 bonded/sync、D-PHY
命令模式；上限 64 包、单包 100 字节，整组必须放入现有 TX 缓冲区。
发送前验证全部消息，拒绝读、ACK、混合 LP/HS、异型 DCS、无效长度或溢出。
映射一次，按原 MSM 字节顺序及 0xff 对齐打包，仅尾包置 BIT7。
同一 cmd_mutex 内获取 PM/时钟、提交一次、等待完成、恢复 IRQ/控制/HS/时钟/PM。
获取失败释放已取得资源；超时或异常短 DMA 在释放前复位控制器。
v2.9 父时钟错误现在返回给调用者，避免继续使用未确认的父时钟。

AA569 生成头保留 type、batch 和 delay。实际面板回调预检组是否完整，
动态分配最大组消息数组，按组提交和等待；仍按 prepare/enable 分隔最后
独立 display-on，保持亮度与关屏 HS，原供电/reset 次序未改。
一次 DMA 出错可能已经让面板收到部分或全部命令，调用内不会自动重试。

## 验证与剩余门槛

另按实际 `component_add()` 顺序核对同步绑定：AA569 门槛在调用它之前设置，
绑定失败清除；MIPI 包装与原逐包接口一样允许 host->attach() 内的同步发送，
由 host 检查 readiness。实际 attach 函数也纳入故障检查，覆盖同步提交及失败回收。
首轮 Actions 在测试桩的 GCC 缩进警告处停止；第二轮通过 C 检查后发现面板
缺少 MIPI 常量头文件；修正后第三轮完成内核构建。失败日志一并保留。

`check-dsi-batch.py` 编译实际 DRM 包生成/API、MSM 分组/普通打包、DMA 提交、
manager 门槛/触发、父时钟/速率/使能、复位及恢复函数；外设 I/O 使用受控桩。
独立厂商格式向量逐字节比对 13 组，检查边界、映射/PM/父时钟/速率/各时钟
使能失败、IOVA 错误、超时清理、下一调用和原逐包路径。普通打包/dispatch/
manager trigger 还与固定原代码进行相等比较。不是仅测试另写的算法。

注入范围为映射/PM、两个父时钟、OPP/两个速率及四个时钟使能、IOVA 和
DMA 完成超时。清理使用原有恢复/时钟关闭接口；其中 void 接口无法反馈
硬件清理失败，主机桩不证明真实控制器在超时后的恢复能力。

`check-panel.py` 检查实际生命周期、全部 150+3 包、13 个边界、LP/HS、
12 组初始化失败、亮度/关屏失败、分配失败、截断组和原电源回收。
本地九项 C 检查及 53 项 Python/实际 shell 检查通过。ARM64 Actions 的
九项 C ASan/UBSan、内核/模块/DTB 编译、完整 GNOME/QEMU 组合均通过。
下载的 37 个内核清单文件、模块 AArch64/符号/vermagic、原生 DTB 七个
反例、全部 13 组 DMA 哈希及本地/Actions C 证据一致。

新 rootfs 为 445489152 字节，SHA256 为
`40f08d2d9efa736c00f11f2e92914879bec7a601ffa8f3d46b915452fb3be0f8`；
由前轮已验证的 GNOME 基础镜像刷新匹配模块，未复用旧内核的模块声明。
附件 ZIP 的 GitHub SHA256/CRC、内部清单、实际 initramfs 脚本和 QEMU
标记顺序均已复核。QEMU 执行 180 秒期限并重启，手机配置仍为 900 秒，
没有执行手机期限测试。原生数据交接通过，但没有激活或加载显示模块。

PLL 取整、真实 burst 时长、TE/MDP 互斥、控制器错误中断、SPR/资源接管、
物理亮屏及反复电源周期仍未验收。QEMU 无 AA569 硬件，不验证这些内容。
跨根原生显式激活仍未实现，native 桌面打包继续禁用。
