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

    def test_same_player_is_aggregated_into_one_row(self):
        import history_table
        rows = [
            {"round": 1, "player": "Drama", "bet": 25, "stake": 25, "result": "WIN", "balance_after": 55},
            {"round": 2, "player": " drama ", "bet": 50, "stake": 100, "result": "LOSE", "balance_after": 0},
            {"round": 3, "player": "DRAMA", "bet": 20, "stake": 20, "result": "WIN", "balance_after": 20},
        ]
        aggregated = history_table.aggregate_players(rows, limit=5)
        self.assertEqual(len(aggregated), 1)
        row = aggregated[0]
        self.assertEqual(row["player"], "DRAMA")
        self.assertEqual(row["total_bet"], 95)
        self.assertEqual(row["wins"], 2)
        self.assertEqual(row["losses"], 1)
        self.assertEqual(row["cash"], 20)
        self.assertEqual(row["goal"], -55)

    def test_only_five_most_recent_unique_players_are_returned(self):
        import history_table
        rows = []
        for index, name in enumerate(("A", "B", "C", "D", "E", "F"), start=1):
            rows.append({"round": index, "player": name, "bet": 10, "stake": 10, "result": "WIN", "balance_after": 40})
        rows.append({"round": 7, "player": "B", "bet": 10, "stake": 10, "result": "LOSE", "balance_after": 30})
        aggregated = history_table.aggregate_players(rows, limit=5)
        self.assertEqual([row["player"] for row in aggregated], ["B", "F", "E", "D", "C"])
        self.assertEqual(len(aggregated), 5)

    def test_row_values_show_aggregated_player_data(self):
        import history_table
        row = {
            "player": "Drama",
            "total_bet": 120,
            "wins": 3,
            "losses": 2,
            "cash": 105,
            "goal": 25,
        }
        self.assertEqual(
            history_table.row_values(row, display_index=1),
            ("1", "Drama", "120$", "3W / 2L", "105$", "+25$"),
        )


    def test_distinct_sessions_do_not_disappear(self):
        from history_table import aggregate_players
        rows=[dict(round=1,player='Denos',bet=10,stake=10,result=result,balance_after=balance,timestamp=stamp)
              for result,balance,stamp in [('WIN',40,1),('LOSE',30,2),('WIN',40,3)]]
        row=aggregate_players(rows)[0]
        self.assertEqual((row['wins'],row['losses'],row['goal']),(2,1,10))


if __name__ == "__main__":
    unittest.main()
