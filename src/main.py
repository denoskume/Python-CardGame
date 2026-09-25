"""Application entry point for Rouge Gagne, Noir Perd.

This module configures platform-specific audio, initializes Pygame,
creates the domain objects, and runs the event/update/render loop.
"""

import os
from pathlib import Path

# WSLg exposes Windows audio through a PulseAudio socket.
# Configure SDL before importing/initializing pygame so the mixer uses it.
_wslg_pulse = Path("/mnt/wslg/PulseServer")
if _wslg_pulse.exists():
    os.environ.setdefault("PULSE_SERVER", "unix:/mnt/wslg/PulseServer")
    os.environ.setdefault("SDL_AUDIODRIVER", "pulseaudio")

import pygame
import user as us
import bet as bt
import game as gm
import dashboard as db

def main():
    """Initialize Pygame, create game objects, and run the main loop."""
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    # Ensure the mixer is connected to the selected SDL audio backend.
    if pygame.mixer.get_init() is None:
        try:
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512,
            )
        except pygame.error as e:
            print(f"⚠ Audio unavailable; continuing without sound: {e}")
    else:
        print(
            "✓ Audio initialized:",
            pygame.mixer.get_init(),
            "| driver:",
            os.environ.get("SDL_AUDIODRIVER", "auto"),
            "| server:",
            os.environ.get("PULSE_SERVER", "default"),
        )
    pygame.display.set_caption("Rouge gagne, Noir perd")
    screen = pygame.display.set_mode((960, 630))
    clock = pygame.time.Clock()

    # Domain objects hold player and betting state independently of rendering.
    player = us.User(nickname="", avatar_index=0, initial_balance=30)
    betting = bt.Bet(min_amount=10, max_amount=100, amount=10, turbo=1)

    # CardGame coordinates state transitions, timers, gameplay, and persistence.
    card_game = gm.CardGame(screen, player, betting)

    running = True
    while running:
        # Process input first, then update the active state and render one frame.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                card_game.handle_event(event)
        card_game.update()
        card_game.draw()
        pygame.display.flip()
        clock.tick(60) 

    pygame.quit()

if __name__ == "__main__":
    main()




