import unittest
from game_fixture import make_game
from bet import Bet
import game as gm

class RoundRulesTests(unittest.TestCase):
    def test_total_stake_must_be_affordable(self):
        self.assertFalse(Bet(amount=15, turbo=3).is_valid(30))
        self.assertTrue(Bet(amount=10, turbo=3).is_valid(30))
        self.assertFalse(Bet(amount=10, turbo=True).is_valid(30))
        self.assertFalse(Bet(amount=10.5).is_valid(30))

    def test_settlement_once_and_frozen_stake(self):
        game, clock = make_game(self)
        game.start_round()
        game.state = gm.STATE_CHOOSE
        red = next(i for i,c in enumerate(game.cards) if c.is_red)
        game.bet.amount = 20
        game.resolve_round(red)
        game.resolve_round(red)
        self.assertEqual(game.user.balance, 40)
        self.assertEqual(len(game.round_history), 1)

    def test_loss_and_invalid_index(self):
        game, clock = make_game(self)
        game.start_round()
        game.state = gm.STATE_CHOOSE
        game.resolve_round(99)
        self.assertEqual(game.user.balance, 30)
        black = next(i for i,c in enumerate(game.cards) if not c.is_red)
        game.resolve_round(black)
        self.assertEqual(game.user.balance, 20)

    def test_deadline_selection_is_timeout(self):
        game, clock = make_game(self)
        game.start_round()
        game.state = gm.STATE_CHOOSE
        clock[0] = 10000
        game.resolve_round(next(i for i,c in enumerate(game.cards) if c.is_red))
        self.assertEqual(game.user.balance, 20)
        self.assertIsNone(game.round_history[-1]['chosen_index'])

    def test_invalid_round_cannot_start(self):
        game, clock = make_game(self)
        game.bet.amount, game.bet.turbo = 15, 3
        game.start_round()
        self.assertEqual(game.cards, [])

    def test_net_uses_profit_not_payout(self):
        import game_statistics as stats
        self.assertEqual(stats.summarize_rounds([{'result':'WIN','stake':10},{'result':'LOSE','stake':10}])['net'], 0)
        self.assertIsNone(stats.summarize_rounds([])['win_rate'])
