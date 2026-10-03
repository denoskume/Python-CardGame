import unittest
from pathlib import Path


class DirectNameInputTests(unittest.TestCase):
    def test_browser_input_stops_keyboard_event_propagation(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('for (const eventName of ["keydown", "keyup", "keypress"])', source)
        self.assertIn('event.stopPropagation()', source)

    def test_browser_input_keeps_native_text_entry_enabled(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('field.inputMode = "text"', source)
        self.assertNotIn('field.value = current + key', source)


if __name__ == "__main__":
    unittest.main()
