# OnePlus 13 完整 Ubuntu：r272 里程碑

2026-11-03 已完成原始完整系统中的 GPU、自动音频、普通桌面自动 OTG 与5GHz保留回归联合验收。源码、已审核构建输入、Actions工作流和脱敏验收记录都已上传GitHub，可以从本分支重新构建配套RAM测试镜像。

**这是需要电脑提供配套rootfs的临时启动系统。不是单个boot文件即可独立运行的安装包，也没有永久刷写或双系统安装步骤。** 镜像不预建普通用户，首次设置由使用者自行建号。原项目下方的Pad分区/安装说明不适用于本手机里程碑。

## 固定版本

| 项目 | 内容 |
| --- | --- |
| 里程碑分支 | `milestone/oneplus13-full-ubuntu-r272-20261103` |
| 快照标签 | `oneplus13-full-ubuntu-r272-20261103` |
| 已验收镜像源码 | `d3605af22a7377a244421babfb65f73afbc617ea` |
| 已验收源码树 | `db78ba9e36a221f89cb7062cbd2e03e646be57a1` |
| 验收记录提交 | `0150de1cf3b1e0ff53eba77e95df10124648bc5d` |
| 成功构建 | [Actions41462106749](https://github.com/zhou9547/onepluspad-2pro-mainline/actions/runs/41462106749)，kernel/Mesa/SSC/rootfs/image五项成功 |
| 机型范围 | 一加13 / dodge / SM8750；已测PJZ110 24GB及AA569显示配置，其他机型/内存或面板组合不作已验收承诺 |

本分支从上述验收记录版本建立，只增加里程碑和使用说明，不更改内核、用户态、驱动、固件或构建流程，不为文档改动重复编译。完整机器可读依据见[里程碑快照](docs/oneplus13/MILESTONE-R272-20261103.json)与[真机验收记录](docs/oneplus13/FULL-UBUNTU-R272-ACCEPTANCE-20261103.md)。

## 已通过的范围

- 完整Ubuntu26.04/GNOME50、1662个包，浏览器、Files、Software、Text Editor、Terminal、LibreOffice Writer/Calc等真实ARM64应用；交付零普通用户、root锁定、无默认密码和自动登录，本人实物屏幕键盘建号进入普通用户Wayland桌面。
- 实际GTK GL场景渲染、MSM GPU引擎工作和Adreno GLES像素回读；镜像自带首用户音频服务自动完成麦克风/双扬声器声学检查并删除原始录音。已有本人可听/流畅反馈与本轮机器检查分别保留。
- 同一拓展坞/U盘、无外接电源、仅手机供电：原方向两次接入，实际拔下后仅翻转手机端Type-C180°第三次接入。三次真实外设节点、GNOME自动NTFS3只读挂载、4096字节O_RDONLY块读/文件前缀及卸载通过，连续保持130.549/15.458/30.617秒；本轮无额外失败重插。
- 15.525秒冻结看门狗恢复、服务重启后重新读盘/卸载、source/实际角色/同一块节点连续5.138秒稳定检查通过。
- 同次5220MHz Wi-Fi前后关联/IP/HTTP/校验证书HTTPS通过，后检未重连；显示CRTC active、Mutter ON且DPU/GMU错误0。四项固件实际保存值、PC device/sink与UDC、双功放关断和Android七项基线均完成恢复。

这是限定设备、限定只读操作和有界保持时间的验收。r268/r269/r270的失败和额外重插记录没有被删除或回填成功；本轮成功不证明此前source丢失的根因或任意拓展坞/接头都已稳定。

## 从GitHub Actions构建

1. 打开仓库的 **Actions → OnePlus 13 current image from source → Run workflow**，分支选择 **`milestone/oneplus13-full-ubuntu-r272-20261103`**。
2. 普通GitHub托管ARM64构建：`use_server=false`、`all_on_server=false`、`runtime_qemu=false`。不需要本机私有文件、设备标识或Wi-Fi密码；[qualified-data来源和许可](devices/oneplus13/qualified-data/PROVENANCE.md)中的已审核数据已在仓库。需要有可用的GitHub ARM64 runner配额。
3. 只有已配置可信自托管ARM64 runner及`oneplus13-arm64`标签时才用`use_server=true`；最近成功构建使用此选项，rootfs/镜像组装及SSC仍由GitHub runner完成。`all_on_server`不是普通使用者的必选项。QEMU仅作可选诊断，不能替代真机验收。
4. 等kernel、Mesa、SSC、rootfs和image均成功，再下载 **`complete-ram-image-本次完整提交SHA`**。不要把失败任务的部分产物当完整镜像。
5. 在完整产物目录检查`SHA256SUMS`，并核对`automatic-usb-manifest.json`中的source、kernel、boot/rootfs哈希。选用 **`boot-automatic-usb-ram-experimental.img` + `rootfs.squashfs`**；其他实验boot不是此次验收配置。

也可以用GitHub CLI发起构建（需要相应仓库Actions权限）：

```sh
gh workflow run oneplus13-current-image.yml \
  --repo zhou9547/onepluspad-2pro-mainline \
  --ref milestone/oneplus13-full-ubuntu-r272-20261103 \
  -f use_server=false -f all_on_server=false -f runtime_qemu=false
```

fork后将仓库参数换成自己的仓库，并启用Actions。底层入口是[oneplus13-source-image.yml](.github/workflows/oneplus13-source-image.yml)。构建会从该次工作流、同一提交取得全部组件，不依赖旧镜像拼装。

**新构建会拥有自己的source标记、会话nonce和镜像哈希，不能要求与下列历史验收二进制逐字节相同，也不能直接继承它的真机资格。** “可从固定源码构建”不等于每次重建产物已做真机测试。以本次产物清单验证配对；原Actions附件保存期为14天，过期后从分支/标签重建，不假定旧附件永久存在。

历史已验收配对仅供核对原Actions附件：

```text
8e21ce9e2ae46486a7c8d82354f470221e16643afa2e79c2c9770637685c15be  boot-automatic-usb-ram-experimental.img
28c13993f6b01cef36cf55aac151d4226473e20d07d5c356d140fce0b63138bb  rootfs.squashfs
```

## 镜像在哪里、是否包含隐私

boot和rootfs不只在本地：上面成功Actions的`complete-ram-image-d3605af22a7377a244421babfb65f73afbc617ea`附件包含两者。源码及已审核构建输入保存在Git仓库，体积较大的成品镜像通过Actions附件分发，不是作为Git普通文件提交；附件当前可用，默认14天后会过期，可从固定分支/标签重建。

针对已交付实际SquashFS再次回读确认：普通用户0、个人home文件0、未锁定密码哈希0、保存的NetworkManager连接0、SSH客户端/主机私钥0、machine-id为空、未启用自动登录。见[脱敏隐私复核](docs/oneplus13/R272-PRIVACY-READBACK-20261103.json)。本人的Wi-Fi密码、设备标识、访问密钥、原始日志及RAM中创建的测试帐号不随里程碑上传。本地`private`目录与原始测试记录也不是构建所需输入。

产物仍包含已审核并由本人授权发布的固件、板级校准/显示配置和boot几何参数，不能把它等同于纯通用Ubuntu或适合任意手机的镜像；原厂许可不因上传而改变。每次构建的会话nonce和镜像哈希用于绑定RAM测试，不是本人的手机序列号。上述回读是明确类别的核验，不作为任意二进制绝无未知元数据的保证。

## 临时启动需要哪些准备

以下是操作契约及命令形态，不是本仓库自动执行的刷机脚本。当前里程碑没有一个跨操作系统、自动识别全部USB网卡的一键启动器；电脑侧适配器、服务就绪时序和恢复计划需要事先准备。构建工作流本身不会连接手机。

1. 仅适用于已经具备临时boot条件的目标设备；不提供解锁操作。为本次设备建立新的精确源码/镜像/计划和未消费ledger，记录Android起始基线、操作窗口与恢复路径。旧验收脚本、授权和ledger都不能复用。
2. 在可信电脑上准备配套rootfs服务。镜像USB NCM网络手机端是`172.16.13.1/24`，电脑须正确绑定`172.16.13.2`；服务监听`172.16.13.2:8000`。不要把地址配到无关实体网卡，或在服务尚不可达时让手机开始拉取rootfs。若网卡在启动后才出现，应由主机计划事先处理地址/监听就绪时序；目前没有独立于电脑rootfs的启动模式。
3. 从本次`automatic-usb-manifest.json`读取`rootfs_sha256`。在仓库根目录，可先进行**不接触手机**的文件预检（路径及SHA替换为本次值）：

   ```sh
   python3 tools/oneplus13/serve-rootfs.py \
     --image /absolute/path/rootfs.squashfs \
     --sha256 ROOTFS_SHA256 --check-only
   ```

   网络及计划就绪后，同一命令去掉`--check-only`才启动分块服务。普通`python -m http.server`不实现该镜像的分块URL协议，不能替代它。
4. 保持电脑数据线，明确选择本次已登记设备后，仅使用命令形态：

   ```sh
   fastboot -s DEVICE_SERIAL boot /absolute/path/boot-automatic-usb-ram-experimental.img
   ```

   此文件不要求也不允许`flash`、`erase`、`set_active`、解锁、重分区或持久安装。`rootfs.squashfs`不能直接fastboot刷入某个分区。镜像从USB取完整rootfs、核对哈希后在RAM中运行；主机需留有约1.4GB传输与相应内存/启动时间余量。
5. 原始系统自带**300秒**自动返回期限。r272由精确绑定的RAM测试计划reload调整为3300秒，这是本轮测试条件，不是下载镜像默认就能长时间使用。若需更长窗口，先制定新计划，再在RAM内调整并回读；不能重复启动bootstrap或restart其Required timer。
6. 首次设置中自行创建用户和密码。重启后RAM更改消失。Wi-Fi凭据不在仓库或产物中；本次自行设置，不上传用户名/密码。开发诊断接口仅限可信电脑及隔离网络，不对公网暴露。

USB物理测试仍必须真正换线，先确认Type-C host/source再由原生服务先current64=1250、后VBUS24=1；恢复按24→64→18→17使用当轮实际保存值。不能用强制role、按钮确认或“等了一会儿”代替真实节点和只读读盘。准备好Wi-Fi控制通道后再拔电脑线接拓展坞。

## 尚未解决或未验收

- 手动锁屏/电源键唤醒/待机；目前`idle-delay=0`只避免自动熄屏，不是唤醒修复。
- 反向横屏左右声道映射；中文输入法完整体验。
- 写盘、外接供电/PD充电、拓展坞显示输出及其他接口、更广泛U盘/拓展坞和不同设备配置。
- 相机/GNSS暂停，NFC跳过；双系统与永久安装均未执行，也不在该里程碑的临时操作说明中。

进一步适配请从此分支另建开发分支，保持里程碑分支/标签不变。不要把r272称为所有手机功能均已适配的日用正式版。
