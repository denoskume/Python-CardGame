import unittest
from pathlib import Path


class DirectNameInputTests(unittest.TestCase):
    def test_browser_input_stops_keyboard_event_propagation(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('setAttribute("onkeydown", "event.stopPropagation();")', source)
        self.assertIn('setAttribute("onkeyup", "event.stopPropagation();")', source)
        self.assertIn('setAttribute("onkeypress", "event.stopPropagation();")', source)

    def test_browser_input_keeps_native_text_entry_enabled(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('field.inputMode = "text"', source)


if __name__ == "__main__":
    unittest.main()
