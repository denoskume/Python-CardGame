# ALPRO V1 — academic report and presentation notes

## Source identification

- Project: **Rouge Gagne, Noir Perd**
- Program: MSc Control and Robotics, Data Science, Signal and Image Processing, **Master 1 Semester 1**
- Course: **Algorithmics and Programming (ALPRO)**, taught in Python
- Authors: **Denos KUME and Sena FUKABE**
- Instructor: **Mira Rizkallah**
- Report dated: **12 December 2025** (PDF generation timestamp: 19 December 2025)
- Presentation: **20 slides**, 12 December 2025
- The original student submission supplied for this update included a 22-page PDF report, PowerPoint presentation and the five Python modules saved in `original-code.zip`.

## Problem and objective

Create a small, maintainable interactive system in which a player chooses a stake, follows one red card during a shuffle, and selects the card before the timer expires. Connect programming concepts to a working Pygame interface and a documented software-development lifecycle. The academic goal was to validate the ALPRO course through a collaborative implemented project and presentation.

## Requirements and implementation

The source modules are `main.py`, `user.py`, `bet.py`, `game.py` and `dashboard.py`. V1 uses classes for the player, bet and cards, with a `CardGame` controller for states and transitions. The interface includes a start menu, stake configuration, observation, shuffle, selection and a result/dashboard view. JSON stores round history locally. Main timed game phases are 10 seconds each. The design prioritizes responsive event handling and separation of game logic from presentation.

## Report figures and diagrams

The academic submission contains figures for:

1. **UML class diagram** showing the class-level architecture.
2. **ER diagram** for the player and round records.
3. **SDLC Gantt chart** for design, implementation, testing and documentation. See the [original 2025 Gantt diagram](figures/sdlc-gantt.webp) extracted from the submitted report.
4. **Sequence diagram** of an end-to-end game round.
5. **V1 screenshots** for the menu, betting dashboard, observation, shuffle, selection and results.

The figures are discussed in the portfolio report; see the supplied report for the original full-resolution diagrams.

## Testing and findings

The submission documents functional and non-functional testing, including input validation, valid/invalid bets, round progression, timing, game result consistency, resilience of JSON history and performance concerns around approximately 60 FPS. It describes a working modular Pygame game and a classroom presentation. It **does not report V2's later browser tests or measured rendering benchmarks**, which must remain clearly attributed to V2.

## Development timeline and risks

The presentation states the project was planned and delivered between **October and December 2025**. The report divides work into design, implementation, testing and documentation, and identifies invalid input, lag, JSON corruption and state inconsistencies as key risks. Mitigations include validation, guarded state transitions, separation of modules and defensive persistence.

## V2 relationship

The V2 release remains unchanged at repository root. It adds later improvements, automated checks and a playable web build. Do not treat its performance metrics or web features as results achieved in the original S1 submission.

### References

- Original student project report: *Rouge Gagne, Noir Perd*, ALPRO, December 2025, 22 pages (user-provided archive)
- Original student presentation: *Rouge Gagne, Noir Perd*, ALPRO, December 2025, 20 slides (user-provided archive)
- [Python documentation](https://docs.python.org/)
- [Pygame documentation](https://www.pygame.org/docs/)
