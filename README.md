# REDMI Watch 5 esim unofficial rom
## REDMI Watch 5 esim 非官方固件
### What do we do? 我们做了什么？

- Better fonts 更好的字体
- more customize applications(.rpk) slots 更多的自定义应用栏位

### Editions 固件版本

| Edition | 基线 Base | 字体 Fonts | 说明 Notes |
|---------|-----------|-----------|------------|
| `Theme1` / `Theme2` / `Theme3` | 3.110.029 | 自定义 MiSans | 早期版本 legacy |
| `Theme4` | 官方 **3.110.078** | 苹方 PingFang SC | 去预装游戏、含工具链 |

`Theme4` 说明：

- 以官方 3.110.078 为基线（`ap / system / app / misc / watchface` 等保持官方原样），
  因此 **AVB 分区校验可通过**；
- 字体替换为苹方（PingFang SC Regular/Medium/Semibold，已 CFF→TrueType 转换并子集化）；
- `quickapp` 删除 7 个预装游戏（2048、找色块、24点、记忆卡牌、拳力挑战、小人过桥、打地鼠）。

### Tools 工具

见 [`tools/`](tools/)：romfs 解包/重打包、体积报告、苹方字体生成、ROM 构建脚本。

### How to use it? 如何使用？

1.Download the rom edition that you want in [Release](https://github.com/s12mcOvO/REDMI-Watch5-esim-Unofficial-ROM/releases) page.
  
  在[Release](https://github.com/s12mcOvO/REDMI-Watch5-esim-Unofficial-ROM/releases)页面下载你喜欢的固件版本

2.**DO NOT UNPACK THE ZIP** and install the [AstroBox](https://astrobox.online/en/) or other unofficial Mi Watch controller.

  **不要解压压缩包** 并且下载[Astrobox](https://astrobox.online/)或其他非官方小米/红米手表控制软件

3.Flash the zip to your devices(REDMI Watch 5 esim) in your favorite way.

  用你最喜欢的方式将固件刷入你的设备
