"""Adaptive shuffle speed based on consecutive wins."""


def next_win_streak(current_streak: int, result: str) -> int:
    """Advance a win streak or reset it after any non-win result."""
    return current_streak + 1 if result == "WIN" else 0


def shuffle_timing(win_streak: int) -> tuple[int, int]:
    """Return (shuffle interval, swap duration) in milliseconds."""
    if win_streak >= 4:
        return 170, 170
    if win_streak == 3:
        return 200, 200
    if win_streak == 2:
        return 240, 240
    return 300, 300
