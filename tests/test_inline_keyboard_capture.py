import unittest
from pathlib import Path


class InlineKeyboardCaptureTests(unittest.TestCase):
    def test_browser_field_preserves_native_key_handling(self):
        source = Path("src/menu_input.py").read_text(encoding="utf-8")
        self.assertIn('addEventListener(eventName', source)
        self.assertIn('event.stopPropagation()', source)
        self.assertIn('event.key === "Enter"', source)
        self.assertNotIn('event.key === "Backspace"', source)
        self.assertNotIn('field.value = current + key', source)
        self.assertNotIn('dispatchEvent(new Event("input"', source)


if __name__ == "__main__":
    unittest.main()
