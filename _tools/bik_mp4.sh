#!/bin/bash
SRC="/sessions/modest-hopeful-ritchie/mnt/Games/thug2/drive_c/Program Files (x86)/Activision/Tony Hawk's Underground 2/Game/Data/movies/bik"
DST="/sessions/modest-hopeful-ritchie/mnt/Games/THUG2-Assets/movies/mp4"
DEADLINE=$(( $(date +%s) + ${1:-480} ))
mkdir -p "$DST"
for f in "$SRC"/*.bik; do
  b=$(basename "$f" .bik)
  [ -s "$DST/$b.mp4" ] && continue
  [ $(date +%s) -ge $DEADLINE ] && { echo "budget reached"; break; }
  ffmpeg -nostdin -v error -y -i "$f" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
         -c:a aac -b:a 128k -movflags +faststart "$DST/$b.mp4" </dev/null || echo "FAIL $b"
  echo "done $b"
done
echo "mp4 total: $(ls "$DST" | wc -l)/24"
