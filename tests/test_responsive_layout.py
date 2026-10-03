import unittest
from pathlib import Path


class ResponsiveLayoutContractTests(unittest.TestCase):
    def test_main_uses_browser_viewport_and_resizable_display(self):
        source = Path("src/main.py").read_text(encoding="utf-8")
        self.assertIn("emscripten", source)
        self.assertIn("innerWidth", source)
        self.assertIn("innerHeight", source)
        self.assertIn("pygame.RESIZABLE", source)
        self.assertIn("VIDEORESIZE", source)

    def test_dashboard_defines_adaptive_layout(self):
        source = Path("src/dashboard.py").read_text(encoding="utf-8")
        self.assertIn("def _layout", source)
        self.assertIn("portrait", source)
        self.assertIn("compact", source)
        self.assertIn("_sync_card_geometry", source)
        self.assertIn("min_touch", source)

    def test_target_viewports_are_represented(self):
        source = Path("src/dashboard.py").read_text(encoding="utf-8")
        for marker in ("390", "844", "768", "1024", "1440"):
            self.assertIn(marker, source)

    def test_menu_title_has_reserved_space_above_panel(self):
        source = Path("src/dashboard.py").read_text(encoding="utf-8")
        self.assertIn("title_y =", source)
        self.assertIn("title_clearance =", source)
        self.assertIn("panel_top = max(", source)
        self.assertIn("title_y + title_clearance", source)

    def test_desktop_menu_uses_full_available_width(self):
        source = Path("src/desktop_menu.py").read_text(encoding="utf-8")
        self.assertIn('if cfg["compact"]', source)
        self.assertIn('panel_width = game.w - 2 * cfg["margin"]', source)
        self.assertIn('input_width = min(420', source)
        self.assertIn('btn_w = min(320', source)

    def test_main_installs_desktop_menu_override(self):
        source = Path("src/main.py").read_text(encoding="utf-8")
        self.assertIn("import desktop_menu", source)
        self.assertIn("desktop_menu.install(db)", source)


if __name__ == "__main__":
    unittest.main()
