import unittest
from unittest.mock import patch
from game_fixture import make_game
import game as gm

class SettingsTests(unittest.TestCase):
    def test_difficulty_timing(self):
        from settings import shuffle_timing
        for level, streak, expected in [('easy',0,(420,420)),('expert',0,(150,150)),('normal',0,(300,300)),('normal',1,(300,300)),('normal',2,(240,240)),('normal',3,(200,200)),('normal',4,(170,170))]:
            self.assertEqual(shuffle_timing(level,streak),expected)

    def test_preferences_normalize_invalid_storage(self):
        from settings import Settings
        self.assertEqual(Settings('invalid', volume=4).volume,1)
        self.assertEqual(Settings('invalid').difficulty,'normal')
        self.assertEqual(Settings(volume=-1).volume,0)

    def test_round_timing_frozen_and_streak_reset(self):
        from settings import Settings
        game, clock = make_game(self)
        game.apply_settings(Settings('easy'))
        game.start_round()
        game.apply_settings(Settings('expert'))
        self.assertEqual(game.swap_duration,420)
        game.state = gm.STATE_BET
        game.start_round()
        self.assertEqual(game.swap_duration,150)
        game.consecutive_wins = 4
        game.activate_profile()
        self.assertEqual(game.consecutive_wins,0)

    def test_muted_audio_does_not_play(self):
        from settings import Settings
        game, clock = make_game(self)
        game.apply_settings(Settings(sound_enabled=False))
        game.play_sound('win')
        self.assertIsNone(game.result_channel)

    def test_audio_unavailable_is_nonfatal(self):
        game, clock = make_game(self)
        with patch('pygame.mixer.init', side_effect=gm.pygame.error('unavailable')):
            gm.pygame.mixer.quit()
            game.enable_audio()
            game.play_sound('win')
        self.assertIsNone(game.result_channel)
