#!/usr/bin/env python3
"""
build_pingfang_font.py - 用 macOS 自带苹方(PingFang)生成手表字体目录。

背景:
  - 手表 `vela_font.bin` 内含 6 个 TrueType 字体:
      MiSans-{Regular,Medium,Demibold}.ttf   (主字体, 官方为全量 CJK)
      MiSansF-{Regular,Medium,Demibold}.ttf  (221 字形的小型兜底)
  - 苹方是 CFF(PostScript) 轮廓, LVGL/手表现有字体为 TrueType(glyf),
    因此必须 CFF->TrueType 转换 + 子集化控制体积。

依赖 (建议用 venv):
    python3 -m venv venv && venv/bin/pip install fonttools otf2ttf

用法:
    venv/bin/python tools/build_pingfang_font.py <输出目录>
    然后：python3 tools/vela_romfs.py pack <输出目录> new/vela_font.bin --volume font

注意:
  - 苹方为 Apple 专有字体, 随 ROM 分发存在授权风险, 自行评估。
  - 主字体为常用 CJK 子集(~2.9万字), 极生僻字可能缺字。
"""
import os
import subprocess
import sys

PING = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/" \
       "86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc"
SC = {"Regular": 3, "Medium": 7, "Semibold": 11}

MAIN_RANGES = [
    "U+0020-007E", "U+00A0-00FF", "U+0100-017F", "U+2000-206F", "U+2070-209F",
    "U+20A0-20BF", "U+2100-214F", "U+2150-218F", "U+2190-21FF", "U+2200-22FF",
    "U+2300-23FF", "U+2460-24FF", "U+25A0-25FF", "U+2600-26FF", "U+3000-303F",
    "U+3040-309F", "U+30A0-30FF", "U+3100-312F", "U+3200-32FF", "U+3300-33FF",
    "U+3400-4DBF", "U+4E00-9FFF", "U+F900-FAFF", "U+FE30-FE4F", "U+FF00-FFEF",
]

# 官方 MiSansF 的 221 个码点(兜底), 用一个官方 font.bin 解出的文件即可
FALLBACK_CMAP_FROM = os.environ.get("MISANSF_TTF", "")


def set_names(font, family, sub, ps):
    nt = font["name"]
    for nid, val in ((1, family), (2, sub), (4, f"{family} {sub}"), (6, ps),
                     (16, family), (17, sub)):
        nt.setName(val, nid, 3, 1, 0x409)
        nt.setName(val, nid, 1, 0, 0)


def build(outdir, weight, family, sub, psname, ranges=None, unicodes=None):
    from fontTools.ttLib import TTCollection, TTFont
    from fontTools import subset as ftsub

    ttc = TTCollection(PING, lazy=False)
    f = ttc.fonts[SC[weight]]
    opts = ftsub.Options()
    opts.layout_features = []
    opts.notdef_outline = True
    opts.drop_tables = ["EBDT", "EBLC", "GSUB", "GPOS", "GDEF", "DSIG", "BASE",
                        "JSTF", "MATH", "VORG", "trak", "meta", "cidg"]
    subr = ftsub.Subsetter(options=opts)
    if unicodes is not None:
        subr.populate(unicodes=sorted(unicodes))
    else:
        subr.populate(unicodes=ftsub.parse_unicodes(",".join(ranges)))
    subr.subset(f)

    otf = os.path.join(outdir, psname + ".otf")
    ttf = os.path.join(outdir, psname + ".ttf")
    f.flavor = None
    f.save(otf)
    import shutil
    otf2ttf = shutil.which("otf2ttf") or os.path.join(
        os.path.dirname(sys.executable), "otf2ttf")
    subprocess.run([otf2ttf, otf, "-o", ttf, "--overwrite"], check=True)
    os.remove(otf)
    g = TTFont(ttf)
    set_names(g, family, sub, psname)
    g.save(ttf)
    print(f"  {psname:20} glyphs={g['maxp'].numGlyphs:>6} size={os.path.getsize(ttf)}")


def main(outdir):
    os.makedirs(outdir, exist_ok=True)
    for w, sub in (("Regular", "Regular"), ("Medium", "Medium"), ("Semibold", "Demibold")):
        build(outdir, w, "MiSans", sub, f"MiSans-{sub}", ranges=MAIN_RANGES)
    if FALLBACK_CMAP_FROM and os.path.exists(FALLBACK_CMAP_FROM):
        from fontTools.ttLib import TTFont
        fb = set(TTFont(FALLBACK_CMAP_FROM, lazy=True).getBestCmap().keys())
    else:
        fb = set(range(0x20, 0x7F))  # 退化: 仅 ASCII
    for w, sub in (("Regular", "Regular"), ("Medium", "Medium"), ("Semibold", "Demibold")):
        build(outdir, w, "MiSansF", sub, f"MiSansF-{sub}", unicodes=fb)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    main(sys.argv[1])
