#!/bin/bash
SRC="/sessions/modest-hopeful-ritchie/mnt/Games/thug2/drive_c/Program Files (x86)/Activision/Tony Hawk's Underground 2/Game/Data/movies/bik"
DST="/sessions/modest-hopeful-ritchie/mnt/Games/THUG2-Assets/movies/frames"
mkdir -p "$DST"
one() {
  f="$1"; b=$(basename "$f" .bik)
  [ -s "$DST/${b}_90.png" ] && return 0
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  for pct in 15 40 65 90; do
    t=$(awk -v d="${d:-1}" -v p="$pct" 'BEGIN{printf "%.3f", d*p/100}')
    ffmpeg -nostdin -v error -y -ss "$t" -i "$f" -frames:v 1 "$DST/${b}_${pct}.png" </dev/null 2>/dev/null
  done
}
export -f one; export DST
find "$SRC" -name '*.bik' -print0 | xargs -0 -P 2 -I{} bash -c 'one "$@"' _ {}
echo "frames: $(ls "$DST" | wc -l)"
