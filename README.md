# Tony Hawk's Underground 2 — extracted asset archive

Everything visual pulled out of the installed PC copy of THUG2 and converted to
open formats. Source was the Wine prefix at `thug2/drive_c/Program Files (x86)/Activision/Tony Hawk's Underground 2/Game/Data`.
Nothing in the game folder was modified.

Open **`INDEX.html`** in a browser to browse the whole thing.

## What's here

| Folder | Contents | Count |
|---|---|---|
| `loading-screens/english/` | The main set, all 640×448 | 64 |
| `loading-screens/french/` | French set — mostly a different, busier 512×512 composition | 64 |
| `loading-screens/german/` | German set, same deal | 64 |
| `images/` | Menu sprites, level-select art, HUD panels, graffiti tags, create-a-skater parts, particles, faces, themes | ~2,180 |
| `textures/` | Board decks, cars, sponsor logos, skater body textures, scuffs | ~660 |
| `fonts/` | In-game font and button-prompt sheets | 8 |
| `levels/<LEVEL>_textures/` | Every environment texture per level, unpacked from the `.tex.xbx` dictionaries | ~12,000 |
| `models/.../<NAME>_textures/` | Skater, pedestrian, cutscene and prop textures | ~7,000 |
| `movies/mp4/` | Intro, credits, pro bails, sponsor bumpers — H.264 | 24 |
| `movies/frames/` | Four stills per video (at 15/40/65/90% of runtime) | 96 |
| `extras/` | Box art, game icons, installer logo, PC manual PDF, readme |  |
| `_index/` | Contact sheets and thumbnails used by `INDEX.html` |  |
| `_tools/` | The decoders, so you can re-run or adapt any of this |  |
| `_manifest_images.csv`, `_manifest_textures.csv` | Source path → dimensions → format for every file |  |

Total: **21,539 PNGs** plus 24 videos. All PNGs keep their alpha channel where the
source had one; fully-opaque images were written as RGB to save space.

## Good banner candidates

The 640×448 English loading screens are the obvious picks — they're full-scene
composites with graffiti lettering already built in. The French and German sets
are worth a look too: most of them are a different, denser 512×512 collage
rather than a translation of the English art, so all 192 are distinct images.
Beyond those, `images/MainmenuSprites/`, `images/Tags/` and `textures/Logos/`
have the cleanest standalone graphics, and the `movies/frames/` stills from
`hawk`, `probail1/2` and `skatopia` are high-motion and crop well.

## Format notes

These formats aren't really documented anywhere, so — for whoever needs this next:

### `.img.xbx` — standalone images

32-byte header, little-endian:

| Offset | Type | Meaning |
|---|---|---|
| 0x00 | u32 | version (always 2) |
| 0x04 | u32 | bits-per-pixel class (8) |
| 0x08 | u32 | width |
| 0x0C | u32 | height |
| 0x10 | u32 | format: `0` = 32bpp BGRA, `19` = 8bpp palettised |
| 0x14 | u32 | reserved (0) |
| 0x18 | u16, u16 | width, height again |
| 0x1C | u32 | palette size in bytes — `0`, `64` (16 entries) or `1024` (256 entries) |

Then the palette (BGRA entries) if present, followed by pixel or index data.

Three things will bite you:

1. **Palette comes first**, before the index data — not after.
2. **Power-of-two images are Xbox Morton-swizzled.** Interleave the x and y bits,
   taking one x bit then one y bit alternately, for as many bits as each axis has.
   Non-power-of-two images (like the 640×448 loading screens) are stored linearly.
3. **Rows are bottom-up.** Flip vertically or all your text comes out upside down.

### `.tex.xbx` — texture dictionaries

`u32 version (1)`, `u32 texture_count`, then per texture a 32-byte header:

| Offset | Type | Meaning |
|---|---|---|
| +0x00 | u32 | checksum — the hashed original texture name; the string itself isn't stored |
| +0x04 | u32 | width |
| +0x08 | u32 | height |
| +0x0C | u32 | mip level count |
| +0x10 | u32 | bits per pixel (32, or 8 for palettised) |
| +0x14 | u32 | 32 |
| +0x18 | u32 | compression: `0` = uncompressed BGRA, `1`/`2` = DXT1, `5` = DXT5 |
| +0x1C | u32 | palette size in bytes (0 unless 8bpp) |

Then the palette if present, then **each mip level as a `u32` byte count followed
by that many bytes**. Level 0 is full resolution; this archive only keeps level 0.
DXT blocks are stored linearly (not swizzled), but the image is still bottom-up,
and uncompressed/palettised entries still follow the power-of-two swizzle rule.

Berlin (`levels/BE/`) is the only level that uses 8bpp palettised entries, and a
parser that assumes every entry is DXT will blow up on texture 236 of 753.

Because only the name hash survives, textures are named `<index>_<checksum>.png`.

### `.bik` — Bink video

ffmpeg decodes these natively (`binkvideo` + `binkaudio_dct`), no RAD tools needed.

## Not included

`Game/Data/streams/music/` holds 137 more `.bik` files — that's the licensed
soundtrack as Bink audio, not game art. It converts fine with ffmpeg if you want
it for your own archive, but it's commercial music rather than Neversoft assets,
so it's left alone here.

Everything in this folder is Activision/Neversoft artwork, extracted from a legally
installed copy for personal and fan use. Worth keeping in mind for anything
public-facing.
