import unittest
from urllib.parse import quote
from unittest.mock import patch
from types import SimpleNamespace
from game_fixture import make_game
import menu_input

class Field:
    def __init__(self):
        self.value='';self.attrs={};self.styles={};self.removed=False
        self.style=SimpleNamespace(setProperty=lambda key,value,*args:self.styles.update({key:value}))
    def setAttribute(self,key,value):self.attrs[key]=value
    def getAttribute(self,key):return self.attrs.get(key)
    def removeAttribute(self,key):self.attrs.pop(key,None)
    def remove(self):self.removed=True
    def focus(self):pass

class NativeFieldTests(unittest.TestCase):
    def setUp(self):
        self.game,self.clock=make_game(self)
        self.game.activate('play')
        self.field=Field()
        self.document=SimpleNamespace(getElementById=lambda key:self.field,
            querySelector=lambda key:SimpleNamespace(getBoundingClientRect=lambda:SimpleNamespace(width=480,height=315,left=10,top=20)))
        self.platform=SimpleNamespace(window=SimpleNamespace(document=self.document,eval=lambda code:quote(self.field.value) if code.startswith("encodeURIComponent") else None))

    def test_native_input_matches_canvas_scaling_and_visible_palette(self):
        with patch('sys.platform','emscripten'),patch.dict('sys.modules',{'platform':self.platform}):
            menu_input._ensure_browser_field(self.game)
        r=self.game.name_input_rect
        self.assertEqual(self.field.styles['left'],f'{10+r.x*.5}px')
        self.assertEqual(self.field.styles['width'],f'{r.width*.5}px')
        self.assertNotEqual(self.field.styles['color'],self.field.styles['background'])

    def test_unicode_paste_and_enter_submit(self):
        self.field.value='Dé nos'
        self.field.attrs['data-submit']='1'
        with patch('sys.platform','emscripten'),patch.dict('sys.modules',{'platform':self.platform}):
            menu_input.update_native_field(self.game)
        self.assertEqual(self.game.user.nickname,'Dé nos')
        self.assertEqual(self.game.state,'BET_SETUP')
        self.assertNotIn('data-submit',self.field.attrs)

    def test_browser_bridge_preserves_utf8_names(self):
        self.field.value='DÃ© nos'
        self.platform.window.eval=lambda code:'D%C3%A9%20nos'
        with patch('sys.platform','emscripten'),patch.dict('sys.modules',{'platform':self.platform}):
            menu_input._sync_browser_value(self.game)
        self.assertEqual(self.game.user.nickname,'Dé nos')
