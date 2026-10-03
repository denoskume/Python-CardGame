import unittest
from pathlib import Path


class MenuInputContractTests(unittest.TestCase):
    def test_menu_shows_required_instructions(self):
        source = Path("src/desktop_menu.py").read_text(encoding="utf-8")
        self.assertIn("Enter your nickname or name", source)
        self.assertIn("Select your avatar", source)
        self.assertIn("name_input_rect", source)

    def test_browser_input_uses_inline_native_field(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('sys.platform != "emscripten"', source)
        self.assertNotIn("platform.window.prompt", source)
        self.assertIn('createElement("input")', source)
        self.assertIn('querySelector("canvas")', source)
        self.assertIn("pygame.key.start_text_input()", source)
        self.assertIn("name_input_rect", source)

    def test_main_installs_menu_input(self):
        source = Path("src/main.py").read_text(encoding="utf-8")
        self.assertIn("import menu_input", source)
        self.assertIn("menu_input.install(gm)", source)


if __name__ == "__main__":
    unittest.main()
