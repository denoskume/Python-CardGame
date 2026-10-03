"""Persistent player profiles and one-time welcome balance handling."""

import json
import os
import sys

_STORAGE_KEY = "python-cardgame-profiles-v1"
_DEFAULT_WELCOME_BALANCE = 30


def normalize_name(name):
    """Return a stable case-insensitive key for a player name or nickname."""
    return " ".join(str(name).strip().casefold().split())


def resolve_profile(registry, name, welcome_balance=_DEFAULT_WELCOME_BALANCE):
    """Return an existing profile or create one with the welcome balance once."""
    key = normalize_name(name)
    if not key:
        raise ValueError("A non-empty player name is required")

    existing = registry.get(key)
    if isinstance(existing, dict) and existing.get("welcome_granted"):
        return {
            "key": key,
            "balance": max(0, int(existing.get("balance", 0))),
            "welcome_granted_now": False,
        }

    registry[key] = {
        "display_name": str(name).strip(),
        "balance": int(welcome_balance),
        "welcome_granted": True,
    }
    return {
        "key": key,
        "balance": int(welcome_balance),
        "welcome_granted_now": True,
    }


def store_balance(registry, key, balance):
    """Update the persisted balance of an already registered player."""
    profile = registry.get(key)
    if not isinstance(profile, dict):
        return
    profile["balance"] = max(0, int(balance))
    profile["welcome_granted"] = True


def _browser_storage():
    if sys.platform != "emscripten":
        return None
    try:
        import platform
        return platform.window.localStorage
    except Exception:
        return None


def _profile_file(game):
    project_dir = os.path.dirname(os.path.dirname(__file__))
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "profiles.json")


def _load_registry(game):
    storage = _browser_storage()
    if storage is not None:
        try:
            raw = storage.getItem(_STORAGE_KEY)
            if raw:
                data = json.loads(str(raw))
                if isinstance(data, dict):
                    return data
        except Exception as exc:
            print(f"⚠ Browser profiles unavailable: {exc}")
        return {}

    try:
        path = _profile_file(game)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
                if isinstance(data, dict):
                    return data
    except Exception as exc:
        print(f"⚠ Player profiles unavailable: {exc}")
    return {}


def _save_registry(game):
    storage = _browser_storage()
    if storage is not None:
        try:
            storage.setItem(_STORAGE_KEY, json.dumps(game.player_profiles, ensure_ascii=False))
        except Exception as exc:
            print(f"⚠ Browser profile save failed: {exc}")
        return

    try:
        with open(_profile_file(game), "w", encoding="utf-8") as handle:
            json.dump(game.player_profiles, handle, ensure_ascii=False, indent=2)
    except Exception as exc:
        print(f"⚠ Player profile save failed: {exc}")


def install(game_module):
    """Attach persistent profile behavior to CardGame without changing game rules."""
    original_init = game_module.CardGame.__init__
    original_handle_menu_event = game_module.CardGame.handle_menu_event
    original_save_history = game_module.CardGame._save_history
    original_reset_game = game_module.CardGame.reset_game
    original_start_round = game_module.CardGame.start_round

    def init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.player_profiles = _load_registry(self)
        self.active_profile_key = None
        self.welcome_balance_granted_now = False

    def activate_profile(self):
        resolved = resolve_profile(
            self.player_profiles,
            self.user.name,
            welcome_balance=_DEFAULT_WELCOME_BALANCE,
        )
        self.active_profile_key = resolved["key"]
        self.user.balance = resolved["balance"]
        self.welcome_balance_granted_now = resolved["welcome_granted_now"]
        _save_registry(self)

    def handle_menu_event(self, event):
        previous_state = self.state
        original_handle_menu_event(self, event)
        if previous_state == game_module.STATE_MENU and self.state == game_module.STATE_BET:
            activate_profile(self)

    def save_history(self):
        original_save_history(self)
        if self.active_profile_key:
            store_balance(self.player_profiles, self.active_profile_key, self.user.balance)
            _save_registry(self)

    def reset_game(self):
        balance = self.user.balance
        original_reset_game(self)
        self.user.balance = balance
        self.welcome_balance_granted_now = False

    def start_round(self):
        self.welcome_balance_granted_now = False
        original_start_round(self)

    game_module.CardGame.__init__ = init
    game_module.CardGame.handle_menu_event = handle_menu_event
    game_module.CardGame._save_history = save_history
    game_module.CardGame.reset_game = reset_game
    game_module.CardGame.start_round = start_round
