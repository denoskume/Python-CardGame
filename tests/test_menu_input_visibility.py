import unittest
from pathlib import Path


class MenuInputVisibilityTests(unittest.TestCase):
    def test_web_input_forces_visible_text_and_caret(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('"-webkit-text-fill-color", "#111111", "important"', source)
        self.assertIn('"color", "#111111", "important"', source)
        self.assertIn('"caret-color", "#111111", "important"', source)
        self.assertIn('"opacity", "1", "important"', source)

    def test_web_input_does_not_use_browser_prompt(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertNotIn("window.prompt", source)
        self.assertNotIn("platform.window.prompt", source)


if __name__ == "__main__":
    unittest.main()
