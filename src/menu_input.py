"""Menu input helpers for responsive desktop and browser typing."""

import sys

import pygame

_BROWSER_INPUT_ID = "cardgame-name-input"


def _browser_field():
    """Return the inline browser input when running through Pygbag."""
    if sys.platform != "emscripten":
        return None
    try:
        import platform
        return platform.window.document.getElementById(_BROWSER_INPUT_ID)
    except Exception:
        return None


def _remove_browser_field():
    """Remove the web-only input when the menu is no longer visible."""
    field = _browser_field()
    if field is None:
        return
    try:
        field.remove()
    except Exception:
        pass


def _ensure_browser_field(game):
    """Overlay a real HTML input exactly on the responsive Pygame name field."""
    if sys.platform != "emscripten":
        return None

    input_rect = getattr(game, "name_input_rect", None)
    if input_rect is None:
        return None

    try:
        import platform

        window = platform.window
        document = window.document
        canvas = document.querySelector("canvas")
        if canvas is None:
            return None

        field = document.getElementById(_BROWSER_INPUT_ID)
        if field is None:
            field = document.createElement("input")
            field.id = _BROWSER_INPUT_ID
            field.type = "text"
            field.placeholder = "Tap here to type..."
            field.autocomplete = "off"
            field.spellcheck = False
            field.value = game.user.nickname
            field.setAttribute("maxlength", str(game.player_name_max_len))
            document.body.appendChild(field)

        canvas_rect = canvas.getBoundingClientRect()
        scale_x = canvas_rect.width / max(1, game.w)
        scale_y = canvas_rect.height / max(1, game.h)
        left = canvas_rect.left + input_rect.x * scale_x
        top = canvas_rect.top + input_rect.y * scale_y
        width = input_rect.width * scale_x
        height = input_rect.height * scale_y

        style = field.style
        style.setProperty("position", "fixed")
        style.setProperty("left", f"{left}px")
        style.setProperty("top", f"{top}px")
        style.setProperty("width", f"{width}px")
        style.setProperty("height", f"{height}px")
        style.setProperty("box-sizing", "border-box")
        style.setProperty("z-index", "10000")
        style.setProperty("margin", "0")
        style.setProperty("padding", "0 12px")
        style.setProperty("border", "2px solid #111")
        style.setProperty("border-radius", "8px")
        style.setProperty("background", "#ffffff")
        style.setProperty("color", "#111111")
        style.setProperty("font", "700 18px Arial, sans-serif")
        style.setProperty("outline", "none")

        return field
    except Exception:
        return None


def _sync_browser_value(game):
    """Mirror native browser text into the game model without a popup."""
    field = _browser_field()
    if field is None:
        return
    try:
        value = str(field.value)[: game.player_name_max_len]
        if value != game.user.nickname:
            game.user.nickname = value
    except Exception:
        pass


def install(game_module):
    """Patch CardGame so browser typing happens directly in the visible field."""
    original_handle_menu_event = game_module.CardGame.handle_menu_event
    original_draw = game_module.CardGame.draw

    def handle_menu_event(self, event):
        _sync_browser_value(self)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            input_rect = getattr(self, "name_input_rect", None)
            if input_rect is not None and input_rect.collidepoint(event.pos):
                self.active_input = True
                field = _ensure_browser_field(self)
                if field is not None:
                    try:
                        field.focus()
                    except Exception:
                        pass
                    return
                try:
                    pygame.key.start_text_input()
                except Exception:
                    pass

        original_handle_menu_event(self, event)

        if not self.active_input:
            try:
                pygame.key.stop_text_input()
            except Exception:
                pass

    def draw(self):
        _sync_browser_value(self)
        original_draw(self)
        if self.state == game_module.STATE_MENU:
            _ensure_browser_field(self)
        else:
            _remove_browser_field()

    game_module.CardGame.handle_menu_event = handle_menu_event
    game_module.CardGame.draw = draw
