import ast
from pathlib import Path
import unittest


class MainEntryContractTests(unittest.TestCase):
    def setUp(self):
        self.source = Path("src/main.py").read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)

    def test_main_is_async_and_yields_to_asyncio(self):
        async_main = next(
            (node for node in self.tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "main"),
            None,
        )
        self.assertIsNotNone(async_main)

        imports_asyncio = any(
            isinstance(node, ast.Import) and any(alias.name == "asyncio" for alias in node.names)
            for node in self.tree.body
        )
        self.assertTrue(imports_asyncio)

        has_async_yield = any(
            isinstance(node, ast.Await)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "asyncio"
            and node.value.func.attr == "sleep"
            and len(node.value.args) == 1
            and isinstance(node.value.args[0], ast.Constant)
            and node.value.args[0].value == 0
            for node in ast.walk(async_main)
        )
        self.assertTrue(has_async_yield)

    def test_main_guard_uses_asyncio_run(self):
        self.assertIn("asyncio.run(main())", self.source)


if __name__ == "__main__":
    unittest.main()
