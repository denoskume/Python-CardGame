import tempfile
import unittest
from pathlib import Path

from scripts.patch_web_shell import patch


SAMPLE_HTML = """<html><head></head><body><script>
config = {
    fb_ar   :  1.77,
    fb_width : "1280",
    fb_height : "720"
}
</script><canvas class="emscripten" id="canvas"></canvas></body></html>"""


class WebShellTests(unittest.TestCase):
    def test_patch_replaces_fixed_framebuffer_with_viewport_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index.html"
            index.write_text(SAMPLE_HTML, encoding="utf-8")
            patch(index)
            html = index.read_text(encoding="utf-8")

        self.assertNotIn('fb_width : "1280"', html)
        self.assertNotIn('fb_height : "720"', html)
        self.assertNotIn('fb_ar   :  1.77', html)
        self.assertIn('String(window.innerWidth)', html)
        self.assertIn('String(window.innerHeight)', html)
        self.assertIn('100vw !important', html)
        self.assertIn('100vh !important', html)
        self.assertIn('syncViewportFramebuffer', html)


if __name__ == "__main__":
    unittest.main()
