import unittest
from pathlib import Path


class NativeInlineMenuTypingTests(unittest.TestCase):
    def test_browser_field_keeps_native_character_input(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertNotIn('field.value = current + key', source)
        self.assertNotIn('event.preventDefault();\n                  event.stopPropagation();\n                }', source)

    def test_browser_field_still_stops_key_events_from_reaching_game(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('event.stopPropagation()', source)
        self.assertIn('field.focus()', source)


if __name__ == "__main__":
    unittest.main()
