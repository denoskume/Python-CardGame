"""Menu input helpers for responsive desktop and browser typing."""

import sys

import pygame


def _browser_name_prompt(current_name, max_len):
    """Use a native browser prompt so mobile devices open the software keyboard."""
    if sys.platform != "emscripten":
        return None
    try:
        import platform
        value = platform.window.prompt("Enter your nickname or name", current_name)
        if value is None:
            return current_name
        return str(value).strip()[:max_len]
    except Exception:
        return current_name


def install(game_module):
    """Patch CardGame menu input without changing the rest of the state machine."""
    original_handle_menu_event = game_module.CardGame.handle_menu_event

    def handle_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            input_rect = getattr(self, "name_input_rect", None)
            if input_rect is not None and input_rect.collidepoint(event.pos):
                self.active_input = True
                try:
                    pygame.key.start_text_input()
                except Exception:
                    pass

                browser_value = _browser_name_prompt(self.user.nickname, self.player_name_max_len)
                if browser_value is not None:
                    self.user.nickname = browser_value
                return

        original_handle_menu_event(self, event)

        if not self.active_input:
            try:
                pygame.key.stop_text_input()
            except Exception:
                pass

    game_module.CardGame.handle_menu_event = handle_menu_event
