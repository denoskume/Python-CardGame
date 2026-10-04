from pathlib import Path
import unittest


class GlobalTypographyTests(unittest.TestCase):
    def setUp(self):
        self.source = Path("src/theme.py").read_text(encoding="utf-8")

    def test_all_theme_font_roles_use_global_scale(self):
        self.assertIn("TEXT_SCALE_DESKTOP=1.40", self.source)
        self.assertIn("TEXT_SCALE_COMPACT=1.30", self.source)
        self.assertIn("text_scale=TEXT_SCALE_COMPACT if compact else TEXT_SCALE_DESKTOP", self.source)
        self.assertIn("scaled_px=max(10,int(round(px*text_scale)))", self.source)
        self.assertIn("_font(self.assets/('ui-bold.ttf' if bold else 'ui-regular.ttf'),scaled_px,bold)", self.source)


if __name__ == "__main__":
    unittest.main()
