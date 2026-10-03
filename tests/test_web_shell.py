import tempfile
import unittest
from pathlib import Path

from scripts.patch_web_shell import patch_web_shell


class WebShellPatchTests(unittest.TestCase):
    def test_generated_shell_uses_browser_viewport(self):
        sample = '''<html><head><style>body { margin: 0; }</style></head><body><canvas id="canvas"></canvas><script>
config = { fb_ar: 1.77, fb_width : "1280", fb_height : "720" }
</script></body></html>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "index.html"
            path.write_text(sample, encoding="utf-8")
            patch_web_shell(path)
            patched = path.read_text(encoding="utf-8")

        self.assertIn("window.innerWidth", patched)
        self.assertIn("window.innerHeight", patched)
        self.assertIn("100vw", patched)
        self.assertIn("100vh", patched)
        self.assertNotIn('fb_width : "1280"', patched)
        self.assertNotIn('fb_height : "720"', patched)


if __name__ == "__main__":
    unittest.main()
