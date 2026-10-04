import unittest
from pathlib import Path


class BrowserHistoryContractTests(unittest.TestCase):
    def test_controller_uses_injected_storage(self):
        from game_fixture import make_game
        game, clock = make_game(self)
        game.global_history = []
        game._save_history()
        self.assertEqual(game.storage.load_history(), [])


if __name__ == "__main__":
    unittest.main()
