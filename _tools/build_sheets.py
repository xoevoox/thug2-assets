import os, sys, math, json, time
from PIL import Image

D = "/sessions/modest-hopeful-ritchie/mnt/Games/THUG2-Assets"
IDX = os.path.join(D, "_index")
SHEETS = os.path.join(IDX, "sheets")
TILE, COLS, PER_SHEET = 96, 14, 280
DEADLINE = time.time() + float(sys.argv[1]) if len(sys.argv) > 1 else time.time() + 480

os.makedirs(SHEETS, exist_ok=True)

def checker(w, h, s=8):
    bg = Image.new('RGB', (w, h), (110, 110, 110))
    px = bg.load()
    for y in range(h):
        for x in range(w):
            if ((x // s) + (y // s)) % 2:
                px[x, y] = (150, 150, 150)
    return bg

CHECK = checker(TILE, TILE)

# collect leaf dirs with pngs
groups = {}
for root, dirs, files in os.walk(D):
    if root.startswith(IDX):
        continue
    pngs = sorted(f for f in files if f.lower().endswith('.png'))
    if pngs:
        groups[os.path.relpath(root, D)] = pngs

meta = {}
made = skipped = 0
for rel in sorted(groups):
    files = groups[rel]
    nsheets = math.ceil(len(files) / PER_SHEET)
    slug = rel.replace(os.sep, '__')
    meta[rel] = {'count': len(files), 'sheets': []}
    for s in range(nsheets):
        name = '%s%s.jpg' % (slug, '' if nsheets == 1 else '_p%d' % (s + 1))
        meta[rel]['sheets'].append(name)
        out = os.path.join(SHEETS, name)
        if os.path.exists(out):
            skipped += 1
            continue
        if time.time() > DEADLINE:
            print('budget reached'); json.dump(meta, open(os.path.join(IDX, 'sheets.json'), 'w')); sys.exit(2)
        chunk = files[s * PER_SHEET:(s + 1) * PER_SHEET]
        rows = math.ceil(len(chunk) / COLS)
        sheet = Image.new('RGB', (COLS * TILE, rows * TILE), (32, 32, 32))
        for i, f in enumerate(chunk):
            try:
                im = Image.open(os.path.join(D, rel, f))
                im.thumbnail((TILE, TILE), Image.LANCZOS)
                if im.mode in ('RGBA', 'LA', 'P'):
                    im = im.convert('RGBA')
                    tile = CHECK.copy()
                    tile.paste(im, ((TILE - im.width) // 2, (TILE - im.height) // 2), im)
                else:
                    tile = Image.new('RGB', (TILE, TILE), (32, 32, 32))
                    tile.paste(im.convert('RGB'), ((TILE - im.width) // 2, (TILE - im.height) // 2))
                sheet.paste(tile, ((i % COLS) * TILE, (i // COLS) * TILE))
            except Exception:
                pass
        sheet.save(out, quality=82, optimize=True)
        made += 1

json.dump(meta, open(os.path.join(IDX, 'sheets.json'), 'w'))
print('sheets made:', made, 'already present:', skipped, 'groups:', len(groups))
