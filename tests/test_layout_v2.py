import unittest
import sys
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import pygame
from layout import compute_layout

class LayoutV2Tests(unittest.TestCase):
    def test_start_action_is_centered_in_hero_area(self):
        layout = compute_layout((960, 630), 'START_SCREEN')
        play = layout['btn_play']
        self.assertEqual(play.size, (220, 48))
        self.assertEqual(play.centerx, 331)
        self.assertEqual(play.y, 300)
        self.assertLess(play.bottom, layout['card_0'].top)

    def test_controls_stay_inside_viewport(self):
        from layout import compute_layout
        for size in [(360,640),(390,844),(844,390),(960,630),(1440,900)]:
            bounds = pygame.Rect((0,0),size)
            for state in ['START_SCREEN','MENU','BET_SETUP','SHOW_BACKS','CHOOSE','RESULT','GAME_OVER','HELP','SETTINGS','PAUSE']:
                layout = compute_layout(size,state)
                for key,rect in layout.items():
                    if key.startswith('btn_'):
                        self.assertTrue(bounds.contains(rect),(size,state,key,rect))
                        self.assertGreaterEqual(min(rect.size),44)
                if state == 'RESULT':
                    for i in range(3):
                        for key,rect in layout.items():
                            if key.startswith('btn_'):
                                self.assertFalse(layout[f'card_{i}'].colliderect(rect))

    def test_landscape_header_clearance(self):
        from layout import compute_layout
        layout=compute_layout((844,390),'MENU')
        self.assertGreaterEqual(layout['name_input'].top,170)
        layout=compute_layout((844,390),'RESULT')
        self.assertGreaterEqual(layout['card_0'].top,176)
        self.assertLessEqual(layout['card_0'].bottom,290)
