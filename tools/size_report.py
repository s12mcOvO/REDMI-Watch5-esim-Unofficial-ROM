#!/usr/bin/env python3
"""
size_report.py - report space usage of Vela romfs partitions.

Examples:
    python3 tools/size_report.py Theme1/vela_app.bin --top 25
    python3 tools/size_report.py Theme1                 # summarise every romfs image
    python3 tools/size_report.py Theme1 --json out.json # machine readable
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vela_romfs import load_image, walk, file_data_off, TYPE_DIR  # noqa: E402

ROOTS = ("vela_font.bin", "vela_app.bin", "vela_watchface.bin", "vela_system.bin",
         "vela_vendor.bin", "vela_misc.bin", "vela_quickapp.bin", "vela_i18n.bin")


def iter_files(image):
    data, volume, first, _ = load_image(image)
    stack = walk(data, first, len(data))
    out = []

    def rec(nodes, prefix):
        for ino in nodes:
            path = prefix + ino["name"]
            if ino["type"] == TYPE_DIR:
                rec(ino["children"], path + "/")
            else:
                out.append((path, ino["size"]))

    rec(stack, "")
    return volume, out


def report_image(image, top):
    volume, files = iter_files(image)
    total = sum(s for _, s in files)
    print("=" * 78)
    print("%s  (volume %r)" % (image, volume))
    print("  files: %d   data: %d bytes (%.1f MB)" % (len(files), total, total / 1048576))
    print("  largest %d:" % top)
    for path, size in sorted(files, key=lambda x: -x[1])[:top]:
        print("    %10d  %6.2f%%  %s" % (size, 100.0 * size / max(total, 1), path))
    return {"image": image, "volume": volume, "files": len(files), "bytes": total,
            "entries": [{"path": p, "size": s} for p, s in files]}


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="a romfs .bin, or a Theme directory")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--json")
    args = ap.parse_args(argv)

    images = []
    if os.path.isdir(args.target):
        for name in ROOTS:
            p = os.path.join(args.target, name)
            if os.path.exists(p):
                images.append(p)
    else:
        images.append(args.target)

    results = [report_image(p, args.top) for p in images]
    if args.json:
        with open(args.json, "w") as f:
            json.dump(results, f, indent=2)
        print("\nwrote %s" % args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
