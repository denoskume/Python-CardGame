# Rouge Gagne, Noir Perd — CardGame V1 (ALPRO)

**Master 1 · Semester 1 · Control and Robotics (CORO DASSIP), Centrale Nantes**  
**Course:** Algorithmics and Programming (ALPRO), Python · Academic year 2025–2026  
**Developed by:** Denos KUME and Sena FUKABE · **Instructor:** Mira Rizkallah  
**Course presentation:** 12 December 2025

This folder preserves the academic **V1** of *Rouge Gagne, Noir Perd*, the game built and presented for the ALPRO course, separately from the later V2 application stored at the repository root under `src/`.

## What V1 does

The player identifies a red card among three, watches the shuffle, and chooses its position before the timer expires. The program covers an event-driven Pygame interface, object-oriented domain models, an explicit round state machine, fictitious betting credits, a local history file, and a summary dashboard.

- `code/main.py` — entry point and event/update/render loop
- `code/user.py` — player model and balance
- `code/bet.py` — stake rules and turbo multiplier
- `code/game.py` — state transitions, card shuffle and game logic
- `code/dashboard.py` — visual interface and game dashboards
- `code/assets/` — original V1 sprites and sounds (binary-identical to the files preserved with V2)
- `original-code.zip` — exact five Python source files supplied from the 2025 V1 archive, retained as a source-of-truth backup

The source ZIP is verified by SHA-256: `8dddd09fb16537763d3a9a3b98babf6fb8b357359eaf72794908a6712230dba3`. GitHub Actions restores the five source files into `code/` and checks that each is valid Python before committing. **V2 files are not changed.**

## Run V1

Use Python 3.12 or a supported Python 3 version with Pygame.

```bash
python -m pip install pygame
cd versions/v1/code
python main.py
```

The game creates a local `history.json` as rounds are played; a real player-history file was excluded from this public repository to avoid publishing player data.

## Academic documentation

The V1 academic report (22 pages) covers requirements, UML class diagram, ER diagram, SDLC Gantt chart, sequence diagram, UI screenshots, implementation, test plan, limitations and perspectives. The course presentation contains 20 slides, including the project architecture and a complete-round sequence diagram. Their content and findings are summarized in `docs/academic-report.md` without attributing later V2 tests or benchmarks to V1.

The original V1 animated gameplay demonstration is already available at [docs/cardgame_demo.gif](../../../docs/cardgame_demo.gif).

The [original SDLC Gantt figure](docs/figures/sdlc-gantt.webp) is preserved from the 2025 report, showing the October–December planning, development, testing and documentation sequence.

**V1 and V2 are distinct.** V1 documents the ALPRO academic work of 2025; V2 extends and modernizes the application with browser support and later tests. The [portfolio project page](https://denoskume.github.io/portfolio/#/projects/python-cardgame) explains both versions.
