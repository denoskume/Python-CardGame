"""Capture deterministic UI states using temporary profiles and a dummy display."""
import argparse
import os
import sys
import tempfile
from pathlib import Path
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import pygame
from game import CardGame
from user import User
from bet import Bet
from storage import Storage

parser=argparse.ArgumentParser()
parser.add_argument('--output',required=True)
args=parser.parse_args()
output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
pygame.init();pygame.display.set_mode((960,630))
with tempfile.TemporaryDirectory() as temp:
    for size in [(360,640),(390,844),(844,390),(960,630),(1440,900)]:
        game=CardGame(pygame.Surface(size),User('Denos Kume'),Bet(),Storage(Path(temp)))
        game.start_round()
        game.cards[0].is_red=False;game.cards[1].is_red=True;game.cards[2].is_red=False
        game.round_result='WIN';game.selected_card_index=1
        game.global_history=[dict(round=1,player='Denos Kume',bet=10,stake=10,result='WIN',balance_after=40)]
        game.round_history=game.global_history.copy()
        for state in ['START_SCREEN','MENU','BET_SETUP','SHOW_BACKS','SHUFFLE','CHOOSE','RESULT','GAME_OVER','HELP','SETTINGS','PAUSE']:
            game.state_before_pause='SHUFFLE'
            game.state=state
            for card in game.cards: card.face='FRONT' if state in ('SHUFFLE','CHOOSE','PAUSE') else 'BACK'
            game.resize(size);game.draw()
            pygame.image.save(game.screen,str(output/f'{size[0]}x{size[1]}-{state}.png'))
pygame.quit()
