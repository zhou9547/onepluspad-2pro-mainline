# OnePlus 13 / 一加 13：离线适配候选

适用目标为一加 13（dodge / SM8750），不适用于 13R、13T、13s 或平板。
这是针对后续真机测试的开发候选，**没有真机启动或外设可用的结论**。
仓库原有 Pad 2 Pro 的功能表、固件包、分区脚本和刷机步骤均不适用于手机。

## 下载与复现

在本仓库 Actions 中运行 **OnePlus 13 offline build**，下载成功运行中的
`oneplus13-offline-<commit>` artifact。也可在 Ubuntu 24.04 主机上安装工作流
列出的依赖后运行 `bash tools/oneplus13/build.sh`。

产物包含 Image / Image.gz、手机 DTB、匹配的模块、内核配置、只读 RAM
initramfs、实验性 Android v2 RAM 镜像、输入版本、SHA256 和独立检查结果。
`verification.json` 和 `qemu.log` 只证明离线格式、构建和 ARM64 用户态路径。
QEMU virt 不模拟 SM8750 手机硬件。

## 真机测试前

当前默认设备树只提供源自社区参考的保守低内存区，避免把未知容量当成
16/24 GB；bootloader 是否覆盖内存描述仍需验证。板级供电来自被固定版本的
一加 13 社区设备树，尚未与这台手机的运行时 FDT 对照。

`boot-oneplus13-ram-experimental.img` 是打包格式候选。**不要刷入任何分区**。
它没有被证明能通过该手机 ABL 的 DTB 选择、stock DTBO 和 hypervisor 叠加。
先取得匹配原厂 boot/init_boot/vendor_boot/dtbo/vbmeta、运行时 FDT、型号、
容量、系统版本和解锁状态，校验恢复文件后再设计唯一一次 RAM 测试。
本项目没有对设备执行任何命令，也没有提供自动分区或擦除工具。

RAM 环境设计为 300 秒后重启；kernel panic 为 15 秒。实际硬件死锁可能令
软件计时器失效，自动恢复也需要真机验证。启动后逐个将块设备设置为只读，
不挂载 Android；USB NCM 地址为 172.16.13.1，HTTP 日志端口 8080，
开发 root shell 为 telnet 23 / USB ACM。只在可信 USB 连接下运行此调试镜像。

## 功能范围

当前工作：SM8750 平台复用、独立手机设备树与配置、匹配模块、RAM 调试
用户态、自动构建和产物检查。显示只使用社区固件 framebuffer 线索。
屏幕原生接管、S3910 触控、GPU 固件、无线、音频、电量/充电、休眠、
传感器、蜂窝、相机与双系统均待独立移植/真机验证；不能由编译成功推断。

源码、已知差距和下一步见同目录 STATUS.md、TECHNICAL-DEBT.md 和 WORKLOG.md；
产物中的独立 README 是本说明的副本。

## 来源

- 平台内核：yzddmr6/linux-sm8750-erhai，固定提交见 source.json。
- 手机板级资料：sm8750-mainline/linux 的 OnePlus-13-WIP，index986，BSD-3-Clause。
- 一加官方：OnePlusOSS 的 SM8750 devicetree/modules 源码。

保留原始版权和许可证。没有分发这台手机的校准数据、唯一地址或私钥。
