import os
import random
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
sys.path.insert(0, str(Path('src').resolve()))
import pygame
from game import CardGame
from user import User
from bet import Bet
from storage import Storage


def make_game(test, balance=30, now_ms=0):
    pygame.init()
    pygame.display.set_mode((960, 630))
    temp = tempfile.TemporaryDirectory()
    test.addCleanup(temp.cleanup)
    clock = [now_ms]
    timer = patch('pygame.time.get_ticks', side_effect=lambda: clock[0])
    timer.start()
    test.addCleanup(timer.stop)
    random.seed(7)
    with patch.object(CardGame, '_load_history', return_value=[]):
        game = CardGame(pygame.display.get_surface(), User('Denos', initial_balance=balance), Bet(), storage=Storage(Path(temp.name)))
    game.history_file = str(Path(temp.name) / 'history.json')
    return game, clock
