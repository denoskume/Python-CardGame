import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))


class PlayerProfileContractTests(unittest.TestCase):
    def test_profile_module_normalizes_name_and_grants_welcome_once(self):
        import player_profiles

        registry = {}
        first = player_profiles.resolve_profile(registry, "  Denos  Kume ", welcome_balance=30)
        second = player_profiles.resolve_profile(registry, "denos   kume", welcome_balance=30)

        self.assertEqual(first["balance"], 30)
        self.assertTrue(first["welcome_granted_now"])
        self.assertEqual(second["balance"], 30)
        self.assertFalse(second["welcome_granted_now"])
        self.assertEqual(len(registry), 1)

    def test_returning_profile_restores_latest_balance_without_new_bonus(self):
        import player_profiles

        registry = {}
        first = player_profiles.resolve_profile(registry, "Denos", welcome_balance=30)
        player_profiles.store_balance(registry, first["key"], 12)
        returning = player_profiles.resolve_profile(registry, " DENOS ", welcome_balance=30)

        self.assertEqual(returning["balance"], 12)
        self.assertFalse(returning["welcome_granted_now"])

    def test_browser_profile_storage_uses_local_storage(self):
        source = Path("src/player_profiles.py").read_text(encoding="utf-8")
        self.assertIn("localStorage", source)
        self.assertIn("python-cardgame-profiles-v1", source)
        self.assertIn("welcome_granted", source)

    def test_bet_screen_has_welcome_balance_label(self):
        source = Path("src/welcome_balance_ui.py").read_text(encoding="utf-8")
        self.assertIn("Welcome Balance", source)
        self.assertIn("welcome_balance_granted_now", source)

    def test_main_installs_profiles_after_browser_history(self):
        source = Path("src/main.py").read_text(encoding="utf-8")
        history_pos = source.index("web_history.install(gm)")
        profiles_pos = source.index("player_profiles.install(gm)")
        game_pos = source.index("gm.CardGame(")
        self.assertLess(history_pos, profiles_pos)
        self.assertLess(profiles_pos, game_pos)


if __name__ == "__main__":
    unittest.main()
