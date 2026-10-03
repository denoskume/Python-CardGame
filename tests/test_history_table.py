import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class HistoryTableTests(unittest.TestCase):
    def test_columns_include_occurrences(self):
        import history_table
        self.assertEqual(
            history_table.COLUMNS,
            ("#", "Player", "Occ.", "Bet", "Result", "Cash", "Goal"),
        )

    def test_history_is_aggregated_by_normalized_player(self):
        import history_table
        rows = [
            {"round": 1, "player": "Drama", "bet": 25, "stake": 25, "result": "WIN", "balance_after": 55},
            {"round": 2, "player": " drama ", "bet": 25, "stake": 25, "result": "WIN", "balance_after": 80},
            {"round": 3, "player": "DRAMA", "bet": 50, "stake": 150, "result": "LOSE", "balance_after": 30},
            {"round": 4, "player": "John", "bet": 10, "stake": 10, "result": "LOSE", "balance_after": 20},
        ]
        summaries = history_table.summarize_players(rows, limit=5)
        self.assertEqual(len(summaries), 2)
        self.assertEqual(summaries[0]["player"], "John")
        drama = summaries[1]
        self.assertEqual(drama["player"], "DRAMA")
        self.assertEqual(drama["occurrences"], 3)
        self.assertEqual(drama["total_bet"], 100)
        self.assertEqual(drama["wins"], 2)
        self.assertEqual(drama["losses"], 1)
        self.assertEqual(drama["cash"], 30)
        self.assertEqual(drama["goal"], -100)

    def test_only_five_most_recent_unique_players_are_returned(self):
        import history_table
        rows = []
        for index, name in enumerate(("A", "B", "C", "D", "E", "F"), start=1):
            rows.append({"round": index, "player": name, "bet": 10, "stake": 10, "result": "WIN", "balance_after": 40})
        rows.append({"round": 7, "player": "B", "bet": 20, "stake": 20, "result": "LOSE", "balance_after": 20})
        summaries = history_table.summarize_players(rows, limit=5)
        self.assertEqual([row["player"] for row in summaries], ["B", "F", "E", "D", "C"])
        self.assertEqual(summaries[0]["occurrences"], 2)

    def test_summary_row_values(self):
        import history_table
        summary = {
            "player": "Drama",
            "occurrences": 7,
            "total_bet": 175,
            "wins": 5,
            "losses": 2,
            "cash": 105,
            "goal": 75,
        }
        self.assertEqual(
            history_table.row_values(summary, 1),
            ("1", "Drama", "7", "175$", "5W / 2L", "105$", "+75$"),
        )

    def test_main_installs_history_table(self):
        source = Path("src/main.py").read_text(encoding="utf-8")
        self.assertIn("history_table.install(db)", source)
        module = Path("src/history_table.py").read_text(encoding="utf-8")
        self.assertIn('"Last attempts (all sessions combined):"', module)


if __name__ == "__main__":
    unittest.main()
