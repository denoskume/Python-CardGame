"""Application entry point for Rouge Gagne, Noir Perd."""

import asyncio
import os
import sys
from pathlib import Path

_wslg_pulse = Path("/mnt/wslg/PulseServer")
if _wslg_pulse.exists():
    os.environ.setdefault("PULSE_SERVER", "unix:/mnt/wslg/PulseServer")
    os.environ.setdefault("SDL_AUDIODRIVER", "pulseaudio")

import pygame
import user as us
import bet as bt
import game as gm
def _browser_viewport():
    """Return the current browser viewport when running through Pygbag."""
    if sys.platform != "emscripten":
        return None
    try:
        import platform
        width = int(platform.window.innerWidth)
        height = int(platform.window.innerHeight)
        return max(320, width), max(300, height)
    except Exception:
        return None


def _initial_size():
    """Choose a useful first window size for desktop and browser devices."""
    viewport = _browser_viewport()
    if viewport is not None:
        return viewport
    return 960, 630


async def main() -> None:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.display.init()
    pygame.font.init()

    pygame.display.set_caption("Rouge gagne, Noir perd")
    screen = pygame.display.set_mode(_initial_size(), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    player = us.User(nickname="", avatar_index=0, initial_balance=30)
    betting = bt.Bet(min_amount=10, max_amount=1000, amount=10, turbo=1)
    card_game = gm.CardGame(screen, player, betting)

    if sys.platform == "emscripten":
        import platform
        loading = platform.window.document.getElementById('cardgame-loading')
        if loading is not None:
            loading.remove()
    running = True
    last_browser_size = screen.get_size()

    while running and card_game.running:
        browser_size = _browser_viewport()
        if browser_size is not None and browser_size != last_browser_size:
            screen = pygame.display.set_mode(browser_size, pygame.RESIZABLE)
            card_game.screen = screen
            card_game.resize(screen.get_size())
            last_browser_size = browser_size

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width = max(320, event.w)
                height = max(300, event.h)
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                card_game.screen = screen
                card_game.resize(screen.get_size())
                last_browser_size = screen.get_size()
            else:
                card_game.handle_event(event)

        card_game.update()
        card_game.draw()
        pygame.display.flip()
        if sys.platform != "emscripten":
            clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
