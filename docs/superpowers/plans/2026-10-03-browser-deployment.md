# Python CardGame Browser Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing Python CardGame playable in a browser through Pygbag and GitHub Pages while preserving the desktop version.

**Architecture:** Keep the existing Pygame modules and game logic intact. Adapt only the application entry loop for async browser execution, package the current source/assets with Pygbag, and deploy the generated static bundle through GitHub Actions to GitHub Pages.

**Tech Stack:** Python, Pygame, asyncio, Pygbag/WebAssembly, GitHub Actions, GitHub Pages

**Spec:** `docs/superpowers/specs/2026-10-03-browser-deployment-design.md`

## Global Constraints

- Preserve the current desktop game behavior and entry point.
- Browser URL target: `https://denoskume.github.io/Python-CardGame/`.
- Keep existing game logic, modules, player flow, betting rules, and assets unchanged unless browser compatibility requires it.
- Browser audio failure must not stop gameplay.
- Browser history-file read/write failure must not stop gameplay.
- Do not add cloud persistence, authentication, multiplayer, or a frontend rewrite.

## Review Focus

- Browser runtime cannot block on the Pygame loop; verify each frame yields to asyncio.
- Asset paths must still resolve when packaged from the browser entry directory.
- Mixer/audio initialization may fail in-browser; verify the existing graceful fallback remains effective.
- `data/history.json` writes may be unavailable or non-durable in WebAssembly; verify failures are non-fatal.
- GitHub Pages serves from `/Python-CardGame/`; verify the generated bundle uses paths that work under the repository subpath.

---

### Task 1: Make the Pygame Entry Loop Browser-Compatible

**Files:**
- Modify: `src/main.py`
- Create: `tests/test_main_entry.py`

**Interfaces:**
- Consumes: existing `User`, `Bet`, `CardGame`, and Pygame initialization flow.
- Produces: `async def main() -> None`, invoked by `asyncio.run(main())` for desktop and compatible with Pygbag in-browser execution.

- [ ] **Step 1: Write a failing source-level test for the async entry contract**

Create `tests/test_main_entry.py` that parses `src/main.py` with `ast` and asserts that `main` is an `AsyncFunctionDef`, that the module imports `asyncio`, that `main` contains an `await asyncio.sleep(0)` expression, and that the `__main__` guard calls `asyncio.run(main())`.

- [ ] **Step 2: Run the test and verify it fails**

Run: `python -m unittest tests.test_main_entry -v`

Expected: FAIL because the current `main` is synchronous and does not yield to asyncio.

- [ ] **Step 3: Implement the minimal browser-compatible entry loop**

Modify `src/main.py` to import `asyncio`, change `main` to `async def main() -> None`, add `await asyncio.sleep(0)` once per rendered frame after frame pacing, and replace the direct `main()` call in the `__main__` guard with `asyncio.run(main())`.

Do not change game rules, state transitions, initial balance, betting limits, rendering calls, or desktop audio setup beyond what async compatibility requires.

- [ ] **Step 4: Run the entry-contract test**

Run: `python -m unittest tests.test_main_entry -v`

Expected: PASS.

- [ ] **Step 5: Run a syntax/import check**

Run: `python -m py_compile src/main.py src/game.py src/dashboard.py src/user.py src/bet.py`

Expected: command exits with status 0.

- [ ] **Step 6: Commit**

```bash
git add src/main.py tests/test_main_entry.py
git commit -m "feat: make card game loop browser compatible"
```

### Task 2: Add a Reproducible Pygbag Browser Build

**Files:**
- Modify: `requirements.txt`
- Create: `scripts/build_web.sh`
- Create: `tests/test_web_build_config.py`

**Interfaces:**
- Consumes: browser-compatible `src/main.py` from Task 1 and existing `src/assets/`.
- Produces: a reproducible command that builds static browser output with Pygbag without changing the desktop source layout.

- [ ] **Step 1: Write a failing configuration test**

Create `tests/test_web_build_config.py` asserting that `requirements.txt` declares `pygbag`, `scripts/build_web.sh` exists, the script invokes Pygbag against the directory containing the browser entry file, and the script exits on build errors.

- [ ] **Step 2: Run the test and verify it fails**

Run: `python -m unittest tests.test_web_build_config -v`

Expected: FAIL because Pygbag and the build script are not yet configured.

- [ ] **Step 3: Add Pygbag as a project build dependency**

Update `requirements.txt` so the existing `pygame>=2.5,<3.0` desktop dependency remains and Pygbag is explicitly listed for the browser build.

- [ ] **Step 4: Add `scripts/build_web.sh`**

The script must use strict shell mode, run Pygbag from the correct project/source directory, build non-interactively for CI, and leave the generated static output in a deterministic location that the Pages workflow can upload.

- [ ] **Step 5: Run the configuration test**

Run: `python -m unittest tests.test_web_build_config -v`

Expected: PASS.

- [ ] **Step 6: Install dependencies and run the browser build locally/in CI environment**

Run:

```bash
python -m pip install -r requirements.txt
bash scripts/build_web.sh
```

Expected: Pygbag completes successfully and generated static web files exist.

- [ ] **Step 7: Verify packaged assets**

Confirm the generated package contains the card images, avatars, logo cards, and optional sound assets from `src/assets/`.

- [ ] **Step 8: Commit**

```bash
git add requirements.txt scripts/build_web.sh tests/test_web_build_config.py
git commit -m "build: add pygbag web package"
```

### Task 3: Automate GitHub Pages Deployment

**Files:**
- Create: `.github/workflows/deploy-web.yml`
- Create: `tests/test_pages_workflow.py`

**Interfaces:**
- Consumes: deterministic browser build from Task 2.
- Produces: GitHub Pages artifact and deployment from `main`, plus manual `workflow_dispatch` support.

- [ ] **Step 1: Write a failing workflow-structure test**

Create `tests/test_pages_workflow.py` that reads `.github/workflows/deploy-web.yml` and asserts it contains push-to-main and manual triggers, Pages write/id-token permissions, Python setup, dependency installation, `scripts/build_web.sh`, Pages artifact upload, and Pages deployment.

- [ ] **Step 2: Run the test and verify it fails**

Run: `python -m unittest tests.test_pages_workflow -v`

Expected: FAIL because the workflow does not yet exist.

- [ ] **Step 3: Create the GitHub Pages workflow**

Create `.github/workflows/deploy-web.yml` using official checkout, setup-python, configure-pages, upload-pages-artifact, and deploy-pages actions. Run the browser build before artifact upload. Deploy only from `main`; allow workflow dispatch for manual verification.

- [ ] **Step 4: Run the workflow-structure test**

Run: `python -m unittest tests.test_pages_workflow -v`

Expected: PASS.

- [ ] **Step 5: Run all repository web-port tests**

Run: `python -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/deploy-web.yml tests/test_pages_workflow.py
git commit -m "ci: deploy card game to github pages"
```

### Task 4: Document the Live Browser Version

**Files:**
- Modify: `README.md`
- Create: `tests/test_readme_live_link.py`

**Interfaces:**
- Consumes: deployed GitHub Pages URL from Task 3.
- Produces: recruiter-facing `Play Live` documentation while retaining existing desktop instructions.

- [ ] **Step 1: Write a failing README test**

Create `tests/test_readme_live_link.py` asserting that `README.md` contains `https://denoskume.github.io/Python-CardGame/`, a visible `Play Live` label, the existing desktop `python src/main.py` command, and a short note that browser history persistence is best-effort/session-dependent.

- [ ] **Step 2: Run the test and verify it fails**

Run: `python -m unittest tests.test_readme_live_link -v`

Expected: FAIL because the live-play documentation is absent.

- [ ] **Step 3: Update the README**

Add a prominent `Play Live` link near the project introduction and a concise browser section. Retain the existing desktop installation/run documentation and explain the browser history limitation without implying that gameplay is incomplete.

- [ ] **Step 4: Run the README test**

Run: `python -m unittest tests.test_readme_live_link -v`

Expected: PASS.

- [ ] **Step 5: Run the full verification suite**

Run:

```bash
python -m unittest discover -s tests -v
python -m py_compile src/main.py src/game.py src/dashboard.py src/user.py src/bet.py
bash scripts/build_web.sh
```

Expected: all tests pass, Python compilation succeeds, and the browser bundle builds successfully.

- [ ] **Step 6: Commit**

```bash
git add README.md tests/test_readme_live_link.py
git commit -m "docs: add live browser game link"
```

### Task 5: Verify the Published Game End-to-End

**Files:**
- No source changes unless verification exposes a browser-specific defect.

**Interfaces:**
- Consumes: GitHub Pages deployment from Task 3 and documentation from Task 4.
- Produces: verified public browser experience at the target URL.

- [ ] **Step 1: Confirm the GitHub Actions deployment run succeeds**

Expected: build and deploy jobs complete successfully for `main`.

- [ ] **Step 2: Open the public Pages URL**

Open: `https://denoskume.github.io/Python-CardGame/`

Expected: the Pygbag game canvas loads rather than a repository 404 or blank page.

- [ ] **Step 3: Exercise the complete playable flow**

Verify: start screen → profile nickname/avatar → betting → observation → shuffle → selection → result → next round; also verify pause/resume and game-over behavior.

- [ ] **Step 4: Verify graceful browser limitations**

Confirm image assets render, optional audio failure does not stop the game, and unavailable/non-durable JSON persistence does not stop a new or completed round.

- [ ] **Step 5: Final repository status check**

Confirm README live link matches the working Pages URL and no generated build directory or runtime `data/history.json` was accidentally committed.
