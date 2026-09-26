# REDMI Watch 5 eSIM — 界面动画流畅度优化方案

> 目标：提升系统 UI（滑动、切换、控件动效）的流畅度。
> 约束：只做方案与工具，暂不改固件；设备可实测、可救砖。
> 本文所有结论基于对仓库内 `Theme1/` 分区镜像的静态分析。

---

## 1. 现状勘查（已确认）

### 1.1 分区与格式

使用 `tools/vela_romfs.py` 可直接解包/重打包以下 romfs 分区：

| 分区 | 大小 | 内容 |
|------|------|------|
| `vela_font.bin` | 27.6 MB | 6 个 MiSans 字重，每个约 4.6 MB |
| `vela_app.bin` | 95.9 MB | 94 个 `.res` 资源包（`launcher.res`、`breath.res` 20.6 MB 等） |
| `vela_watchface.bin` | 81.3 MB | 39 个预置表盘 |
| `vela_system.bin` | 72.3 MB | 开机/充电/OTA/恢复动画资源 + `wechat`/`whatsapp` |
| `vela_vendor.bin` | 19.6 MB | 射频/传感器/GPS/NFC/触摸等固件 |
| `vela_misc.bin` | 17.9 MB | 时区、运动语音、SSL 证书 |
| `vela_quickapp.bin` | 2.6 MB | 快应用（含微信 rpk） |
| `vela_i18n.bin` | 0.7 MB | 翻译 |

其余为启动链路分区：`sbl`、`tee`、`dsp`、`ap`、`CP`、`sensor`、`ota`、`mmap`、`nv` 等，**禁止改动**。

### 1.2 系统架构

- `vela_ap.bin` 中出现 `apps/graphics/lvgl/lvgl/src/misc/lv_anim.c` 等路径 → **UI 框架是 LVGL**（跑在 Linux 形态的 Vela 上）。
- `vela_ap.bin` 内还含 DVFS / cpufreq / thermal / dbus / iwasm 等字符串 → 存在完整的频率与功耗管理。
- `vela_ap.bin` 是高熵复合镜像（熵 ~7.27 bit/B），内含 ELF（偏移 `0xbb16b8`）、gzip 段、内嵌 romfs（偏移 `0xd184dc`）。**属于启动关键分区。**
- `vela_mmap.bin` 是各内存区域的地址/大小映射表。
- 固件内存在帧率调试输出（`"%.2ffps/%ld"`、`#awidget_refresh_rainbow`），可能可开启 FPS overlay 用于量化。

### 1.3 关键结论

1. **动画时长/缓动/FPS 上限等参数，绝大多数编译进了 `vela_ap.bin`（LVGL 与应用代码），romfs 里没有现成配置文件。**
2. romfs 分区只能间接影响“负载”，不能直接改动画参数。
3. 校验字段非标准且**启动不校验**——实证：三个自定义 `vela_font.bin` 的校验位全为 0 且能正常开机。因此重打包只需保持结构与名字/大小正确即可，工具已据此设计。

---

## 2. 影响动画流畅度的四个层级

| 层级 | 内容 | 可改位置 |
|------|------|----------|
| **L1 渲染管线** | LVGL 刷新周期、draw buffer 大小/数量、双缓冲、vsync、DDR/PSRAM 带宽、GPU/RGA 加速 | `vela_ap.bin`（编译期常量） |
| **L2 频率/功耗** | cpufreq governor、DVFS 最低频率、温控降频阈值 | `vela_ap.bin` / 设备树 / NV |
| **L3 运行负载** | 常驻 app 数量、表盘复杂度、资源包体积、内存占用 | romfs 分区（`app`/`watchface`/`system`） |
| **L4 动画参数** | duration、easing、fps 上限、重绘区域 | `vela_ap.bin` + 各 `.res` |

---

## 3. 优化选项（按风险分层）

### Tier 0 — 零风险，先做（不改固件）
- 量化基线：找/开 FPS overlay，或主观记录卡顿场景（滑动列表、切表盘、打开控制中心）。
- 关闭后台常驻：不必要的快应用、蓝牙常连、自动心率等，观察是否改善。
- 减少预置表盘数量、避免复杂动态表盘。
- 目的：确认瓶颈是“算力/带宽”还是“动画参数过大”。

### Tier 1 — 低风险，仅改 romfs，可用现有工具
- 精简 `vela_font.bin`：保留实际使用的字重（需先确认引用关系）。
- 精简 `vela_watchface.bin`：删除不用的预置表盘。
- 精简 `vela_app.bin` / `vela_quickapp.bin`：删除不用的资源包/快应用。
- **收益**：降低存储与内存压力，减少分配/换页抖动；对动画 FPS 属“间接改善”，需实测对比。
- **风险**：删错被引用的资源会功能缺失甚至开机动画异常；必须逐个验证。

### Tier 2 — 中/高风险，需改 `vela_ap.bin`（本项目主要收益点）
- 调整 LVGL 刷新周期 / 默认动画时长 / 缓冲区大小。
- 调整 cpufreq governor 或 DVFS 最低频率、温控阈值。
- **前提**：先逆向 `vela_ap.bin` 的容器格式（定位内嵌 ELF 与各段），确认未被签名校验，才能安全 patch。
- **风险**：这是启动关键镜像，patch 错误极易变砖；必须有可靠救砖手段后再动。

---

## 4. 工具

### 4.1 已完成：`tools/vela_romfs.py`

```bash
python3 tools/vela_romfs.py list    Theme1/vela_app.bin
python3 tools/vela_romfs.py extract Theme1/vela_app.bin work/app
python3 tools/vela_romfs.py pack    work/app Theme1_new/vela_app.bin --volume app
python3 tools/vela_romfs.py verify  Theme1/vela_app.bin work/app
```

- 已在全部 8 个 romfs 分区上通过“解包 → 重打包 → 逐文件内容比对”验证。
- 重打包时**保持原分区体积不增大**，否则刷入会溢出分区表。

### 4.2 待补工具（按需开发）
- `tools/res_diff.py`：对比两个 `.res`（EGMI 格式）以确认改动。
- `tools/size_report.py`：导出各分区的体积占用，辅助裁剪。
- `tools/ap_container.py`：`vela_ap.bin` 容器解析（Tier 2 前提）。

---

## 5. 验证与回滚流程（设备实测）

1. **备份**：保留原始 `Theme1/2/3`，或另存一份原始镜像。
2. **单变量**：每轮只改一个分区、一个点。
3. **打包**：`vela_romfs.py pack` 后必须 `verify`，并确认新镜像 ≤ 原分区大小。
4. **刷入**：先刷单个非关键分区（如 `vela_font.bin`）验证流程。
5. **观测**：开机 + FPS/主观对比；记录与基线的差异。
6. **回滚**：若异常，立即刷回对应原始分区；确保 fastboot / MIFlash / UART 可用。
7. **晋级**：只有 Tier 1 稳定后，才评估是否进入 Tier 2。

---

## 6. 需要的决定

在开工前需要确认：
1. 是否先做 **Tier 1 资源裁剪**（我可产出候选清单 + 脚本，但被引用关系需要设备上验证）。
2. 是否启动 **Tier 2 `vela_ap.bin` 逆向**（收益最大，但周期长、风险高）。
3. 是否愿意先花时间把 **FPS 量化手段**（debug overlay / 串口日志）打通——这决定后续能否“凭数据”而非“凭感觉”优化。

---

## 7. 深入勘查补充（第二轮，2026-09）

### 7.1 发现：`vela_ap.bin` 内嵌完整 rootfs，可直接编辑配置

`vela_ap.bin` 在偏移 **`0xd1ab98`** 处有一个真实 romfs（卷名 `NSHInitVol`，大小 `4,233,248` 字节），
即系统根目录 `/`，可用 `tools/vela_romfs.py` 解包：

```
lvx_video_config.json       charger_parameters.json
build.prop                  font_config.json
init.d/rcS  rc.sysinit  rc.sysinit.ap
media/{criteria.txt, graph.conf, settings.pfw, default/*.xml}
dbus-1/system.conf          ofonod.aot
mobile-broadband-provider-info/...   ssl/curl/ca-certificates.crt
```

关键配置：
- **`font_config.json`**：只声明 `MiSans-Regular / MiSans-Medium / MiSans-Demibold`
  （`MiSansF-*` 未被引用）→ 字体裁剪有了依据（仍建议设备验证）。
- **`build.prop`**：含 `persist.watchface.video_flag=0`（视频表盘默认关）、蓝牙/调制解调器自启等。
- **`init.d/rcS`**：挂载各 romfs 分区；启动 `mediad / miwear / healthd / chargerd / power_log` 等。
  可在此脚本中加入运行期调优命令（若有对应接口）。
- `media/graph.conf`、`settings.pfw` 是**音频管线**配置（非图形），`Vtun_Video` 为视频 tunnel。

### 7.2 发现：`rcS` 揭示分区挂载点

`/dev/system→/resource/system`、`/dev/app→/resource/app`、`/font`、`/watchface`、
`/quickapp`、`/resource/misc`、`/vendor`。可据此定位每个资源在运行期的路径。

### 7.3 FPS 量化（进行中）

- `vela_ap.bin` 内确有 `"%.2ffps/%ld"`、`#awidget_refresh_rainbow` 等帧率相关字符串，
  说明固件自带帧率统计，但**未找到可通过文件开启的开关**；需在设备上通过隐藏手势/工程模式/串口日志触发。

### 7.4 `vela_ap.bin` 结构（Tier 2 进展）

- `vela_ap.bin` 不是带段表的容器，而是**固定地址 XIP 镜像**：由 `vela_mmap.bin` 可知
  `ap` 映射到 `0x605c0000`。文件头 `0x00–0x294` 是 ARM 向量表（word0=初始 SP，word1=复位向量，
  其余为默认异常向量），`0x294` 起是代码。
- 内嵌 `/etc` rootfs（romfs，卷名 `NSHInitVol`）位于文件偏移 **`0xd1ab98`**，运行时地址 `0x612dab98`；
  该地址作为字面量出现在偏移 `0x16a9d0` 的指针池中，即**代码按固定地址访问**，没有动态段表。
- rootfs 区域为 `[0xd1ab98, 0x11243b8)`，其后仅 992 字节空隙，再往后是下一段内容。
- 文件末尾是 **AVB 脚注 `AVBf`**，指向 vbmeta（见 7.5）。

### 7.5 决定性结论：`ap` 受 AVB 保护，Tier 2 此路不通

对全部 32 个分区扫描 AVB 脚注，结果：

| 受 AVB 保护（RSA 签名 + SHA256，`algo=1`） | 无 AVB |
|---|---|
| `CP` `CP_f` `CRF` `CRF_f` **`ap`** `ap_f` `dsp` `dsp_f` `ota` `sensor` `sensor_f` `tee` `tee_f` | `app` `font` `i18n` `misc` `quickapp` **`system`** `vendor` `watchface` `sbl` `sbl_bak` `mmap` `nv` … |

对 `ap` 的 vbmeta 校验（`vbmeta@0x14e6000`，描述符 partition=`/dev/ap`）：

```
image_size = 0x14e4120 (21,905,696)
algo       = SHA-256  (实测)
salt       = c97f718f080812a0ac97db77d56b72ffbefb07d3f276597cb8a206064fde22ae
digest     = 9fd955f8aafab6211155bdc0f618015197dbf8e1e81bfdf100391f19e66824ba
sha256(salt || image[0:image_size]) == digest   →   MATCH
```

**即：rootfs 位于被 SHA-256 覆盖的镜像区内，任何改动都会破坏 AVB 校验。**

对照解释：
- 项目一直能改 `font/system/app/watchface/vendor/misc/i18n/quickapp` —— 因为它们**没有 AVB 脚注**，所以能刷。
- `ap`（含 `/etc` rootfs、LVGL 代码、DVFS）**有 AVB**，改了就过不了校验。

**因此：通过修改 `vela_ap.bin` 调整动画/LVGL/DVFS 参数，在未绕过 AVB 的前提下不可行，会导致无法启动。**
要突破只有三条路（都需要设备实测确认）：
1. 解锁/工程模式关闭 AVB（该机型是否支持未知，且可能清数据/失效）；
2. 拿到 OEM 私钥重签名（不可得）；
3. 使用**运行时覆盖**（persist 属性 / 可写分区 `/data`、`/factory_prop`、`nv`）来影响行为，绕开静态镜像。

### 7.6 更新后的路线

1. **立即可做（低风险、非 AVB）**：Tier 1 资源裁剪（`app/font/misc/vendor/system`），见
   `docs/tier1-trim-candidates.md`。
2. **受 AVB 阻断**：~~替换 `ap` 内嵌 rootfs~~ → 不可行。
3. **新方向（中风险）**：排查**运行时覆盖**——是否有 persist 属性 / `/data` 覆盖能改变字体、
   自启服务或渲染行为；这不需要动 `ap`。
4. **待打通**：FPS 量化（设备侧）。
5. **不在本项目范围**：patch LVGL/DVFS 常量（需先有办法绕过 AVB）。
