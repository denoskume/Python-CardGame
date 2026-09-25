<table width="100%">
  <tr>
    <td align="left" width="50%">
      <img src="https://www.ec-nantes.fr/medias/photo/logocn-rvb_1648479844750-png?ID_FICHE=178994&amp;INLINE=FALSE" alt="Centrale Nantes" height="72">
    </td>
    <td align="right" width="50%">
      <strong>MSc. CORO DASSIP</strong>
    </td>
  </tr>
</table>

<table width="85%" align="center">
  <tr>
    <td align="center">
      <h1>CardGame</h1>
    </td>
  </tr>
</table>

<p align="center"><strong>Rouge Gagne, Noir Perd</strong></p>

Interactive card-tracking and betting game developed in Python with Pygame.

The player observes one red card and two black cards, follows the red card through an animated shuffle, and must identify its final position before the selection timer expires.

![CardGame Live Demo](docs/cardgame_demo.gif)

---

## Context

The project combines a simple visual-memory game with a complete event-driven application architecture. The technical objective is not only to display moving cards, but to coordinate player state, betting rules, timed phases, animations, audio feedback, persistent history, and user-interface rendering without blocking the main Pygame loop.

The implementation is organized as independent Python modules rather than notebooks. Documentation for the **problem statement**, **requirements and approach**, and **theoretical foundations** is therefore consolidated in this README, while executable behavior remains in `src/*.py`.

---

## Problem Statement

Design and implement an interactive three-card tracking game in which one red card must remain logically identifiable while card positions change through animated random swaps.

The application must:

- create and validate a player profile;
- maintain an independent player balance;
- enforce configurable betting limits and turbo multipliers;
- display one red and two black cards before every round;
- hide card identity during shuffling while preserving each card's logical identity;
- animate random pairwise card swaps without blocking the event loop;
- enforce timed observation, shuffle, and selection phases;
- resolve a round as win, loss, or timeout;
- update the player's balance from the effective stake;
- stop play when the remaining balance is below the minimum bet;
- support pause/resume behavior;
- render all screens and game states consistently;
- persist recent round history to JSON;
- continue operating when optional audio playback is unavailable.

### Inputs and Fixed Parameters

| Item | Current value |
| --- | ---: |
| Window size | 960 × 630 px |
| Target frame rate | 60 FPS |
| Cards per round | 3 |
| Red cards | 1 |
| Black cards | 2 |
| Initial balance | $30 |
| Minimum bet | $10 |
| Maximum bet | $100 |
| Bet increment | $5 |
| Turbo multipliers | ×1, ×2, ×3 |
| Observation time | 10 s |
| Shuffle time | 10 s |
| Selection time | 10 s |
| Swap interval | 300 ms |
| Swap animation duration | 300 ms |
| Persisted history limit | 200 rounds |
| Runtime history file | `data/history.json` |

### Completion Criterion

The project is complete when the game can progress from player setup through repeated betting rounds without blocking the main event loop, every round produces a deterministic state transition and balance update, invalid or timed-out selections are handled explicitly, persistent history is maintained, and the application remains usable when optional media resources are unavailable.

---

## Requirements and Approach

The software is designed around explicit separation of responsibilities: domain state is kept outside the rendering layer, the game controller owns transitions and timing, and the main loop only coordinates events, updates, rendering, and frame pacing.

### Global Requirements

| Requirement | Implemented approach |
| --- | --- |
| Application loop | Pygame event → update → render loop at 60 FPS |
| Game lifecycle | explicit finite-state machine |
| Player state | dedicated `User` object |
| Betting state | dedicated `Bet` object |
| Core controller | `CardGame` |
| Rendering | isolated in `dashboard.py` |
| Shuffle motion | non-blocking interpolation between card slots |
| Timing | `pygame.time.get_ticks()` |
| Persistence | bounded JSON history |
| Audio | optional Pygame mixer with graceful fallback |
| Runtime data | stored outside source code |
| Platform support | standard desktop Pygame; WSLg audio handled when available |

### Functional Requirements

#### Player and Session

**Approach:** collect a nickname and avatar selection before entering the betting workflow. Store identity and balance in a `User` instance.

**Acceptance:** a valid player can enter the game, preserve identity during the session, and reset to the configured initial balance when the game is restarted.

#### Betting

**Approach:** manage minimum/maximum bet, $5 increments, and turbo multiplier independently in `Bet`.

The nominal stake is

```text
stake = bet × turbo
```

and the resolved stake is capped by the available balance.

**Acceptance:** the base bet remains inside configured limits, the turbo multiplier remains in `{1,2,3}`, and a round cannot start from an invalid betting configuration.

#### Round Initialization

**Approach:** create three card objects at fixed screen slots, randomly assign exactly one red identity, and start the observation timer.

**Acceptance:** every round contains exactly three cards and exactly one card has `is_red=True`.

#### Timed Game Phases

**Approach:** represent observation, shuffling, and selection as separate states driven by elapsed time rather than blocking delays.

**Acceptance:** the game advances automatically after 10 seconds of observation, after 10 seconds of shuffling, and resolves a timeout loss after 10 seconds without a card selection.

#### Shuffle Animation

**Approach:** randomly select two card indices and interpolate their rectangles over 300 ms while card identity remains attached to the card object.

**Acceptance:** the visible positions change continuously while the logical red/black identity is never reassigned during the shuffle.

#### Round Resolution

**Approach:** reveal the result, compute the effective stake, update the balance, record the round, and transition to either `RESULT` or `GAME_OVER`.

**Acceptance:** red-card selection produces a win, black-card selection or timeout produces a loss, balance never becomes negative, and the game ends when the balance falls below the minimum bet.

#### Persistence

**Approach:** append one structured record per completed round to `data/history.json` and retain only the 200 most recent entries.

**Acceptance:** valid history survives application restarts and malformed/missing history falls back safely to an empty list.

#### Rendering and Media

**Approach:** delegate visual rendering to `dashboard.py`; load image/audio assets when available and use safe fallback behavior when optional resources cannot be initialized.

**Acceptance:** game logic remains functional even if audio cannot be played.

---

## Theoretical Foundations

### Event-Driven Game Loop

Pygame applications are reactive systems. Each frame executes three logical stages:

```text
Input events
    ↓
State update
    ↓
Rendering
    ↓
Display refresh
```

The main loop in `main.py` processes input first, updates the active game state, renders the corresponding screen, flips the display buffer, and limits execution to 60 FPS.

This structure prevents gameplay logic from being tied directly to drawing code.

### Finite-State Machine

The game lifecycle is modeled with explicit states:

```text
START_SCREEN
    ↓
MENU
    ↓
BET_SETUP
    ↓
SHOW_BACKS
    ↓
SHUFFLE
    ↓
CHOOSE
    ↓
RESULT ──────────────┐
    │                │
    ├─ next round ───┘
    │
    └─ balance < minimum bet
             ↓
         GAME_OVER

PAUSE temporarily suspends active state updates.
```

At any instant, one state determines which events, update rules, and rendering function are valid. This limits accidental interactions between unrelated phases.

### Object-Oriented State Separation

The project separates persistent domain concepts:

- `User` owns player identity and balance;
- `Bet` owns wager limits, amount, multiplier, and stake calculation;
- `Card` owns card identity and screen rectangle;
- `CardGame` coordinates states, timers, animation, round resolution, and persistence;
- `dashboard.py` renders the current state.

This separation reduces coupling between user-interface code and game rules.

### Card Identity vs Card Position

A key invariant is that **card identity belongs to the card object, not to a screen slot**.

During a shuffle, two card rectangles exchange positions, but `is_red` remains attached to the original object. Therefore tracking correctness depends on motion, not on reassigning red/black labels after each swap.

### Non-Blocking Animation

A blocking sleep would freeze input processing and rendering. Instead, the shuffle uses interpolation.

For start position $p_0$, target position $p_1$, and normalized progress $u\in[0,1]$,

```text
p(u) = p0 + u × (p1 - p0)
```

The position is recomputed on successive frames until the 300 ms animation interval is complete.

### Betting Model

Let:

- $B$ be current balance;
- $b$ be the selected base bet;
- $m\in\{1,2,3\}$ be the turbo multiplier.

The nominal stake is

```text
s = b × m
```

and the game resolves an effective stake no larger than the current balance.

For a win:

```text
B' = B + s
```

For a loss or timeout:

```text
B' = max(0, B - s)
```

The session enters `GAME_OVER` when

```text
B' < minimum bet
```

so no new valid round can be started.

### Time-Based State Transitions

Observation, shuffle, and selection phases are controlled from elapsed time:

```text
elapsed = current_ticks - state_start_time
```

Using elapsed time instead of frame counts keeps phase duration approximately independent of small frame-rate fluctuations.

### Persistent History

Each completed round records:

- round number;
- player name;
- base bet;
- multiplier;
- effective stake;
- result;
- chosen card index;
- red-card index;
- round duration;
- balance after the round;
- timestamp.

The data is serialized as JSON. The history is bounded to the latest 200 records to prevent unbounded growth.

### Design Limitations

The current project intentionally remains a local single-player desktop game.

It does not include:

- networking or multiplayer synchronization;
- cryptographic randomness;
- real-money transactions;
- database-backed accounts;
- automated testing infrastructure;
- AI-based card tracking;
- physics-based card motion.

---

## Implementation Architecture

```text
main.py
  │
  ├── User
  │     └── identity + balance
  │
  ├── Bet
  │     └── wager limits + turbo + stake
  │
  └── CardGame
        ├── finite-state controller
        ├── cards and shuffle animation
        ├── timers and input dispatch
        ├── win/loss resolution
        ├── JSON history
        └── Dashboard rendering
```

### Module Responsibilities

| Module | Responsibility |
| --- | --- |
| `src/main.py` | application initialization, Pygame configuration, object creation, 60 FPS main loop |
| `src/game.py` | game states, card model, timers, shuffle animation, input dispatch, round resolution, persistence |
| `src/dashboard.py` | start, menu, betting, gameplay, result, pause, and game-over rendering |
| `src/user.py` | nickname, avatar index, initial/current balance, win/loss balance operations |
| `src/bet.py` | minimum/maximum bet, increments, turbo multiplier, stake calculation, validation |

---

## Project Structure

```text
CardGame/
├── src/
│   ├── assets/
│   ├── bet.py
│   ├── dashboard.py
│   ├── game.py
│   ├── main.py
│   └── user.py
├── data/
│   └── .gitkeep
├── docs/
│   ├── CardGame_Report.pdf
│   └── cardgame_demo.gif
├── .gitignore
├── requirements.txt
└── README.md
```

`data/history.json` is generated at runtime and is intentionally not tracked by Git.

---

## Installation

From the repository root:

```bash
cd Projects/CardGame
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The only direct package dependency is Pygame.

---

## Run

From `Projects/CardGame/`:

```bash
python src/main.py
```

The application opens a **960 × 630** window and targets **60 FPS**.

---

## Controls

| Action | Control |
| --- | --- |
| Leave start screen | any key or mouse click |
| Enter nickname | keyboard |
| Select avatar | mouse |
| Decrease / increase bet | `−` / `+` buttons |
| Select turbo | ×1 / ×2 / ×3 |
| Start round | `START` button |
| Select card | mouse click |
| Pause / resume | `SPACE` |
| Continue / menu / quit | on-screen controls |

---

## Documentation

- [Academic report](docs/CardGame_Report.pdf)
- [Gameplay demo](docs/cardgame_demo.gif)

---

## Technologies

**Python • Pygame • Object-Oriented Programming • Event-Driven Programming • Finite-State Machines • JSON Persistence • 2D Animation • Audio Integration**

---

## Academic Context

**Participants:** Denos Kume, Sena FUKABE  
**Supervisor:** Mira Rizkallah  
**Program:** M1 CORO DASSIP — École Centrale de Nantes  
**Academic Year:** 2025–2026
