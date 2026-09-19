import os, json, html, csv
from PIL import Image

D = "/sessions/modest-hopeful-ritchie/mnt/Games/THUG2-Assets"
IDX = os.path.join(D, "_index")
THUMBS = os.path.join(IDX, "thumbs")
os.makedirs(THUMBS, exist_ok=True)
meta = json.load(open(os.path.join(IDX, "sheets.json")))

# --- big thumbs for loading screens + movie posters ---
def thumbs_for(rel, width=340):
    src = os.path.join(D, rel)
    out = []
    for f in sorted(os.listdir(src)):
        if not f.lower().endswith('.png'):
            continue
        tn = (rel.replace(os.sep, '__') + '__' + f).rsplit('.', 1)[0] + '.jpg'
        p = os.path.join(THUMBS, tn)
        if not os.path.exists(p):
            im = Image.open(os.path.join(src, f)).convert('RGB')
            im.thumbnail((width, width), Image.LANCZOS)
            im.save(p, quality=85, optimize=True)
        out.append((f, tn))
    return out

ls_en = thumbs_for('loading-screens/english-640x448')
ls_fr = thumbs_for('loading-screens/french-512x512')
ls_gr = thumbs_for('loading-screens/german-512x512')

movie_posters = {}
fr_dir = os.path.join(D, 'movies/frames')
if os.path.isdir(fr_dir):
    for f in sorted(os.listdir(fr_dir)):
        if f.endswith('_40.png'):
            base = f[:-7]
            tn = 'movie__' + base + '.jpg'
            p = os.path.join(THUMBS, tn)
            if not os.path.exists(p):
                im = Image.open(os.path.join(fr_dir, f)).convert('RGB')
                im.thumbnail((320, 320), Image.LANCZOS); im.save(p, quality=85, optimize=True)
            movie_posters[base] = tn

total_png = sum(v['count'] for v in meta.values())

def esc(s): return html.escape(str(s))

def gallery(items, rel):
    return '\n'.join(
        '<a class="card" href="%s/%s"><img loading="lazy" src="_index/thumbs/%s"><span>%s</span></a>'
        % (esc(rel), esc(f), esc(tn), esc(f.rsplit('.', 1)[0]))
        for f, tn in items)

# group contact sheets under top-level headings
tops = {}
for rel in sorted(meta):
    top = rel.split(os.sep)[0]
    tops.setdefault(top, []).append(rel)

LABELS = {
    'images': 'UI, sprites, menus, tags & create-a-skater art',
    'textures': 'Boards, cars, logos, skater & scuff textures',
    'fonts': 'In-game font sheets',
    'levels': 'Level environment textures (from .tex.xbx dictionaries)',
    'models': 'Character, ped, cutscene & prop textures',
    'movies': 'Bink video stills',
    'loading-screens': 'Loading screens',
    'extras': 'Cover art, icons, manual',
}

sections = []
for top in sorted(tops):
    if top in ('loading-screens', '_index'):
        continue
    blocks = []
    for rel in tops[top]:
        sheets = ''.join('<a href="_index/sheets/%s"><img loading="lazy" class="sheet" src="_index/sheets/%s"></a>'
                         % (esc(s), esc(s)) for s in meta[rel]['sheets'])
        blocks.append('<details><summary><b>%s</b> <em>%d images</em></summary><div class="sheets">%s</div>'
                      '<p class="path">folder: <code>%s</code></p></details>'
                      % (esc(rel), meta[rel]['count'], sheets, esc(rel)))
    n = sum(meta[r]['count'] for r in tops[top])
    sections.append('<section><h2>%s <span class="n">%d images</span></h2><p class="sub">%s</p>%s</section>'
                    % (esc(top), n, esc(LABELS.get(top, '')), '\n'.join(blocks)))

movies_html = '\n'.join(
    '<a class="card" href="movies/mp4/%s.mp4"><img loading="lazy" src="_index/thumbs/%s"><span>%s</span></a>'
    % (esc(b), esc(tn), esc(b)) for b, tn in sorted(movie_posters.items()))

doc = """<!doctype html><meta charset="utf-8"><title>THUG2 asset archive</title>
<style>
:root{color-scheme:dark}
body{background:#14161a;color:#e8e8ea;font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:28px 34px 80px}
h1{font-size:30px;margin:0 0 4px;letter-spacing:-.02em}
.lede{color:#9aa0a8;margin:0 0 26px}
.stats{display:flex;gap:26px;flex-wrap:wrap;margin:0 0 34px;padding:16px 20px;background:#1c1f25;border-radius:10px}
.stats div b{display:block;font-size:24px}
.stats div span{color:#9aa0a8;font-size:13px}
h2{font-size:20px;margin:36px 0 2px;border-bottom:1px solid #2a2e36;padding-bottom:8px}
h2 .n{float:right;color:#8a9098;font-weight:400;font-size:13px}
.sub{color:#8a9098;margin:6px 0 14px;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:12px}
.card{display:block;background:#1c1f25;border-radius:8px;overflow:hidden;text-decoration:none;color:#c9ced6;border:1px solid #262a32}
.card:hover{border-color:#5b8def}
.card img{display:block;width:100%;height:auto;background:#0d0f12}
.card span{display:block;padding:7px 9px;font-size:12px;word-break:break-all}
details{background:#1a1d22;border:1px solid #262a32;border-radius:8px;margin:8px 0;padding:10px 14px}
summary{cursor:pointer}summary em{color:#8a9098;font-style:normal;font-size:12px;margin-left:8px}
.sheets{margin-top:10px}
.sheet{max-width:100%;border-radius:6px;margin:6px 0;image-rendering:auto}
.path{color:#7d838b;font-size:12px}
code{background:#23272e;padding:1px 5px;border-radius:4px}
</style>
<h1>Tony Hawk's Underground 2 &mdash; asset archive</h1>
<p class="lede">Everything decoded out of the installed game: Neversoft <code>.img.xbx</code> images, <code>.tex.xbx</code> texture dictionaries, and Bink video. All images are PNG with alpha preserved.</p>
<div class="stats">
  <div><b>__TOTPNG__</b><span>PNG images</span></div>
  <div><b>__LS__</b><span>loading screens</span></div>
  <div><b>__MOV__</b><span>videos (MP4)</span></div>
  <div><b>__GRP__</b><span>asset folders</span></div>
</div>

<section><h2>Loading screens &mdash; English <span class="n">640&times;448 &middot; __NEN__ files</span></h2>
<p class="sub">The main set. Click any thumbnail for the full-resolution PNG.</p>
<div class="grid">__GEN__</div></section>

<section><h2>Loading screens &mdash; French <span class="n">512&times;512 &middot; __NFR__ files</span></h2>
<p class="sub">Localised variants. Different 512&times;512 composition &mdash; often busier artwork than the English set.</p>
<div class="grid">__GFR__</div></section>

<section><h2>Loading screens &mdash; German <span class="n">512&times;512 &middot; __NGR__ files</span></h2>
<div class="grid">__GGR__</div></section>

<section><h2>Videos <span class="n">__MOV__ files</span></h2>
<p class="sub">Intro, credits, pro bails and sponsor bumpers, converted to H.264 MP4. Four stills per video are in <code>movies/frames/</code>.</p>
<div class="grid">__GMOV__</div></section>

__SECTIONS__
"""
doc = (doc.replace('__TOTPNG__', '{:,}'.format(total_png))
          .replace('__LS__', str(len(ls_en) + len(ls_fr) + len(ls_gr)))
          .replace('__MOV__', str(len(movie_posters)))
          .replace('__GRP__', '{:,}'.format(len(meta)))
          .replace('__NEN__', str(len(ls_en))).replace('__NFR__', str(len(ls_fr))).replace('__NGR__', str(len(ls_gr)))
          .replace('__GEN__', gallery(ls_en, 'loading-screens/english-640x448'))
          .replace('__GFR__', gallery(ls_fr, 'loading-screens/french-512x512'))
          .replace('__GGR__', gallery(ls_gr, 'loading-screens/german-512x512'))
          .replace('__GMOV__', movies_html)
          .replace('__SECTIONS__', '\n'.join(sections)))

open(os.path.join(D, 'INDEX.html'), 'w').write(doc)
print('INDEX.html written;', total_png, 'pngs,', len(meta), 'groups,', len(movie_posters), 'movies')
