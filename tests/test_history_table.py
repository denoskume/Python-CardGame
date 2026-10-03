import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class HistoryTableTests(unittest.TestCase):
    def test_columns_match_last_attempts_table(self):
        import history_table
        self.assertEqual(
            history_table.COLUMNS,
            ("#", "Player", "Bet", "Result", "Cash", "Goal"),
        )

    def test_returns_only_five_latest_unique_events(self):
        import history_table
        duplicate = {"round": 7, "player": "Drama", "bet": 25, "stake": 25, "result": "WIN", "balance_after": 105}
        rows = [
            {"round": 3, "player": "Drama", "bet": 45, "stake": 90, "result": "WIN", "balance_after": 180},
            {"round": 4, "player": "Drama", "bet": 50, "stake": 150, "result": "LOSE", "balance_after": 30},
            {"round": 5, "player": "Drama", "bet": 25, "stake": 25, "result": "WIN", "balance_after": 55},
            {"round": 6, "player": "Drama", "bet": 25, "stake": 25, "result": "WIN", "balance_after": 80},
            duplicate,
            dict(duplicate),
            {"round": 8, "player": "Drama", "bet": 25, "stake": 25, "result": "WIN", "balance_after": 130},
            {"round": 9, "player": "Drama", "bet": 25, "stake": 25, "result": "LOSE", "balance_after": 105},
        ]
        latest = history_table.latest_events(rows, limit=5)
        self.assertEqual([row["round"] for row in latest], [9, 8, 7, 6, 5])
        self.assertEqual(len(latest), 5)

    def test_row_values_use_real_event_data(self):
        import history_table
        row = {"round": 8, "player": "Drama", "bet": 25, "stake": 25, "result": "WIN", "balance_after": 130}
        self.assertEqual(
            history_table.row_values(row),
            ("8", "Drama", "25$", "WIN", "130$", "+25$"),
        )

    def test_loss_goal_is_negative(self):
        import history_table
        row = {"round": 9, "player": "Drama", "bet": 25, "stake": 25, "result": "LOSE", "balance_after": 105}
        self.assertEqual(history_table.row_values(row)[-1], "-25$")

    def test_main_installs_history_table(self):
        source = Path("src/main.py").read_text(encoding="utf-8")
        self.assertIn("history_table.install(db)", source)
        module = Path("src/history_table.py").read_text(encoding="utf-8")
        self.assertIn('"Last attempts (all sessions combined):"', module)


if __name__ == "__main__":
    unittest.main()
