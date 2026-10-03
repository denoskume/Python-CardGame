"""Browser persistence for CardGame history while preserving desktop JSON storage."""

import json
import sys

_STORAGE_KEY = "python-cardgame-history-v1"


def install(game_module):
    """Use browser localStorage for CardGame history on Pygbag only."""
    original_load = game_module.CardGame._load_history
    original_save = game_module.CardGame._save_history

    def _browser_storage():
        if sys.platform != "emscripten":
            return None
        try:
            import platform
            return platform.window.localStorage
        except Exception:
            return None

    def load_history(self):
        storage = _browser_storage()
        if storage is None:
            return original_load(self)
        try:
            raw = storage.getItem(_STORAGE_KEY)
            if raw:
                data = json.loads(str(raw))
                if isinstance(data, list):
                    return data[-200:]
        except Exception as exc:
            print(f"⚠ Browser history unavailable: {exc}")
        return []

    def save_history(self):
        storage = _browser_storage()
        if storage is None:
            return original_save(self)
        try:
            self.global_history = self.global_history[-200:]
            storage.setItem(_STORAGE_KEY, json.dumps(self.global_history, ensure_ascii=False))
        except Exception as exc:
            print(f"⚠ Browser history save failed: {exc}")

    game_module.CardGame._load_history = load_history
    game_module.CardGame._save_history = save_history
