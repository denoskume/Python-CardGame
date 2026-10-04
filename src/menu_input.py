"""Menu input helpers for responsive desktop and browser typing."""

import sys
import json
from urllib.parse import unquote

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


def _install_browser_key_capture(field):
    """Stop field keystrokes reaching Pygbag while preserving native typing."""
    try:
        import platform

        if str(field.getAttribute("data-cardgame-keys") or "") == "1":
            return

        platform.window.eval(
            """
            (() => {
              const field = document.getElementById('cardgame-name-input');
              if (!field || field.getAttribute('data-cardgame-keys') === '1') return;
              field.setAttribute('data-cardgame-keys', '1');

              for (const eventName of ["keydown", "keyup", "keypress"]) {
                field.addEventListener(eventName, (event) => {
                  event.stopPropagation();
                });
              }

              field.addEventListener("input", (event) => {
                event.stopPropagation();
              });

              field.addEventListener("keydown", (event) => {
                if (event.key === "Enter") {
                  field.setAttribute("data-submit", "1");
                  field.blur();
                  event.stopPropagation();
                }
              });
            })();
            """
        )
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

        document = platform.window.document
        canvas = document.querySelector("canvas")
        if canvas is None:
            return None

        field = document.getElementById(_BROWSER_INPUT_ID)
        if field is None:
            field = document.createElement("input")
            field.id = _BROWSER_INPUT_ID
            field.type = "text"
            field.inputMode = "text"
            field.placeholder = "Tap here to type..."
            field.autocomplete = "off"
            field.spellcheck = False
            # Set through ASCII-only JSON to preserve Unicode across the WASM bridge.
            field.setAttribute("maxlength", str(game.player_name_max_len))
            document.body.appendChild(field)
            platform.window.eval("document.getElementById('cardgame-name-input').value = " + json.dumps(game.user.nickname))
            _install_browser_key_capture(field)

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
        style.setProperty("border", "2px solid #dfb970")
        style.setProperty("border-radius", "8px")
        style.setProperty("background", "#171c23", "important")
        style.setProperty("color", "#f1eee7", "important")
        style.setProperty("-webkit-text-fill-color", "#f1eee7", "important")
        style.setProperty("caret-color", "#f1eee7", "important")
        style.setProperty("opacity", "1", "important")
        style.setProperty("font-family", "Arial, sans-serif", "important")
        style.setProperty("font-size", "18px", "important")
        style.setProperty("font-weight", "700", "important")
        style.setProperty("line-height", f"{height}px", "important")
        style.setProperty("text-align", "left", "important")
        style.setProperty("text-shadow", "none", "important")
        style.setProperty("appearance", "none", "important")
        style.setProperty("-webkit-appearance", "none", "important")
        style.setProperty("outline", "none")

        _install_browser_key_capture(field)
        return field
    except Exception:
        return None


def _sync_browser_value(game):
    """Mirror native browser text into the game model without a popup."""
    field = _browser_field()
    if field is None:
        return
    try:
        import platform
        # The WASM proxy can decode raw DOM Unicode as Latin-1. Transfer ASCII escapes.
        encoded = platform.window.eval("encodeURIComponent(document.getElementById('cardgame-name-input').value)")
        value = unquote(str(encoded))[: game.player_name_max_len]
        if value != game.user.nickname:
            game.user.nickname = value
    except Exception:
        pass


def update_native_field(game):
    """Synchronize the native field outside rendering; Enter submits once."""
    _sync_browser_value(game)
    field = _ensure_browser_field(game)
    if field is not None and str(field.getAttribute('data-submit') or '') == '1':
        field.removeAttribute('data-submit')
        game.activate('continue')
