#!/usr/bin/env bash
set -euo pipefail

rm -rf src/build/web
python -m pygbag --build --disable-sound-format-error src

test -f src/build/web/index.html
printf 'Web build ready: %s\n' "src/build/web"
