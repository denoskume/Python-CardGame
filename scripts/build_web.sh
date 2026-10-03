#!/usr/bin/env bash
set -euo pipefail

WEB_SRC=".web-src"

rm -rf "$WEB_SRC" src/build/web
cp -R src "$WEB_SRC"
rm -rf "$WEB_SRC/build"

for sound in shuffle win lose; do
  ffmpeg -y -loglevel error \
    -i "src/assets/${sound}.mp3" \
    -c:a libvorbis "$WEB_SRC/assets/${sound}.ogg"
done

rm -f "$WEB_SRC/assets/"*.mp3
sed -i 's/\.mp3"/\.ogg"/g' "$WEB_SRC/game.py"

python -m pygbag --build --no_opt "$WEB_SRC"

mkdir -p src/build
cp -R "$WEB_SRC/build/web" src/build/web
python scripts/patch_web_shell.py src/build/web/index.html

test -f src/build/web/index.html
grep -q 'full-viewport-shell' src/build/web/index.html
grep -q 'window.innerWidth' src/build/web/index.html
grep -q 'window.innerHeight' src/build/web/index.html
printf 'Web build ready with OGG audio and full viewport shell: %s\n' "src/build/web"
