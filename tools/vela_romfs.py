#!/usr/bin/env python3
"""
vela_romfs.py - inspect / unpack / repack Xiaomi Vela romfs partitions
                (Redmi Watch 5 eSIM: vela_font/app/system/vendor/misc/i18n/... .bin)

On-disk format (genromfs-style, little-endian-free / big-endian fields):

    superblock @ 0:
        char   magic[8] = "-rom1fs-"
        u32    total_size
        u32    checksum            (not validated on boot)
        char   volume_name[]       (NUL terminated, padded to 16)

    inode:
        u32    next;      low 4 bits = type, high bits = offset of next sibling
        u32    spec_info; 0 for files, offset of first child for directories
        u32    size;      file size (0 for directories)
        u32    checksum;  non-standard, NOT validated (this repo's custom fonts use 0)
        char   name[];    NUL terminated, header+name padded to 16

    type values: 2 = regular file, 9 = directory (0/1 used by "." / ".." markers)

The checksum field is deliberately written as 0 by this tool.  This is safe for
the Redmi Watch 5 eSIM because the three customised `vela_font.bin` images
shipped in this repository already contain all-zero checksums and boot fine.

Commands:
    list    <image>
    extract <image> <outdir>
    pack    <indir> <image> [--volume NAME]
    verify  <image> <indir>          # structural + byte content comparison

WARNING: repacking modifies a flash partition.  Always keep the original Theme*
folders as a rollback and only flash images you have tested on a device you can
unbrick (fastboot / MIFlash / UART).
"""

import argparse
import os
import struct
import sys

MAGIC = b"-rom1fs-"
ALIGN = 16
TYPE_REG = 2
TYPE_DIR = 9


def align_up(n, a=ALIGN):
    return (n + a - 1) & ~(a - 1)


def read_inode(data, off):
    nxt, spec, size, cksum = struct.unpack(">IIII", data[off:off + 16])
    end = data.find(b"\x00", off + 16)
    if end < 0:
        raise ValueError("unterminated name at 0x%x" % off)
    name = data[off + 16:end].decode("utf-8", "surrogateescape")
    return {
        "off": off,
        "type": nxt & 0xF,
        "next": nxt & ~0xF,
        "spec": spec,
        "size": size,
        "cksum": cksum,
        "name": name,
        "name_off": off + 16,
    }


def walk(data, start, end):
    """Depth-first walk.  start = first child offset, end = exclusive bound."""
    nodes = []
    off = start
    seen = set()
    while off and start <= off < end and off not in seen:
        seen.add(off)
        ino = read_inode(data, off)
        if ino["name"] in (".", ".."):
            off = ino["next"]
            continue
        if ino["type"] == TYPE_DIR:
            child_start = ino["spec"]
            child_end = ino["next"] or end
            ino["children"] = walk(data, child_start, child_end)
        else:
            ino["children"] = []
        nodes.append(ino)
        off = ino["next"]
    return nodes


def load_image(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != MAGIC:
        raise ValueError("not a romfs image: %s" % path)
    decl, _ = struct.unpack(">II", data[8:16])
    name_end = data.find(b"\x00", 16)
    volume = data[16:name_end].decode("utf-8", "surrogateescape")
    first = align_up(16 + len(data[16:name_end]) + 1)
    return data, volume, first, decl


def file_data_off(ino):
    return align_up(ino["name_off"] + len(ino["name"].encode("utf-8", "surrogateescape")) + 1)


# --------------------------------------------------------------------------- list

def cmd_list(args):
    data, volume, first, decl = load_image(args.image)
    print("image  : %s" % args.image)
    print("volume : %r" % volume)
    print("size   : %d (declared %d, %d trailing padding)" % (len(data), decl, len(data) - decl))
    total = 0

    def dump(nodes, depth):
        nonlocal total
        for ino in nodes:
            if ino["type"] == TYPE_DIR:
                print("%s%s/" % ("  " * depth, ino["name"]))
                dump(ino["children"], depth + 1)
            else:
                print("%s%-44s %10d" % ("  " * depth, ino["name"], ino["size"]))
                total += ino["size"]

    dump(walk(data, first, len(data)), 0)
    print("file data total: %d bytes" % total)


# ------------------------------------------------------------------------ extract

def cmd_extract(args):
    data, volume, first, _ = load_image(args.image)
    os.makedirs(args.outdir, exist_ok=True)
    count = 0

    def do(nodes, base):
        nonlocal count
        for ino in nodes:
            target = os.path.join(base, ino["name"])
            if ino["type"] == TYPE_DIR:
                os.makedirs(target, exist_ok=True)
                do(ino["children"], target)
            else:
                off = file_data_off(ino)
                with open(target, "wb") as f:
                    f.write(data[off:off + ino["size"]])
                count += 1

    do(walk(data, first, len(data)), args.outdir)
    print("extracted %d files (volume %r) -> %s" % (count, volume, args.outdir))


# --------------------------------------------------------------------------- pack

def scan_dir(root):
    entries = []
    for name in sorted(os.listdir(root)):
        full = os.path.join(root, name)
        if os.path.isdir(full):
            entries.append([name, "dir", scan_dir(full), None])
        else:
            with open(full, "rb") as f:
                entries.append([name, "file", f.read(), None])
    return entries


def layout(nodes, off, continuation):
    """Assign offsets in pre-order.  `continuation` is the offset a final sibling
    should point at (the parent's own next sibling, or 0 at root)."""
    for ent in nodes:
        name, kind, payload = ent[0], ent[1], ent[2]
        ino_off = off
        data_off = align_up(ino_off + 16 + len(name.encode("utf-8")) + 1)
        if kind == "file":
            off = align_up(data_off + len(payload))
            ent[3] = (ino_off, data_off, off)
        else:
            child_chunks, end = layout(payload, data_off, continuation)
            ent[3] = (ino_off, data_off, end)
            ent.append(child_chunks)
            off = end
    return nodes, off


def emit(nodes, continuation):
    chunks = []
    for i, ent in enumerate(nodes):
        name, kind, payload, off_info = ent[0], ent[1], ent[2], ent[3]
        ino_off, data_off, end_off = off_info
        is_last = i == len(nodes) - 1
        nxt_off = continuation if is_last else nodes[i + 1][3][0]
        typ = TYPE_DIR if kind == "dir" else TYPE_REG
        nxt = (nxt_off & ~0xF) | typ
        if kind == "file":
            spec, size, data = 0, len(payload), payload
        else:
            spec, size, data = data_off, 0, None
        header = struct.pack(">IIII", nxt, spec, size, 0) + name.encode("utf-8") + b"\x00"
        header += b"\x00" * (align_up(len(header)) - len(header))
        chunks.append((ino_off, header))
        if kind == "file":
            pad = b"\x00" * ((align_up(len(data)) - len(data)) if len(data) % ALIGN else 0)
            chunks.append((data_off, data + pad))
        else:
            chunks.extend(emit(ent[4], nxt_off))
    return chunks


def cmd_pack(args):
    tree = scan_dir(args.indir)
    first = align_up(16 + len(args.volume.encode("utf-8")) + 1)
    tree, end = layout(tree, first, 0)
    chunks = emit(tree, 0)
    total = max(off + len(b) for off, b in chunks)
    if args.max_size and total > args.max_size:
        raise SystemExit(
            "refusing to write %d bytes: exceeds partition limit %d (would overflow)"
            % (total, args.max_size)
        )
    sb = bytearray(MAGIC)
    sb += struct.pack(">I", total) + struct.pack(">I", 0)
    sb += args.volume.encode("utf-8") + b"\x00"
    sb += b"\x00" * (align_up(len(sb)) - len(sb))
    out = bytearray(sb) + b"\x00" * (total - len(sb))
    for off, b in chunks:
        out[off:off + len(b)] = b
    with open(args.image, "wb") as f:
        f.write(out)
    print("packed %s (volume %r, %d bytes)" % (args.image, args.volume, len(out)))


# ------------------------------------------------------------------------- verify

def collect_image(nodes, base, out):
    for ino in nodes:
        key = (base + "/" + ino["name"]).lstrip("/")
        if ino["type"] == TYPE_DIR:
            out[key] = ("dir", 0, None)
            collect_image(ino["children"], key, out)
        else:
            out[key] = ("file", ino["size"], ino)


def cmd_verify(args):
    data, volume, first, _ = load_image(args.image)
    img = {}
    collect_image(walk(data, first, len(data)), "", img)
    disk = {}

    def scan(root, rel):
        for name in os.listdir(root):
            full = os.path.join(root, name)
            key = (rel + "/" + name).lstrip("/")
            if os.path.isdir(full):
                disk[key] = ("dir", 0)
                scan(full, key)
            else:
                disk[key] = ("file", os.path.getsize(full))

    scan(args.indir, "")
    problems = []
    for key, (kind, size, ino) in img.items():
        if key not in disk:
            problems.append("missing on disk: " + key)
            continue
        dk, ds = disk[key]
        if dk != kind or ds != size:
            problems.append("mismatch: %s image=%s/%d disk=%s/%d" % (key, kind, size, dk, ds))
        elif kind == "file":
            with open(os.path.join(args.indir, key), "rb") as f:
                if f.read() != data[file_data_off(ino):file_data_off(ino) + size]:
                    problems.append("content differs: " + key)
    for key in disk:
        if key not in img:
            problems.append("extra on disk: " + key)
    if problems:
        print("VERIFY FAILED (%d problems)" % len(problems))
        for p in problems[:40]:
            print("  " + p)
        return 1
    print("VERIFY OK: %d entries, all names/sizes/content match" % len(img))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("image"); p.set_defaults(func=cmd_list)
    p = sub.add_parser("extract"); p.add_argument("image"); p.add_argument("outdir"); p.set_defaults(func=cmd_extract)
    p = sub.add_parser("pack"); p.add_argument("indir"); p.add_argument("image")
    p.add_argument("--volume", default="image")
    p.add_argument("--max-size", type=int, default=0,
                   help="refuse to write if the image would be larger than this many bytes")
    p.set_defaults(func=cmd_pack)
    p = sub.add_parser("verify"); p.add_argument("image"); p.add_argument("indir"); p.set_defaults(func=cmd_verify)
    args = ap.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
