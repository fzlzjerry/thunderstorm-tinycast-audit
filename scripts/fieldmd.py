#!/usr/bin/env python3
"""Parse __swift5_fieldmd of a thin arm64 Mach-O (read only) and emit
type -> [(field name, kind)] with type names resolved from context descriptors.
Usage: fieldmd.py BINARY OUTJSON
"""
import json, struct, sys

BIN, OUT = sys.argv[1], sys.argv[2]
data = open(BIN, "rb").read()

# --- load commands: collect sections with (vmaddr, fileoff, size)
magic, cpu, sub, ftype, ncmds, sizeofcmds, flags, _ = struct.unpack_from("<IiiIIIII", data, 0)
assert magic == 0xFEEDFACF, hex(magic)
off = 32
sections = {}
segs = []
for _ in range(ncmds):
    cmd, cmdsize = struct.unpack_from("<II", data, off)
    if cmd == 0x19:  # LC_SEGMENT_64
        segname = data[off + 8:off + 24].rstrip(b"\0").decode()
        vmaddr, vmsize, fileoff, filesize = struct.unpack_from("<QQQQ", data, off + 24)
        segs.append((segname, vmaddr, vmsize, fileoff, filesize))
        nsects = struct.unpack_from("<I", data, off + 64)[0]
        so = off + 72
        for _ in range(nsects):
            sectname = data[so:so + 16].rstrip(b"\0").decode()
            seg = data[so + 16:so + 32].rstrip(b"\0").decode()
            addr, size, foff = struct.unpack_from("<QQI", data, so + 32)
            sections[(seg, sectname)] = (addr, size, foff)
            so += 80
    off += cmdsize


def v2f(addr):
    for name, va, vs, fo, fs in segs:
        if va <= addr < va + vs:
            return fo + (addr - va)
    return None


def f2v(fo):
    for name, va, vs, sfo, fs in segs:
        if sfo <= fo < sfo + fs:
            return va + (fo - sfo)
    return None


def rel(fo, indirectable=False):
    """resolve a 32-bit relative pointer stored at file offset fo -> target file offset"""
    if fo is None or fo < 0 or fo + 4 > len(data):
        return None
    d = struct.unpack_from("<i", data, fo)[0]
    if d == 0:
        return None
    if indirectable and (d & 1):
        return None  # indirect via GOT: not resolved
    v = f2v(fo)
    if v is None:
        return None
    t = v2f(v + d)
    if t is None or t < 0 or t >= len(data):
        return None
    return t


def cstr(fo):
    if fo is None or fo >= len(data):
        return None
    e = data.index(b"\0", fo)
    return data[fo:e].decode("utf-8", "replace")


def ctx_name(fo, depth=0):
    """name of a context descriptor at file offset fo, with parents"""
    if fo is None or depth > 6 or fo + 12 > len(data):
        return "?"
    flags = struct.unpack_from("<I", data, fo)[0]
    kind = flags & 0x1F
    parent = rel(fo + 4, True)
    if kind == 0:  # module
        return cstr(rel(fo + 8)) or "?"
    if kind in (16, 17, 18):  # class, struct, enum
        name = cstr(rel(fo + 8))
        p = ctx_name(parent, depth + 1) if parent is not None else "?"
        return f"{p}.{name}"
    if kind == 1:  # extension
        return ctx_name(parent, depth + 1) + "(ext)"
    if kind == 2:  # anonymous
        return ctx_name(parent, depth + 1) + "(anon)"
    return f"?kind{kind}"


def mangled(fo):
    """decode a mangled name; resolve direct symbolic refs (0x01)"""
    if fo is None:
        return None
    out, i = [], fo
    while True:
        b = data[i]
        if b == 0:
            break
        if 1 <= b <= 0x17:
            if b == 0x01:
                out.append("<" + ctx_name(rel(i + 1)) + ">")
            else:
                out.append(f"<ref{b}>")
            i += 5
            continue
        if 0x18 <= b <= 0x1F:
            i += 9
            out.append("<ref>")
            continue
        out.append(chr(b))
        i += 1
    return "".join(out)


addr, size, foff = sections[("__TEXT", "__swift5_fieldmd")]
p, end = foff, foff + size
types = []
while p < end:
    mtn = rel(p)
    nfields = struct.unpack_from("<I", data, p + 12)[0]
    recsize = struct.unpack_from("<H", data, p + 10)[0]
    kind = struct.unpack_from("<H", data, p + 8)[0]
    name = mangled(mtn) if mtn is not None else None
    fields = []
    q = p + 16
    for _ in range(nfields):
        fl = struct.unpack_from("<I", data, q)[0]
        fname = cstr(rel(q + 8))
        fty = mangled(rel(q + 4)) if struct.unpack_from("<i", data, q + 4)[0] else None
        fields.append([fname, fty])
        q += recsize
    types.append({"type": name, "kind": kind, "fields": fields})
    p = q
json.dump(types, open(OUT, "w"), indent=0, ensure_ascii=False)
print("descriptors:", len(types))
