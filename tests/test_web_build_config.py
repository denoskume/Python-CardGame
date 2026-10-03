from pathlib import Path
import unittest


class WebBuildConfigTests(unittest.TestCase):
    def test_pygbag_build_is_configured(self):
        requirements = Path("requirements.txt").read_text(encoding="utf-8").lower()
        script = Path("scripts/build_web.sh")
        self.assertIn("pygbag", requirements)
        self.assertTrue(script.exists())
        content = script.read_text(encoding="utf-8")
        self.assertIn("set -euo pipefail", content)
        self.assertIn("python -m pygbag", content)
        self.assertIn("--build", content)
        self.assertIn("src", content)
        self.assertIn("src/build/web", content)


if __name__ == "__main__":
    unittest.main()
