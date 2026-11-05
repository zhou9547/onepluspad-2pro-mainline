# r284 已结束：r283 精简系统本轮功能验收通过（2026-11-05）

仅一次临时 fastboot boot，未执行持久安装或分区写入。手机已返回 Android，七项基线一致；主机服务、防火墙规则已退出。ledger 已消费，当前没有活动真机轮次或剩余启动次数，不运行旧 host.py。

精确镜像：Actions 42019690558；源 07b8435a8715ccdfb7beee7e0e87ba58eb1a3fba，树 e161a9930c1a0bdf51fdacf3fe48a761564912b8。boot ea7f5ea48c8e658da0720804e233fbd34a22d4620cba6a91b834f7766a1760d8；rootfs 0a32d4499d846965a576467ddc9644dac6cd902f5a8d993140057c6622fa80c0。交付 images/diagnostic-r283-20261105，保留 GNOME/Files/Terminal/设置/OSK/Resources/GNOME System Monitor，841 包，默认 180 秒空闲灭屏。交付镜像零普通用户及保存的个人凭据；本轮帐号只存在于 RAM。

原始镜像运行，无 OTG/渲染/音频功能覆盖。普通用户会话、真实 GLES 和 GTK GL/MSM、镜像自动首用户音频/原生麦克风/双扬声器机器检查通过。USB 拓展坞无外接电源，仅手机供电。A 朝向两次，再翻转 B 朝向两次，四次分别保持 130.408、15.789、30.576、30.662 秒；每次均实际枚举、GNOME 自动只读挂载、4096 字节 O_RDONLY 块读取、文件前缀读取、卸载通过，没有额外失败重插。看门狗恢复观察耗时 13.772 秒（冻结相位不同，并不表示更改了内核 15 秒门槛）；服务重启后的再读盘和卸载、实际 source/角色/同一节点连续 5.238 秒保持通过。

每次翻转前本人明确确认屏幕解锁，机器也读取 ScreenSaver=false，GVfs 运行正常；没有禁止空闲锁屏、手工挂载或强制 USB role。连续只读观察器将锁屏、GVfs/udisks、USB 日志写入回执；没有暂停主控制器或临时追加 boot。USB 四项固件按 24→64→18→17 恢复本轮实际保存值，PC device/sink＋UDC configured 通过。5GHz 5220MHz 前后既有链路、IP、HTTP、校验证书 HTTPS 通过，未重连；本轮后检 DNS rc=0。显示未锁定、CRTC active、Mutter ON、DPU/GMU 错误为 0，双功放关断，Android 七项基线一致。

**限定：功能验收通过不等于零协议错误。** 同期内核日志仍有 29 条去重后的 USB -71，部分在初始枚举、故障恢复或断开期间；本轮已自动恢复并完成读盘，原因未证明。r282 首次翻转没有 host/source、额外重插、补测自动挂载失败和观察器时序错误全部保留，不能用本轮覆盖。不能断言只是没插紧或根因已修复，也不能承诺所有接口、线缆、拓展坞均稳定。

r282 的人工双向横屏声道/音量/静音、4 次锁屏认证唤醒、180 秒自动灭屏唤醒、Resources 识别和数据变化保留其精确 r280＋RAM 用户偏好范围。本轮新二进制没有重新做这些人工试听和按键验收；不要把旧人工结果伪装成本轮新测试。实现源码保留，r283 独立回读中仅默认空闲策略等已说明差异。GDM 登录界面唤醒、原生 DPMS/深度 suspend、写盘、外部 PD 供电、视频输出仍未验收；相机/GNSS 暂停，NFC 跳过。

稳定完整系统 r272 入口和固定里程碑保持不变。当前继续按要求使用精简系统诊断，r283 不是新的双系统或永久安装器。任何后续启动仍需新 chat 绑定的精确计划、全新 ledger 和单次确认；当前聊天的重复独立审查豁免不转移给新聊天。

本轮证据：plan.json、ledger.json、final-plan-review.json、owner-actions.jsonl、final.private.json、acceptance.json、usb-protocol-observations.json、receipts/。原始 private 记录和设备标识不上传 GitHub；公开记录仅使用脱敏摘要。本地可复现代码和观察器全部保留。
