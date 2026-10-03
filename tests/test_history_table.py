import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class HistoryTableTests(unittest.TestCase):
    def test_columns_match_requested_table(self):
        import history_table
        self.assertEqual(history_table.COLUMNS, ("#", "Player", "Bet", "Result", "Cash", "Goal"))

    def test_win_row_uses_positive_goal(self):
        import history_table
        row = {"round": 4, "player": "Jack", "bet": 10, "stake": 30, "result": "WIN", "balance_after": 90}
        values = history_table.row_values(row)
        self.assertEqual(values, ("4", "Jack", "10$", "WIN", "90$", "+30$"))
        self.assertEqual(history_table.result_kind(row), "positive")

    def test_loss_row_uses_negative_goal(self):
        import history_table
        row = {"round": 5, "player": "Paul", "bet": 20, "stake": 20, "result": "LOSE", "balance_after": 10}
        values = history_table.row_values(row)
        self.assertEqual(values, ("5", "Paul", "20$", "LOSE", "10$", "-20$"))
        self.assertEqual(history_table.result_kind(row), "negative")

    def test_dashboard_uses_history_table(self):
        source = Path("src/dashboard.py").read_text(encoding="utf-8")
        self.assertIn("history_table", source)
        self.assertIn('"Last attempts (all sessions combined):"', source)


if __name__ == "__main__":
    unittest.main()
