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


def _font(path, size, bold=False):
    """Load the bundled font, falling back when SDL_ttf cannot render it."""
    try:
        font=pygame.font.Font(str(path),size)
        # Construction can succeed even when SDL_ttf later returns a NULL
        # glyph surface. Probe one glyph now so the fallback is deterministic.
        probe=font.render('A',True,TEXT)
        if probe.get_width()>0 and probe.get_height()>0:
            return font
    except (pygame.error, OSError, ValueError):
        pass

    font=pygame.font.Font(None,size)
    font.set_bold(bool(bold))
    return font


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
        fonts={name:_font(self.assets/('ui-bold.ttf' if bold else 'ui-regular.ttf'),px,bold)
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
