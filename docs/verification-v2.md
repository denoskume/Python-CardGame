# CardGame V2 verification

Validated on 4 October 2026 from the `feat/cardgame-v2` branch.

## Automated checks

- `python -m unittest discover -s tests -v` — all tests pass.
- `python -m compileall -q src` — Python sources compile successfully.
- `git diff --check` — no whitespace errors.
- `bash scripts/build_web.sh` — Pygbag bundle generated in `src/build/web`.

## Runtime checks

- Desktop smoke run with dummy SDL video/audio completed without exceptions.
- Chromium browser flow completed with the Pygbag bundle: accented profile name, profile persistence, betting, round start, pause/resume, card selection, history persistence, returning profile, and mobile viewport rendering.
- Responsive captures were checked at 360×640, 390×844, 844×390, 960×630, and 1440×900.
- 300-frame desktop render benchmark: median ~0.59 ms/frame, p95 ~0.95 ms/frame in the validation environment.

## Scope and limits

The same controller and persistence paths are exercised by the desktop and browser builds. Browser validation used Chromium automation; a physical iOS/Android device was not available in this environment. Audio playback depends on the browser's user-gesture policy, and the browser console may report the platform's `ScriptProcessorNode` deprecation warning while the game remains playable.
