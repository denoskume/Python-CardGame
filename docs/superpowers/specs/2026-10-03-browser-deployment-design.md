# Python CardGame Browser Deployment Design

## Goal

Make the existing Python CardGame playable from a public browser URL at `https://denoskume.github.io/Python-CardGame/` without requiring Python installation, while preserving the current desktop version.

## Current State

The project is a desktop Pygame application launched from `src/main.py`. It uses a continuous 60 FPS event/update/render loop, local assets under `src/assets/`, optional audio through `pygame.mixer`, and bounded round history persisted to `data/history.json`.

## Proposed Architecture

Use Pygbag to package the existing Pygame application for WebAssembly/browser execution and GitHub Pages for free static hosting.

The browser build will keep the existing game domain model and rendering modules. The main compatibility change will be at the application entry loop so the browser runtime can yield control each frame while the desktop version remains runnable.

The browser deployment flow will be:

```text
Python/Pygame source
        ↓
Pygbag browser build
        ↓
Static web bundle
        ↓
GitHub Actions
        ↓
GitHub Pages
```

## Runtime Compatibility

### Main Loop

`src/main.py` will expose an async game loop compatible with Pygbag. Each frame will continue to process events, update game state, render, flip the display, and cap frame rate, but will also yield to the browser event loop with `await asyncio.sleep(0)`.

Desktop execution must remain supported through `asyncio.run(main())`.

### Assets

Existing image and audio assets remain under `src/assets/`. Paths already derive from `__file__`, so the browser package must include the complete `src/assets/` directory.

Missing or unsupported optional audio must continue to degrade gracefully without preventing gameplay.

### Persistence

Desktop JSON history remains unchanged. Browser file-system persistence is not guaranteed by the current architecture, so the browser version may treat round history as session-local when durable writes are unavailable. Failure to read or write `data/history.json` must never stop gameplay.

No new database or cloud persistence layer will be introduced for this deployment.

## Build and Deployment

Add a GitHub Actions workflow dedicated to the browser build and GitHub Pages deployment.

The workflow will:

1. check out the repository;
2. install a supported Python version;
3. install Pygbag;
4. build the browser package from the game source;
5. upload the generated static bundle as the GitHub Pages artifact;
6. deploy on pushes to `main` and allow manual dispatch.

The deployment must not modify or remove the existing desktop installation path.

## Repository Documentation

Update the README with:

- a prominent `Play Live` link;
- a short browser-play section;
- the existing desktop installation/run instructions retained;
- a note that local JSON history is best-effort in the browser environment.

## Verification

Before deployment is considered complete:

- the desktop entry point must still launch successfully;
- the browser build must complete without packaging errors;
- the generated site must load from the repository GitHub Pages path;
- the start screen, profile setup, betting screen, shuffle, selection, result, pause/resume, and game-over flow must remain usable;
- image assets must render;
- lack of browser audio support must not break the game;
- file-history failures must not break the game.

## Non-Goals

This change will not add multiplayer, authentication, cloud saves, real-money features, mobile-native packaging, or a new frontend framework. It is a browser delivery adaptation of the existing Pygame application.
