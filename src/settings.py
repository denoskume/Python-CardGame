"""Normalized preferences and explicit difficulty timing."""
from dataclasses import dataclass, asdict
import math

@dataclass
class Settings:
    difficulty: str = 'normal'
    sound_enabled: bool = True
    volume: float = 0.6

    def __post_init__(self):
        if self.difficulty not in ('easy', 'normal', 'expert'):
            self.difficulty = 'normal'
        if type(self.sound_enabled) is not bool:
            self.sound_enabled = True
        if type(self.volume) not in (int, float) or not math.isfinite(self.volume):
            self.volume = 0.6
        self.volume = max(0, min(1, self.volume))

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, value):
        return cls(**{key: value[key] for key in ('difficulty', 'sound_enabled', 'volume') if key in value})


def shuffle_timing(difficulty: str, streak: int) -> tuple[int, int]:
    if difficulty == 'easy':
        return 420, 420
    if difficulty == 'expert':
        return 150, 150
    duration = 170 if streak >= 4 else 200 if streak == 3 else 240 if streak == 2 else 300
    return duration, duration
