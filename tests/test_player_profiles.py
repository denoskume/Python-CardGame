import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))


class PlayerProfileContractTests(unittest.TestCase):
    def test_profile_module_normalizes_name_and_grants_welcome_once(self):
        import storage as player_profiles

        registry = {}
        first = player_profiles.resolve_profile(registry, "  Denos  Kume ", welcome_balance=30)
        second = player_profiles.resolve_profile(registry, "denos   kume", welcome_balance=30)

        self.assertEqual(first["balance"], 30)
        self.assertTrue(first["welcome_granted_now"])
        self.assertEqual(second["balance"], 30)
        self.assertFalse(second["welcome_granted_now"])
        self.assertEqual(len(registry), 1)

    def test_returning_profile_restores_latest_balance_without_new_bonus(self):
        import storage as player_profiles

        registry = {}
        first = player_profiles.resolve_profile(registry, "Denos", welcome_balance=30)
        registry[first["key"]]["balance"] = 12
        returning = player_profiles.resolve_profile(registry, " DENOS ", welcome_balance=30)

        self.assertEqual(returning["balance"], 12)
        self.assertFalse(returning["welcome_granted_now"])

    def test_controller_restores_profile_balance(self):
        from game_fixture import make_game
        game, clock = make_game(self)
        game.activate_profile()
        game.user.balance = 0
        game._save_history()
        game.reset_game()
        game.activate_profile()
        self.assertEqual(game.user.balance, 0)
        self.assertFalse(game.welcome_balance_granted_now)


if __name__ == "__main__":
    unittest.main()
