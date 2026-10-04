import os
import sys
from pathlib import Path
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pygame
from theme import SmoothFallbackFont


class SmoothFallbackFontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.font.init()

    def test_fallback_renders_at_target_scale_from_supersampled_source(self):
        font = SmoothFallbackFont(28, bold=False)
        self.assertGreaterEqual(font.source_size, 56)

        surface = font.render("Remember the red card.", True, (241, 238, 231))
        measured = font.size("Remember the red card.")

        self.assertEqual(surface.get_size(), measured)
        self.assertGreater(surface.get_width(), 0)
        self.assertGreater(surface.get_height(), 0)

    def test_fallback_preserves_bold_role(self):
        font = SmoothFallbackFont(24, bold=True)
        self.assertTrue(font.get_bold())


if __name__ == "__main__":
    unittest.main()
