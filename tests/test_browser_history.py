import unittest
from pathlib import Path


class BrowserHistoryContractTests(unittest.TestCase):
    def test_web_history_uses_local_storage(self):
        source = Path("src/web_history.py").read_text(encoding="utf-8")
        self.assertIn("localStorage", source)
        self.assertIn("python-cardgame-history-v1", source)
        self.assertIn("getItem", source)
        self.assertIn("setItem", source)
        self.assertIn("[-200:]", source)

    def test_main_installs_web_history_before_game_creation(self):
        source = Path("src/main.py").read_text(encoding="utf-8")
        install_pos = source.index("web_history.install(gm)")
        game_pos = source.index("gm.CardGame(")
        self.assertLess(install_pos, game_pos)


if __name__ == "__main__":
    unittest.main()
