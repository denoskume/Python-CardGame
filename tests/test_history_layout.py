import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class HistoryLayoutTests(unittest.TestCase):
    def test_visible_rows_fit_inside_panel(self):
        import history_table

        self.assertEqual(history_table.visible_row_limit(330, 28, table_offset=44, bottom_padding=12), 8)
        self.assertEqual(history_table.visible_row_limit(245, 28, table_offset=44, bottom_padding=12), 5)

    def test_panel_height_uses_available_desktop_space(self):
        import history_table

        self.assertEqual(history_table.panel_height(600, 204, 30), 330)
        self.assertEqual(history_table.panel_height(420, 143, 20), 257)


if __name__ == "__main__":
    unittest.main()
