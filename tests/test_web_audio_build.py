import unittest
from pathlib import Path


class WebAudioBuildTests(unittest.TestCase):
    def test_web_build_converts_mp3_to_ogg_in_staged_copy(self):
        script = Path("scripts/build_web.sh").read_text(encoding="utf-8")
        workflow = Path(".github/workflows/deploy-web.yml").read_text(encoding="utf-8")

        self.assertIn("ffmpeg", workflow.lower())
        self.assertIn("web-src", script)
        self.assertIn("for sound in shuffle win lose", script)
        self.assertIn("${sound}.mp3", script)
        self.assertIn("${sound}.ogg", script)
        self.assertIn('s/\\.mp3"/\\.ogg"/g', script)
        self.assertIn("pygbag", script)


if __name__ == "__main__":
    unittest.main()
