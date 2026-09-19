"""Parser for Neversoft THUG2 .tex.xbx texture dictionaries.

File:   u32 version(1), u32 texture_count, then each texture:
Texture header (32 bytes):
        u32 checksum (hashed name), u32 width, u32 height, u32 mip_levels,
        u32 bpp(32), u32 ?(32), u32 dxt_type, u32 ?(0)
        dxt_type: 0 = uncompressed 32bpp BGRA, 1/2 = DXT1, 5 = DXT5
Then per mip level: u32 byte_count followed by that many bytes of data.
"""
import io
import struct
import numpy as np
from PIL import Image
import thug2img


def parse(path):
    raw = open(path, 'rb').read()
    ver, cnt = struct.unpack('<II', raw[:8])
    if ver != 1:
        raise ValueError('unsupported tex version %d' % ver)
    off = 8
    out = []
    for _ in range(cnt):
        cs, w, h, lv, bpp, f5, dxt, palbytes = struct.unpack('<8I', raw[off:off + 32])
        off += 32
        pal = b''
        if palbytes:
            pal = raw[off:off + palbytes]
            off += palbytes
        mips = []
        for _L in range(lv):
            (ds,) = struct.unpack('<I', raw[off:off + 4])
            off += 4
            mips.append(raw[off:off + ds])
            off += ds
        out.append(dict(checksum=cs, width=w, height=h, dxt=dxt, bpp=bpp,
                        palette=pal, data=mips[0] if mips else b''))
    return out, off, len(raw)


def _dds(w, h, fourcc, data):
    hdr = bytearray(128)
    hdr[0:4] = b'DDS '
    struct.pack_into('<I', hdr, 4, 124)
    struct.pack_into('<I', hdr, 8, 0x1 | 0x2 | 0x4 | 0x1000 | 0x80000)  # caps/h/w/pixelformat/linearsize
    struct.pack_into('<I', hdr, 12, h)
    struct.pack_into('<I', hdr, 16, w)
    struct.pack_into('<I', hdr, 20, len(data))
    struct.pack_into('<I', hdr, 28, 1)      # mipmap count
    struct.pack_into('<I', hdr, 76, 32)     # pixelformat size
    struct.pack_into('<I', hdr, 80, 0x4)    # DDPF_FOURCC
    hdr[84:88] = fourcc
    struct.pack_into('<I', hdr, 108, 0x1000)  # DDSCAPS_TEXTURE
    return bytes(hdr) + data


def to_image(tex):
    w, h, dxt, data = tex['width'], tex['height'], tex['dxt'], tex['data']
    if w <= 0 or h <= 0 or not data:
        raise ValueError('empty texture')
    if tex.get('palette'):
        pal = np.frombuffer(tex['palette'], dtype=np.uint8).reshape(-1, 4)[:, [2, 1, 0, 3]]
        idx = np.frombuffer(data[:w * h], dtype=np.uint8)
        if len(idx) < w * h:
            raise ValueError('truncated palettised texture')
        if (w & (w - 1)) == 0 and (h & (h - 1)) == 0:
            idx = idx[thug2img.morton_map(w, h)]
        if idx.max(initial=0) >= len(pal):
            pal = np.vstack([pal, np.zeros((int(idx.max()) + 1 - len(pal), 4), np.uint8)])
        return Image.fromarray(pal[idx].reshape(h, w, 4)[::-1], 'RGBA')
    if dxt in (1, 2) and len(data) >= max(1, w // 4) * max(1, h // 4) * 8:
        im = Image.open(io.BytesIO(_dds(w, h, b'DXT1', data)))
    elif dxt == 5 and len(data) >= max(1, w // 4) * max(1, h // 4) * 16:
        im = Image.open(io.BytesIO(_dds(w, h, b'DXT5', data)))
    elif dxt == 0 and len(data) >= w * h * 4:
        px = np.frombuffer(data[:w * h * 4], dtype=np.uint8).reshape(-1, 4)
        if (w & (w - 1)) == 0 and (h & (h - 1)) == 0:
            px = px[thug2img.morton_map(w, h)]
        return Image.fromarray(px[:, [2, 1, 0, 3]].reshape(h, w, 4)[::-1], 'RGBA')
    else:
        raise ValueError('unhandled dxt=%s %dx%d %d bytes' % (dxt, w, h, len(data)))
    im.load()
    return im.convert('RGBA').transpose(Image.FLIP_TOP_BOTTOM)  # stored bottom-up
