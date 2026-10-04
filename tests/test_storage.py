import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path('src').resolve()))

class BrowserStore:
    def __init__(self): self.values = {}
    def getItem(self, key): return self.values.get(key)
    def setItem(self, key, value): self.values[key] = value

class BrokenStore:
    def getItem(self, key): raise RuntimeError('denied')
    def setItem(self, key, value): raise RuntimeError('quota')

class StorageTests(unittest.TestCase):
    def setUp(self):
        import storage
        self.module = storage
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.store = storage.Storage(self.path)

    def row(self, n=1):
        return dict(round=n, player='Denos', result='WIN', stake=10, balance_after=40,
                    duration=20, timestamp=1000, bet=10, mult=1, chosen_index=0, red_index=0)

    def test_history_bound_and_bad_row(self):
        self.store.save_history([self.row(n) for n in range(201)])
        rows = self.store.load_history()
        self.assertEqual((len(rows), rows[0]['round']), (200, 1))
        (self.path/'history.json').write_text(json.dumps([self.row(), {'stake':'oops'}, self.row(2)]))
        self.assertEqual(len(self.store.load_history()), 2)
        self.assertNotIn('difficulty', self.store.load_history()[0])

    def test_profiles_keep_bonus_and_balance(self):
        registry = {}
        first = self.module.resolve_profile(registry, '  Denos Kume ')
        registry[first['key']]['balance'] = 12
        self.store.save_profiles(registry)
        second = self.module.resolve_profile(self.store.load_profiles(), 'denos   kume')
        self.assertEqual(second['balance'], 12)
        self.assertFalse(second['welcome_granted_now'])

    def test_corrupt_known_profile_gets_no_second_bonus(self):
        (self.path/'profiles.json').write_text(json.dumps({'denos': {'balance': 'bad', 'welcome_granted': True}}))
        result = self.module.resolve_profile(self.store.load_profiles(), 'Denos')
        self.assertEqual(result['balance'], 0)
        self.assertFalse(result['welcome_granted_now'])

    def test_browser_denial_preserves_memory(self):
        store = self.module.Storage(self.path, BrokenStore())
        self.assertEqual(store.load_history(), [])
        self.assertFalse(store.save_history([self.row()]))
        self.assertEqual(len(store.load_history()), 1)
        self.assertIsNotNone(store.last_error)
        self.assertFalse((self.path/'history.json').exists())

    def test_browser_existing_keys(self):
        browser = BrowserStore()
        store = self.module.Storage(self.path, browser)
        store.save_history([self.row()])
        store.save_profiles({'denos': {'balance': 12, 'welcome_granted': True}})
        self.assertIn('python-cardgame-history-v1', browser.values)
        self.assertIn('python-cardgame-profiles-v1', browser.values)

    def test_atomic_failure_preserves_previous_file(self):
        self.store.save_history([self.row(1)])
        with patch('os.replace', side_effect=OSError('disk')):
            self.assertFalse(self.store.save_history([self.row(2)]))
        self.assertEqual(json.loads((self.path/'history.json').read_text())[0]['round'], 1)

    def test_malformed_consumed_fields_and_huge_time_are_skipped(self):
        bad=self.row();bad['bet']={}
        huge=self.row();huge['timestamp']=10**1000
        (self.path/'history.json').write_text(json.dumps([bad,huge,self.row(3)]))
        self.assertEqual([row['round'] for row in self.store.load_history()],[3])

    def test_unicode_survives_wasm_storage_bridge(self):
        class WasmStore(BrowserStore):
            def setItem(self,key,value):
                super().setItem(key,value.encode('utf-8').decode('latin-1'))
        browser=WasmStore()
        store=self.module.Storage(self.path,browser)
        registry={'dé nos':{'display_name':'Dé nos','balance':30,'welcome_granted':True}}
        store.save_profiles(registry)
        decoded=json.loads(browser.values['python-cardgame-profiles-v1'])
        self.assertIn('dé nos',decoded)
