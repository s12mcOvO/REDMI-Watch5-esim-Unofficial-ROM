# tools

REDMI Watch 5 eSIM (Vela / o65m) 固件处理工具。

## 环境

- Python 3（仅标准库即可运行 `vela_romfs.py` / `size_report.py`）
- 生成苹方字体额外需要：`fonttools`、`otf2ttf`（建议 venv）

```bash
python3 -m venv venv && venv/bin/pip install fonttools otf2ttf
```

## vela_romfs.py

Vela romfs 分区的 `list / extract / pack / verify`。

```bash
python3 tools/vela_romfs.py list    Theme1/vela_app.bin
python3 tools/vela_romfs.py extract Theme1/vela_app.bin work/app
python3 tools/vela_romfs.py pack    work/app new/vela_app.bin --volume image --max-size 97461248
python3 tools/vela_romfs.py verify  new/vela_app.bin work/app
```

要点：

- 校验字段非标准且**开机不校验**（仓库自定义 `vela_font.bin` 校验位全 0 仍可启动），
  因此重打包写入 0 即可。
- `pack --max-size` 会拒绝超出分区容量的镜像，避免刷入溢出。

## size_report.py

统计各 romfs 分区的体积占用与最大文件。

```bash
python3 tools/size_report.py Theme1 --top 20
python3 tools/size_report.py Theme1/vela_app.bin --json app.json
```

## build_pingfang_font.py

用 macOS 自带苹方生成手表字体目录（CFF→TrueType 转换 + 子集）。

```bash
venv/bin/python tools/build_pingfang_font.py outfont
python3 tools/vela_romfs.py pack outfont new/vela_font.bin --volume font
```

注意：苹方为 Apple 专有字体，随 ROM 分发存在授权风险。

## build_rom.sh

以官方固件包为基线生成定制 ROM（模板）。

```bash
tools/build_rom.sh <官方包解压目录> <字体bin> <输出目录>
```

## 已知结论

- **AVB**：`ap / CP / CRF / dsp / ota / sensor / tee`（及 `_f`）由 RSA+AVB 签名保护，
  **不可修改**；`font / app / system / vendor / misc / watchface / i18n / quickapp` 无 AVB，可改。
- **动画参数**：launcher 的 `launcher.res` 为私有 `EGMI` 编译容器，无明文参数，无法从资源层修改。
