"""Validated local storage with atomic desktop writes and browser adapters."""
import copy
import json
import math
import os
import sys
import tempfile
from pathlib import Path


def normalize_name(name):
    return ' '.join(str(name).strip().casefold().split())


def resolve_profile(registry, name, welcome_balance=30):
    key = normalize_name(name)
    if not key:
        raise ValueError('A player name is required')
    created = key not in registry
    previous = registry.get(key)
    balance = previous.get('balance', 0) if isinstance(previous, dict) else 0
    balance = balance if type(balance) is int and balance >= 0 else 0
    registry[key] = {'display_name': str(name).strip(), 'balance': welcome_balance if created else balance,
                     'welcome_granted': True}
    return {'key': key, 'balance': registry[key]['balance'], 'welcome_granted_now': created}


class UnavailableBrowserStorage:
    def getItem(self, key):
        raise RuntimeError('Browser storage is unavailable')

    def setItem(self, key, value):
        raise RuntimeError('Browser storage is unavailable')


def browser_storage():
    if sys.platform != 'emscripten':
        return None
    try:
        import platform
        return platform.window.localStorage or UnavailableBrowserStorage()
    except Exception:
        return UnavailableBrowserStorage()


class Storage:
    KEYS = {'history': 'python-cardgame-history-v1', 'profiles': 'python-cardgame-profiles-v1',
            'settings': 'python-cardgame-settings-v2'}

    def __init__(self, data_dir: Path, browser_storage=None):
        self.data_dir = Path(data_dir)
        self.browser = browser_storage
        self.last_error = None
        self.memory = {}

    def _load(self, name, default):
        try:
            if self.browser is not None:
                raw = self.browser.getItem(self.KEYS[name])
                value = json.loads(str(raw)) if raw else default
            else:
                path = self.data_dir / (name + '.json')
                value = json.loads(path.read_text(encoding='utf-8')) if path.exists() else default
            self.memory[name] = copy.deepcopy(value)
            return value
        except Exception:
            self.last_error = 'Saving is unavailable. Progress stays in this session only.'
            return copy.deepcopy(self.memory.get(name, default))

    def _save(self, name, value):
        self.memory[name] = copy.deepcopy(value)
        temporary = None
        try:
            data = json.dumps(value, ensure_ascii=True, allow_nan=False)
            if self.browser is not None:
                self.browser.setItem(self.KEYS[name], data)
            else:
                self.data_dir.mkdir(parents=True, exist_ok=True)
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=self.data_dir, delete=False) as handle:
                    temporary = handle.name
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, self.data_dir / (name + '.json'))
            self.last_error = None
            return True
        except Exception:
            self.last_error = 'Saving is unavailable. Progress stays in this session only.'
            return False
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)

    def load_history(self):
        value = self._load('history', [])
        if not isinstance(value, list):
            return []
        valid = []
        for row in value:
            if not isinstance(row, dict) or row.get('result') not in ('WIN', 'LOSE'):
                continue
            if not all(type(row.get(key)) is int and row[key] >= 0 for key in ('stake', 'balance_after', 'round')):
                continue
            if not isinstance(row.get('player'), str):
                continue
            if not all(type(row.get(key)) in (int, float) and 0 <= row[key] <= 1e15 for key in ('duration', 'timestamp')):
                continue
            if 'bet' in row and (type(row['bet']) is not int or row['bet'] < 0):
                continue
            if 'mult' in row and (type(row['mult']) is not int or row['mult'] not in (1,2,3)):
                continue
            valid.append(row)
        return valid[-200:]

    def save_history(self, rows):
        return self._save('history', rows[-200:])

    def load_profiles(self):
        value = self._load('profiles', {})
        if not isinstance(value, dict):
            return {}
        registry = {}
        for name, profile in value.items():
            if not normalize_name(name):
                continue
            balance = profile.get('balance', 0) if isinstance(profile, dict) else 0
            registry[normalize_name(name)] = {'display_name': name, 'welcome_granted': True,
                                            'balance': balance if type(balance) is int and balance >= 0 else 0}
        return registry

    def save_profiles(self, registry):
        return self._save('profiles', registry)

    def load_settings(self):
        value = self._load('settings', {})
        return value if isinstance(value, dict) else {}

    def save_settings(self, settings):
        return self._save('settings', settings)
