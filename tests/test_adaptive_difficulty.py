import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class AdaptiveDifficultyTests(unittest.TestCase):
    def test_shuffle_timing_by_win_streak(self):
        import dynamic_difficulty as difficulty

        self.assertEqual(difficulty.shuffle_timing(0), (300, 300))
        self.assertEqual(difficulty.shuffle_timing(1), (300, 300))
        self.assertEqual(difficulty.shuffle_timing(2), (240, 240))
        self.assertEqual(difficulty.shuffle_timing(3), (200, 200))
        self.assertEqual(difficulty.shuffle_timing(4), (170, 170))
        self.assertEqual(difficulty.shuffle_timing(9), (170, 170))

    def test_win_streak_resets_after_loss(self):
        import dynamic_difficulty as difficulty

        streak = difficulty.next_win_streak(0, "WIN")
        streak = difficulty.next_win_streak(streak, "WIN")
        self.assertEqual(streak, 2)
        self.assertEqual(difficulty.next_win_streak(streak, "LOSE"), 0)

    def test_default_max_bet_is_1000(self):
        import bet

        self.assertEqual(bet.Bet().max, 1000)

    def test_main_uses_1000_max_bet(self):
        source = Path("src/main.py").read_text(encoding="utf-8")
        self.assertIn("max_amount=1000", source)


if __name__ == "__main__":
    unittest.main()
