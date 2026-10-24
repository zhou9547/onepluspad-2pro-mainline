# AA569 实际 OPP 与双 mixer/pipe 预算

上一轮单独授权的唯一 RAM 验收在 DPU atomic performance check 返回 -7 后
提前结束，135.4 秒确认 Android 返回。没有刷写，当前没有新的真机授权。
本轮只在主机与 Actions 上继续修复，旧私有候选禁止重试。

## 复现与来源

旧成功夹具用 1 GHz，没有绑定实际编译 DTB 的 575 MHz MDP 最高 OPP。
当前全宽下限 1440×3200×120，再按 105% 和 125/102 分别向上取整，要求
711529412 Hz，因此会被拒绝。不能通过提高 OPP 或取消性能检查来解决。

固定平台源码仍为 `7a81d184e3098624d4342d8f4eff5e23674bcc9f`。
原项目在 DSC 模式使用两个 LM；AA569 的已有资源门槛更严格要求
2 LM + 2 DSPP + 2 DSC + 1 DSI，且禁止 cloned writeback。
原 `dpu_plane_split` 已有按处理能力拆分并交给正常资源分配的路径。

厂商 `d50b305f7da9e14715a25120a4ac7b1a4b8b97c3` 的
`sde_crtc_get_mixer_resolution` 按实际 mixer 数切分宽度；
`sde_core_perf` 接收用户态给出的时钟投票，没有在内核公开同一套 HAL
时钟算法。因此不宣称本实现精确复刻厂商 HAL，也不从厂商投票反推可超频。
三份完整厂商源文件已记录 Git blob 与 SHA256。

上游近期的 [mixer 模式验证讨论](https://mail-archive.com/dri-devel@lists.freedesktop.org/msg643339.html)
同样强调使用实际分配数量，不能因为硬件支持合并就假定永远使用两个 mixer。
本候选使用既有严格资源门槛，不复制整个通用 topology 补丁。

## 第十一补丁

只在 AA569 opt-in 路径修改：

- 基础像素处理下限按已经分配的两个 LM 计算；其他数量或不整除宽度拒绝。
  每个可见 plane 仍按实际 pipe 的原计算求最大时钟，aggregate bandwidth
  仍全量相加，绝不因为两个 LM 而把内存带宽减半。
- 分配 SSPP 前，先反解真实最高 OPP 能容纳的原始 pipe 时钟：先取
  `floor(max_opp×102/125)`，再取 `floor(result×100/clk_factor)`。
  两次 floor 对应之后的两次 ceil；不能把它们合并成单次比例运算。
  然后复用原 `dpu_plane_split`，让全宽 pipe 在分配前拆为两个 720 宽配置。
- 不修改设备树 OPP、通用 plane 算法、非 AA569 路径、TE 或硬件定时器。
  缺少 OPP/配置、错误 mixer 数量和溢出均拒绝。

## 已完成的离线检查

十项实际 C 检查通过，61 项本地工具测试通过（Windows 不支持 flock 的
一项跳过，ARM64 必须无跳过）。新增预算检查读取实际编译 native DTB，
解析 MDP 的 phandle/OPP 表，而非从夹具填入 1 GHz。

实际 C 执行 mixer/预算函数及原 `dpu_plane_split`：旧全宽预算在 575 MHz
下拒绝，新分配拆成两个 720 pipe，时钟 355764706 Hz、带宽
3557647059 B/s，均保留向上取整和效率余量。另有 3417 组反解边界、
六种 DTB 错误输入、缺失/错误数量/OPP 与非 opt-in 对照。

split 的 DRM 几何回调使用无旋转、无缩放、无需裁剪的明确夹具；没有
模拟完整 DRM resource allocator，也没有验证真实 SSPP 寄存器或画面。
固定底层几何算法不变，其他几何和实际硬件仍需后续检查与验收。

构建脚本把本检查移到 native DTB 编译之后；command budget 清单升级到
版本 3，下载验证将预算的 DTB 哈希绑定至实际附件。私有打包门槛要求
版本 3 和独立的 actual-DTB-OPP 复核证据，旧版本无法再次通过。

ARM64 ASan/UBSan 与完整构建尚待完成；新内核完成后还必须更新匹配
rootfs/模块并重跑 GNOME/QEMU。不能用旧 rootfs 宣称新组合通过，也不
因离线算式通过便自动进行下一次真机实验。
