import unittest
from game_fixture import make_game
import game as gm

class RoundTimingTests(unittest.TestCase):
    def test_pause_excludes_active_time(self):
        game, clock = make_game(self)
        game.start_round()
        clock[0] = 5000
        game.pause(clock[0])
        clock[0] = 10000
        game.resume(clock[0])
        self.assertEqual(clock[0] - game.state_start_time,5000)
        game.state = gm.STATE_CHOOSE
        game.resolve_round(None)
        self.assertEqual(game.round_history[-1]['duration'],5)

    def test_resize_preserves_half_swap(self):
        game, clock = make_game(self)
        game.start_round()
        game.state = gm.STATE_SHUFFLE
        game.swap_two_cards()
        identities = [c.is_red for c in game.cards]
        initial_slots = [c.slot for c in game.cards]
        clock[0] = 150
        game.update_shuffle()
        game.resize((390,844))
        self.assertTrue(game.is_swapping)
        self.assertEqual([c.is_red for c in game.cards],identities)
        clock[0] = 300
        game.update_shuffle()
        self.assertEqual(game.cards[game.swap_i].slot, initial_slots[game.swap_j])
        self.assertEqual(game.cards[game.swap_j].slot, initial_slots[game.swap_i])

    def test_focus_loss_pauses_round(self):
        game, clock = make_game(self)
        game.start_round()
        game.handle_event(gm.pygame.event.Event(gm.pygame.WINDOWFOCUSLOST))
        self.assertEqual(game.state,gm.STATE_PAUSE)
