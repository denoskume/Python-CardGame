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
TEXT_SCALE_DESKTOP=1.40
TEXT_SCALE_COMPACT=1.30


class SmoothFallbackFont:
    """pygame.font-compatible fallback rendered at 2x then downsampled."""
    def __init__(self,size,bold=False,scale=2):
        self.target_size=max(1,int(size))
        self.scale=max(2,int(scale))
        self.source_size=self.target_size*self.scale
        self._font=pygame.font.Font(None,self.source_size)
        self._font.set_bold(bool(bold))

    def render(self,value,antialias,color,*args,**kwargs):
        surface=self._font.render(str(value),True,color,*args,**kwargs)
        width=max(1,round(surface.get_width()/self.scale))
        height=max(1,round(surface.get_height()/self.scale))
        return pygame.transform.smoothscale(surface,(width,height))

    def size(self,value):
        width,height=self._font.size(str(value))
        return max(1,round(width/self.scale)),max(1,round(height/self.scale))

    def get_linesize(self):
        return max(1,round(self._font.get_linesize()/self.scale))

    def set_bold(self,bold):
        self._font.set_bold(bool(bold))

    def get_bold(self):
        return self._font.get_bold()

    def __getattr__(self,name):
        return getattr(self._font,name)


def _font(path, size, bold=False):
    """Load the bundled font, falling back to supersampled text when needed."""
    try:
        font=pygame.font.Font(str(path),size)
        probe=font.render('A',True,TEXT)
        if probe.get_width()>0 and probe.get_height()>0:
            return font
    except (pygame.error, OSError, ValueError):
        pass

    return SmoothFallbackFont(size,bold)


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
        text_scale=TEXT_SCALE_COMPACT if compact else TEXT_SCALE_DESKTOP
        font_specs=[('hero',30 if compact else 48,True),('title',24 if compact else 32,True),
                    ('body',15 if compact else 18,False),('small',12 if compact else 14,False),
                    ('tiny',10 if compact else 12,True),('number',32 if compact else 46,True)]
        fonts={}
        for name,px,bold in font_specs:
            scaled_px=max(10,int(round(px*text_scale)))
            fonts[name]=_font(self.assets/('ui-bold.ttf' if bold else 'ui-regular.ttf'),scaled_px,bold)
        background=pygame.Surface(size)
        background.fill(BG)
        for x in range(-h,w,64):
            pygame.draw.line(background,(19,23,29),(x,0),(x+h,h))
        pygame.draw.line(background,LINE,(0,77),(w,77))
        resources={'fonts':fonts,'background':background,
                   'avatars':[pygame.transform.smoothscale(img,(48,48)) for img in self.avatar_sources]}
        self.cache={size:resources}
        return resources
