#!/usr/bin/env bash
set -euo pipefail

rm -rf src/build/web
python -m pygbag --build --no_opt src

test -f src/build/web/index.html
printf 'Web build ready: %s\n' "src/build/web"
