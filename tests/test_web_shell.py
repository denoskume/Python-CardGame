import tempfile
import unittest
from pathlib import Path

from scripts.patch_web_shell import patch


SAMPLE_HTML = """<html><head></head><body><script>
config = {
    user_canvas : 0,
    user_canvas_managed : 0,
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

    def test_patch_prevents_pygbag_from_overriding_canvas_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            index = Path(tmp) / "index.html"
            index.write_text(SAMPLE_HTML, encoding="utf-8")
            patch(index)
            html = index.read_text(encoding="utf-8")

        self.assertIn('user_canvas : 1', html)
        self.assertIn('user_canvas_managed : 1', html)
        self.assertNotIn('user_canvas_managed : 0', html)

    def test_build_exposes_loading_and_recovery(self):
        from html.parser import HTMLParser
        class Elements(HTMLParser):
            def __init__(self): super().__init__(); self.ids=set()
            def handle_starttag(self,tag,attrs):
                self.ids.update(value for key,value in attrs if key=='id')
        with tempfile.TemporaryDirectory() as tmp:
            index=Path(tmp)/'index.html';index.write_text(SAMPLE_HTML)
            patch(index)
            parser=Elements();parser.feed(index.read_text())
            self.assertTrue({'cardgame-loading','cardgame-load-status','cardgame-start','cardgame-retry'} <= parser.ids)
            self.assertIn('activateCardGame()', index.read_text(encoding='utf-8'))


if __name__ == "__main__":
    unittest.main()
