# Tier 1 — romfs 资源裁剪候选清单

> 用 `python3 tools/vela_romfs.py` / `size_report.py` 静态分析 `Theme1/` 得出。
> 目标：释放 flash、降低内存压力（对动画流畅度是**间接**收益，须设备实测）。
> 原则：**只删确认不被引用的资源**；一次一个分区；随时可回滚。

## 全局体积概览

| 分区 | 数据量 | 可裁剪空间（估算） |
|------|--------|--------------------|
| `vela_watchface.bin` | 77.5 MB | ~~59 MB（视频表盘）~~ **已排除，不动** |
| `vela_system.bin` | 68.5 MB | ~17 MB（OTA 动画）/ 35 MB（setupwizard，慎动） |
| `vela_app.bin` | 91.4 MB | ~28 MB（breath / walkie_talkie 等） |
| `vela_font.bin` | 26.4 MB | ~13 MB（MiSansF 三款，待验证） |
| `vela_misc.bin` | 16.8 MB | ~10 MB（media 音乐） |
| `vela_vendor.bin` | 18.7 MB | ~4.5 MB（gnss_demo / 音频样本） |

---

## ~~候选 A — 视频表盘~~（已排除）

> **用户明确要求：不删视频表盘。** 以下仅作记录，不执行。

| 目录 | 体积 |
|------|------|
| `120917346868/resource.bin` | 16.3 MB |
| `120917346867/resource.bin` | 15.8 MB |
| `120917346866/resource.bin` | 15.2 MB |
| `120917346865/resource.bin` | 14.8 MB |

`build.prop` 中 `persist.watchface.video_flag=0`（视频表盘默认关闭）。**保留不删。**

## 候选 B — OTA 进度动画（`vela_system.bin/ota/`，收益 17.4 MB，风险中低）

- `ota/anim0.bin … anim95.bin`，每个 187,660 B，共 96 个。
- 用途：系统升级进度动画。仅在 OTA 升级时显示。
- 风险：不影响正常开机与日常使用；升级界面可能异常。
- 建议：保守可保留；激进可删。

## 候选 C — 字体 MiSansF（`vela_font.bin`，13.2 MB，风险中）

- `font_config.json`（来自 `vela_ap.bin` 内嵌 rootfs）只引用 **MiSans-Regular / Medium / Demibold**，
  **未引用 MiSansF-\***。
- 但 `vela_ap.bin` 字符串里出现 `MiSansF-Regular/Medium/Demibold`，可能用于繁体/兜底，**需设备验证**。
- 风险：删错 → 部分文字不显示（通常是方框），可回滚。

## 候选 D — 应用资源（`vela_app.bin`）

| 资源 | 体积 | 备注 |
|------|------|------|
| `breath.res` | 20.6 MB | 呼吸训练，占比最大 |
| `walkie_talkie.res` | 5.0 MB | 对讲机 |
| `car_control.res` | 1.7 MB | 车控（需手机端配合） |
| `alipay.res` | 1.5 MB | 支付宝 |
| `easter_egg.res` | 0.66 MB | 彩蛋 |
| `demo.res`/`debug.res`/`sale.res`/`check_tool.res` | 0.07 MB | 测试/演示类，优先删 |

- 依据：这些名字在 `vela_ap.bin` 中基本搜不到（`breath.res` 搜到 1 处），多为独立应用资源。
- 删除后在桌面/应用列表会消失。**不会导致系统启动失败**，但若被 launcher 强引用可能异常。
- 建议：先删 `demo/debug/sale/check_tool/easter_egg`，再评估 `breath/walkie_talkie`。

## 候选 E — 其它

| 位置 | 体积 | 备注 |
|------|------|------|
| `misc/media/`（yogo/box/abdominal/buzz 等） | 10.7 MB | 冥想/音乐，删后对应功能无声 |
| `misc/run_course/` 语音 | 3.4 MB | 跑步课程语音提示 |
| `vendor/gps/gnss_demo.bin` | 1.3 MB | GPS 演示程序，大概率无用 |
| `vendor/audio/*.wav`（factory/runinspeaker） | ~1.3 MB | 工厂/测试音频 |
| `system/setupwizard/` | 35.8 MB | 首次开机配对向导动画，**不建议删**（会影响首次配对） |

---

## 操作与验证流程

```bash
# 1) 解包目标分区
python3 tools/vela_romfs.py extract Theme1/vela_app.bin work/app

# 2) 删除候选（目录/文件）
rm -f work/app/demo.res work/app/debug.res work/app/sale.res work/app/check_tool.res

# 3) 重打包（保持体积不超过原分区！）
python3 tools/vela_romfs.py pack work/app new/vela_app.bin \
    --volume image --max-size 95885312

# 4) 结构校验
python3 tools/vela_romfs.py verify new/vela_app.bin work/app
```

验证后按单分区刷入，观测开机与对应功能。异常则刷回 `Theme1/` 原镜像。

---

## 结论

- **视频表盘：按用户要求保留，不删。**
- **最安全的起点**：删 `demo/debug/sale/check_tool`（均可忽略）、`vendor/gps/gnss_demo.bin`（演示程序）。
- **中等收益**：`system/ota/` 动画（17 MB，仅升级界面用）；`misc/media/`（10 MB，冥想音乐）。
- **待验证**：`font` 的 MiSansF 三款（13 MB）需先在设备上确认是否用于繁体/兜底。
- **对动画流畅度最可能有帮助的**：减少常驻应用（如 `breath`/`walkie_talkie`）→ 降低内存与后台负载，但必须实测确认。
- 注意：以上都是**体积/负载**优化，不改动画参数；直接改动画参数属于 Tier 2（改内嵌 rootfs 配置或 patch ELF）。
