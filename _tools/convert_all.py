import os, sys, csv, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thug2img

SRC = "/sessions/modest-hopeful-ritchie/mnt/Games/thug2/drive_c/Program Files (x86)/Activision/Tony Hawk's Underground 2/Game/Data"
DST = "/sessions/modest-hopeful-ritchie/mnt/Games/THUG2-Assets"

rows, fails = [], []
todo = []
for root, dirs, files in os.walk(SRC):
    for f in files:
        if f.endswith('.img.xbx'):
            todo.append(os.path.join(root, f))
todo.sort()
print("found", len(todo), "img.xbx files", flush=True)

for i, src in enumerate(todo):
    rel = os.path.relpath(src, SRC)
    out = os.path.join(DST, os.path.splitext(os.path.splitext(rel)[0])[0] + '.png')
    try:
        im = thug2img.decode(src)
        # drop a fully-opaque alpha channel to save space
        if im.getchannel('A').getextrema() == (255, 255):
            im = im.convert('RGB')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        im.save(out, optimize=True)
        rows.append((rel, im.width, im.height, im.mode, os.path.getsize(out)))
    except Exception as e:
        fails.append((rel, '%s: %s' % (type(e).__name__, e)))
    if (i + 1) % 400 == 0:
        print(' ', i + 1, '/', len(todo), flush=True)

os.makedirs(DST, exist_ok=True)
with open(os.path.join(DST, '_manifest_images.csv'), 'w', newline='') as fh:
    wtr = csv.writer(fh)
    wtr.writerow(['source_rel', 'width', 'height', 'mode', 'png_bytes'])
    wtr.writerows(rows)

print("OK:", len(rows), " FAILED:", len(fails))
for r in fails[:40]:
    print("  FAIL", r)
