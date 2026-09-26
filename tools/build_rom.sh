#!/usr/bin/env bash
# build_rom.sh - 基于官方 3.110.078 生成定制 ROM
#
# 用法:
#   tools/build_rom.sh <官方包目录> <字体bin> <输出目录>
# 例:
#   tools/build_rom.sh ~/Downloads/RW5e-official/extracted Theme1/vela_font.bin ~/Downloads/RW5e-new
#
# 说明:
#   - 官方基线: 使用官方 3.110.078 全部分区 (system/ap/app/misc/watchface 等保持官方)
#   - 字体:     用给定 vela_font.bin 覆盖
#   - quickapp: 删除以下预装游戏
#       com.vela.minigame.2048 / com.vela.minigame.colorblock /
#       com.application.watch.24count / com.application.N67.MemoryCard /
#       com.application.watch.fistPower / com.vela.game.bridge /
#       com.xiaomi.vela.dadishu
set -euo pipefail

OFFICIAL="${1:?官方包解压目录}"
FONT="${2:?字体 vela_font.bin 路径}"
OUTDIR="${3:?输出目录}"
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
THEME="$OUTDIR/Theme_3.110.078"
WORK="$(mktemp -d)"

echo "[1/4] 复制官方基线 -> $THEME"
rm -rf "$THEME"; mkdir -p "$THEME"
cp "$OFFICIAL"/* "$THEME"/

echo "[2/4] 覆盖字体"
cp "$FONT" "$THEME/vela_font.bin"

echo "[3/4] quickapp 去游戏"
python3 "$ROOT/tools/vela_romfs.py" extract "$OFFICIAL/vela_quickapp.bin" "$WORK/qa" >/dev/null
for g in com.vela.minigame.2048 com.vela.minigame.colorblock \
         com.application.watch.24count com.application.N67.MemoryCard \
         com.application.watch.fistPower com.vela.game.bridge \
         com.xiaomi.vela.dadishu; do
  rm -f "$WORK/qa/${g}"*.rpk
done
max=$(stat -f%z "$OFFICIAL/vela_quickapp.bin" 2>/dev/null || stat -c%s "$OFFICIAL/vela_quickapp.bin")
python3 "$ROOT/tools/vela_romfs.py" pack "$WORK/qa" "$THEME/vela_quickapp.bin" \
        --volume quickapp --max-size "$max"
python3 "$ROOT/tools/vela_romfs.py" verify "$THEME/vela_quickapp.bin" "$WORK/qa"

echo "[4/4] 打包 zip"
mkdir -p "$OUTDIR"
( cd "$OUTDIR" && zip -qr "Theme_3.110.078.zip" "Theme_3.110.078" )
rm -rf "$WORK"
echo "完成: $OUTDIR/Theme_3.110.078.zip"
