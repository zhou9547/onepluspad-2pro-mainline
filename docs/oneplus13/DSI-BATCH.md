# AA569 整组 DSI 提交（离线）

2026-10-24。本轮没有手机操作。源码和主机故障注入已完成，ARM64 Actions
构建及后续匹配模块/rootfs/QEMU 组合验证尚待执行。不能据此宣称屏幕可用。

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

`check-dsi-batch.py` 编译实际 DRM 包生成/API、MSM 分组/普通打包、DMA 提交、
manager 门槛/触发、父时钟/速率/使能、复位及恢复函数；外设 I/O 使用受控桩。
独立厂商格式向量逐字节比对 13 组，检查边界、映射/PM/父时钟/速率/各时钟
使能失败、IOVA 错误、超时清理、下一调用和原逐包路径。普通打包/dispatch/
manager trigger 还与固定原代码进行相等比较。不是仅测试另写的算法。

`check-panel.py` 检查实际生命周期、全部 150+3 包、13 个边界、LP/HS、
12 组初始化失败、亮度/关屏失败、分配失败、截断组和原电源回收。
本地两项 C 检查及 53 项 Python/实际 shell 检查通过。Actions 必须再执行
ASan/UBSan、完整 ARM64 编译和实际产物复核；新 release 不能搭配旧模块。

PLL 取整、真实 burst 时长、TE/MDP 互斥、控制器错误中断、SPR/资源接管、
物理亮屏及反复电源周期仍未验收。QEMU 无 AA569 硬件，不验证这些内容。
跨根原生显式激活仍未实现，native 桌面打包继续禁用。
