import unittest
from pathlib import Path


class InlineMenuInputTests(unittest.TestCase):
    def test_browser_input_uses_inline_dom_field_not_prompt(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertNotIn("window.prompt", source)
        self.assertIn('createElement("input")', source)
        self.assertIn('querySelector("canvas")', source)
        self.assertIn("name_input_rect", source)
        self.assertIn("focus()", source)

    def test_browser_field_syncs_with_nickname(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn("game.user.nickname", source)
        self.assertIn("field.value", source)
        self.assertIn("player_name_max_len", source)


if __name__ == "__main__":
    unittest.main()
