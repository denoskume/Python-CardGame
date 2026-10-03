import unittest
from pathlib import Path


class BetAvatarReturnTests(unittest.TestCase):
    def test_bet_screen_renders_selected_avatar_without_label(self):
        source = Path("src/dashboard.py").read_text(encoding="utf-8")
        self.assertIn("game.user.avatar_index", source)
        self.assertIn("bet_avatar_rect", source)
        self.assertNotIn('"Selected Avatar"', source)

    def test_bet_screen_renders_return_button(self):
        source = Path("src/dashboard.py").read_text(encoding="utf-8")
        self.assertIn("btn_bet_return", source)
        self.assertIn('"← Return"', source)

    def test_return_button_goes_back_to_menu(self):
        source = Path("src/game.py").read_text(encoding="utf-8")
        self.assertIn("btn_bet_return", source)
        self.assertIn("self.state = STATE_MENU", source)


if __name__ == "__main__":
    unittest.main()
