from pathlib import Path
import unittest


class PagesWorkflowTests(unittest.TestCase):
    def test_pages_workflow_contains_required_steps(self):
        path = Path(".github/workflows/deploy-web.yml")
        self.assertTrue(path.exists())
        content = path.read_text(encoding="utf-8")
        for required in (
            "workflow_dispatch:",
            "branches: [main]",
            "pages: write",
            "id-token: write",
            "actions/setup-python",
            "pip install -r requirements.txt",
            "bash scripts/build_web.sh",
            "actions/upload-pages-artifact",
            "actions/deploy-pages",
        ):
            self.assertIn(required, content)


if __name__ == "__main__":
    unittest.main()
