import unittest
from pathlib import Path


class InlineKeyboardCaptureTests(unittest.TestCase):
    def test_browser_field_has_manual_key_capture(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('addEventListener("keydown"', source)
        self.assertIn('event.key == "Backspace"', source)
        self.assertIn('event.key == "Enter"', source)
        self.assertIn('len(str(event.key)) == 1', source)
        self.assertIn('field.value = current + key', source)


if __name__ == "__main__":
    unittest.main()
