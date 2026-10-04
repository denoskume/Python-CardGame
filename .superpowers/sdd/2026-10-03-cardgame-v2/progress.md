# SDD ledger — plan: docs/superpowers/plans/2026-10-03-cardgame-v2.md
Pre-flight: Task 1 controller settlement feeds Task 4 timing and Task 5 input; preserve resolve_round boundary.
Pre-flight: Task 2 Storage supplies Task 3 settings and Task 5 notices; matching signatures.
Pre-flight: Task 4 shared layout consumed by Task 5 renderer/input; matching signatures.
Pre-flight: Task 5 assets/input consumed by Task 6 build; keep audio conversion and native input.
Ruling: use sibling worktree CardGame-v2 — isolated managed scratch with no tracked worktree directory change — cost if wrong: workspace relocation only.
Task 1: complete (commits 335975c..52624d8, tests: python -m unittest discover -s tests -v → Hello from the pygame community. https://www.pygame.org/contribute.html)
Task 2: Ruling: replace two install-order source tests with injected-storage and zero-balance profile behavior — architecture now calls storage explicitly — cost if wrong: behavioral regression caught by controller tests. Legacy modules remain until UI migration removes all dependencies.
Task 2: complete (commits 52624d8..ed92c84, tests: python -m unittest discover -s tests -v → Hello from the pygame community. https://www.pygame.org/contribute.html)
Task 3: complete (commits ed92c84..46618cc, tests: python -m unittest discover -s tests -v → Hello from the pygame community. https://www.pygame.org/contribute.html)
Task 4: complete (commits 46618cc..d135e14, tests: python -m unittest discover -s tests -v → Hello from the pygame community. https://www.pygame.org/contribute.html)
Task 5: Ruling: replace legacy source-string UI/install tests with real controller, layout, render and native-field adapter tests — old assertions enforced method patches removed by the approved architecture — cost if wrong: native browser integration still requires live walkthrough.
Task 5: Ruling: retain history_table pure aggregation and dynamic_difficulty compatibility helpers, remove obsolete install modules — protects existing behavior without runtime patching — cost if wrong: small compatibility surface remains.
Task 5: Visual QA found short-landscape header collisions and avatar/label overlap; corrected layout after failing clearance test. Desktop/mobile contact sheets inspected.
Task 5: complete (commits d135e14..da7f43f, tests: python -m unittest discover -s tests -v → Hello from the pygame community. https://www.pygame.org/contribute.html)
Final review: fresh gpt-6-astra reviewer identified two Important inherited history issues; no Critical or Minor findings.
Final: fixed malformed history bet/type and huge timestamp startup crash — test_malformed_consumed_fields_and_huge_time_are_skipped RED→GREEN.
Final: fixed distinct sessions collapsed by event dedup — test_distinct_sessions_do_not_disappear RED→GREEN; full suite 57/57.
Final: Ruling: reviewer deferred physical mobile keyboard/audio judgment to runtime verification — emulator checks and explicit device-coverage limitations will accompany delivery — cost if wrong: device-specific input/audio issues remain possible.

Task 6: build and runtime verification complete (tests, compileall, web build, desktop smoke, Chromium flow, responsive captures, benchmark).
Task 7: documentation prepared (README, CHANGELOG, verification report, deployment workflow).
