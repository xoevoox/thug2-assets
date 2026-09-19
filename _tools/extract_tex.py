import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thug2tex

SRC = "/sessions/modest-hopeful-ritchie/mnt/Games/thug2/drive_c/Program Files (x86)/Activision/Tony Hawk's Underground 2/Game/Data"
DST = "/sessions/modest-hopeful-ritchie/mnt/Games/THUG2-Assets"

todo = []
for root, dirs, files in os.walk(SRC):
    for f in files:
        if f.endswith('.tex.xbx'):
            todo.append(os.path.join(root, f))
todo.sort()
print("tex dictionaries:", len(todo), flush=True)

rows, fails, nfile = [], [], 0
for i, src in enumerate(todo):
    rel = os.path.relpath(src, SRC)
    base = os.path.splitext(os.path.splitext(rel)[0])[0]
    outdir = os.path.join(DST, os.path.dirname(base), os.path.basename(base) + '_textures')
    try:
        texs, off, sz = thug2tex.parse(src)
    except Exception as e:
        fails.append((rel, 'parse: %s' % e)); continue
    if off != sz:
        fails.append((rel, 'trailing bytes %d/%d' % (off, sz)))
    for j, t in enumerate(texs):
        try:
            im = thug2tex.to_image(t)
            if im.getchannel('A').getextrema() == (255, 255):
                im = im.convert('RGB')
            os.makedirs(outdir, exist_ok=True)
            name = '%04d_%08x.png' % (j, t['checksum'])
            im.save(os.path.join(outdir, name), optimize=True)
            rows.append((rel, j, '%08x' % t['checksum'], t['width'], t['height'], t['dxt']))
            nfile += 1
        except Exception as e:
            fails.append(('%s[%d]' % (rel, j), str(e)))
    if (i + 1) % 100 == 0:
        print(' ', i + 1, '/', len(todo), '->', nfile, 'pngs', flush=True)

with open(os.path.join(DST, '_manifest_textures.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['tex_file', 'index', 'checksum', 'width', 'height', 'dxt_type'])
    w.writerows(rows)
print("extracted:", nfile, " problems:", len(fails))
for f in fails[:25]: print("  ", f)
