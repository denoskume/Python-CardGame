"""Cached, portable typography and visual resources."""
from pathlib import Path
import pygame

BG=(15,18,23)
PANEL=(23,28,35)
LINE=(44,51,62)
TEXT=(241,238,231)
MUTED=(153,163,177)
RED=(199,54,71)
GREEN=(105,211,170)
GOLD=(223,185,112)


class ThemeResources:
    def __init__(self):
        self.cache={}
        self.assets=Path(__file__).parent/'assets'
        self.avatar_sources=[pygame.image.load(str(self.assets/f'avatar{i}.png')) for i in (1,2,3)]

    def for_size(self,size):
        if size in self.cache:
            return self.cache[size]
        w,h=size
        compact=w<600 or h<500
        fonts={name:pygame.font.Font(str(self.assets/('ui-bold.ttf' if bold else 'ui-regular.ttf')),px)
               for name,px,bold in [('hero',30 if compact else 48,True),('title',24 if compact else 32,True),
                                   ('body',15 if compact else 18,False),('small',12 if compact else 14,False),
                                   ('tiny',10 if compact else 12,True),('number',32 if compact else 46,True)]}
        background=pygame.Surface(size)
        background.fill(BG)
        # Subtle table lines add depth without competing with moving cards.
        for x in range(-h,w,64):
            pygame.draw.line(background,(19,23,29),(x,0),(x+h,h))
        pygame.draw.line(background,LINE,(0,77),(w,77))
        resources={'fonts':fonts,'background':background,
                   'avatars':[pygame.transform.smoothscale(img,(48,48)) for img in self.avatar_sources]}
        self.cache={size:resources}
        return resources
