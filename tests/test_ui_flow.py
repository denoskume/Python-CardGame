import os
import unittest
from game_fixture import make_game
import game as gm
import pygame

class UIFlowTests(unittest.TestCase):
    def test_unicode_profile_and_spaces(self):
        game, clock = make_game(self)
        game.activate('play')
        game.user.nickname = ''
        game.active_input = True
        game.handle_event(pygame.event.Event(pygame.TEXTINPUT,text='Dé nos'))
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE,unicode=' ',mod=0))
        self.assertEqual(game.state,gm.STATE_MENU)
        self.assertEqual(game.user.nickname,'Dé nos')
        game.activate('continue')
        self.assertEqual(game.state,gm.STATE_BET)

    def test_keyboard_focus_and_overlays(self):
        game, clock = make_game(self)
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_TAB,mod=0))
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN,mod=0))
        self.assertEqual(game.state,gm.STATE_MENU)
        game.activate('back')
        game.activate('help')
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE,mod=0))
        self.assertEqual(game.state,gm.STATE_START)
        game.activate('settings')
        game.activate('back')
        self.assertEqual(game.state,gm.STATE_START)

    def test_numeric_key_uses_visual_position(self):
        game, clock = make_game(self)
        game.start_round()
        game.state = gm.STATE_CHOOSE
        red = next(c for c in game.cards if c.is_red)
        for i,card in enumerate(sorted(game.cards,key=lambda c:not c.is_red)):
            card.slot = i
        game.resize((960,630))
        game.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_1,mod=0))
        self.assertEqual(game.round_result,'WIN')

    def test_touch_then_mouse_settles_once(self):
        game, clock = make_game(self)
        game.start_round()
        game.state=gm.STATE_CHOOSE
        red=next(c for c in game.cards if c.is_red)
        x,y=red.rect.center
        game.handle_event(pygame.event.Event(pygame.FINGERDOWN,x=x/game.w,y=y/game.h))
        game.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(x,y),touch=True))
        self.assertEqual(game.user.balance,40)
        self.assertEqual(len(game.round_history),1)

    @unittest.skipIf(os.environ.get('GITHUB_ACTIONS') == 'true', 'native Pygame raster test is not reliable on headless CI')
    def test_drawing_is_read_only_and_resources_cached(self):
        game,clock=make_game(self)
        game.start_round()
        before=[(c.slot,c.rect.copy()) for c in game.cards]
        state=game.state
        resources=game.resources
        game.draw(); game.draw()
        self.assertEqual([(c.slot,c.rect) for c in game.cards],before)
        self.assertEqual(game.state,state)
        self.assertIs(game.resources,resources)

    @unittest.skipIf(os.environ.get('GITHUB_ACTIONS') == 'true', 'native Pygame raster test is not reliable on headless CI')
    def test_all_screens_render(self):
        game,clock=make_game(self)
        game.start_round()
        for size in [(360,640),(390,844),(844,390),(960,630),(1440,900)]:
            game.screen=pygame.Surface(size)
            for state in [gm.STATE_START,gm.STATE_MENU,gm.STATE_BET,gm.STATE_SHOW_BACKS,gm.STATE_SHUFFLE,gm.STATE_CHOOSE,gm.STATE_RESULT,gm.STATE_GAME_OVER,gm.STATE_PAUSE,'HELP','SETTINGS']:
                game.state=state
                game.resize(size)
                game.draw()
