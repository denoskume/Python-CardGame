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


def install(game_module) -> None:
    """Apply adaptive timing after each completed round."""
    original_init = game_module.CardGame.__init__
    original_resolve_round = game_module.CardGame.resolve_round

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.consecutive_wins = 0
        self.shuffle_interval, self.swap_duration = shuffle_timing(0)

    def resolve_round(self, index):
        original_resolve_round(self, index)
        self.consecutive_wins = next_win_streak(
            getattr(self, "consecutive_wins", 0),
            self.round_result,
        )
        self.shuffle_interval, self.swap_duration = shuffle_timing(self.consecutive_wins)

    game_module.CardGame.__init__ = __init__
    game_module.CardGame.resolve_round = resolve_round
