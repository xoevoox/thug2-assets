"""Decoder for Neversoft THUG2 .img.xbx images (PC/Xbox build).

Format (all little-endian):
  0x00 u32  version (2)
  0x04 u32  bits-per-pixel class (8)
  0x08 u32  width
  0x0C u32  height
  0x10 u32  format flag (0 = 32bpp BGRA, 19 = 8bpp palettised)
  0x14 u32  reserved
  0x18 u16  width  (again)
  0x1A u16  height (again)
  0x1C u32  palette size in bytes (0, 64 = 16 entries, 1024 = 256 entries)
  0x20      palette (BGRA entries) if present, then pixel/index data

Power-of-two textures are stored Xbox Morton ("swizzled") order.
Rows are stored bottom-up, so the decoded image is flipped vertically.
"""
import struct
import numpy as np
from PIL import Image

_MORTON_CACHE = {}


def _is_pot(v):
    return v > 0 and (v & (v - 1)) == 0


def morton_map(w, h):
    """Linear index (y*w+x) -> offset in Xbox-swizzled data."""
    key = (w, h)
    if key in _MORTON_CACHE:
        return _MORTON_CACHE[key]
    xs = np.arange(w, dtype=np.int64)
    ys = np.arange(h, dtype=np.int64)
    xbits = w.bit_length() - 1
    ybits = h.bit_length() - 1
    xoff = np.zeros(w, dtype=np.int64)
    yoff = np.zeros(h, dtype=np.int64)
    shift = xi = yi = 0
    while xi < xbits or yi < ybits:
        if xi < xbits:
            xoff |= ((xs >> xi) & 1) << shift
            shift += 1
            xi += 1
        if yi < ybits:
            yoff |= ((ys >> yi) & 1) << shift
            shift += 1
            yi += 1
    m = (yoff[:, None] + xoff[None, :]).ravel()
    _MORTON_CACHE[key] = m
    return m


def decode(path):
    """Return a top-left-origin RGBA PIL Image."""
    raw = open(path, 'rb').read()
    if len(raw) < 32:
        raise ValueError('file shorter than header')
    ver, _bpp, w, h, fmt, _res = struct.unpack('<IIIIII', raw[:24])
    palbytes = struct.unpack('<I', raw[28:32])[0]
    if ver != 2:
        raise ValueError('unsupported version %d' % ver)
    if w <= 0 or h <= 0 or w > 8192 or h > 8192:
        raise ValueError('implausible dimensions %dx%d' % (w, h))
    body = raw[32:]
    swizzled = _is_pot(w) and _is_pot(h)

    if palbytes == 0:
        need = w * h * 4
        if len(body) < need:
            raise ValueError('truncated 32bpp data (%d < %d)' % (len(body), need))
        px = np.frombuffer(body[:need], dtype=np.uint8).reshape(-1, 4)
        if swizzled:
            px = px[morton_map(w, h)]
        rgba = px[:, [2, 1, 0, 3]].reshape(h, w, 4)
    else:
        need = palbytes + w * h
        if len(body) < need:
            raise ValueError('truncated palettised data (%d < %d)' % (len(body), need))
        pal = np.frombuffer(body[:palbytes], dtype=np.uint8).reshape(-1, 4)[:, [2, 1, 0, 3]]
        idx = np.frombuffer(body[palbytes:palbytes + w * h], dtype=np.uint8)
        if swizzled:
            idx = idx[morton_map(w, h)]
        if idx.max(initial=0) >= len(pal):
            pal = np.vstack([pal, np.zeros((int(idx.max()) + 1 - len(pal), 4), np.uint8)])
        rgba = pal[idx].reshape(h, w, 4)

    return Image.fromarray(rgba[::-1], 'RGBA')  # bottom-up -> top-down
