"""Explicit round controller shared by desktop and browser."""
import math
import random
import sys
import time
from pathlib import Path
import pygame
from bet import Bet
from user import User
from storage import Storage, browser_storage, resolve_profile
from settings import Settings, shuffle_timing
from layout import compute_layout
from theme import ThemeResources
import dashboard
import menu_input

STATE_START = 'START_SCREEN'
STATE_MENU = 'MENU'
STATE_BET = 'BET_SETUP'
STATE_SHOW_BACKS = 'SHOW_BACKS'
STATE_SHUFFLE = 'SHUFFLE'
STATE_CHOOSE = 'CHOOSE'
STATE_RESULT = 'RESULT'
STATE_GAME_OVER = 'GAME_OVER'
STATE_PAUSE = 'PAUSE'
ACTIVE_STATES = (STATE_SHOW_BACKS, STATE_SHUFFLE, STATE_CHOOSE)


class Card:
    def __init__(self, rect, is_red, **images):
        self.rect, self.is_red = rect, is_red
        self.slot = 0
        self.face = 'BACK'


class CardGame:
    def __init__(self, screen, user: User, bet: Bet, storage=None):
        self.screen = screen
        self.w, self.h = screen.get_size()
        self.user, self.bet = user, bet
        self.storage = storage or Storage(Path(__file__).resolve().parent.parent / 'data', browser_storage())
        self.global_history = self._load_history()
        self.player_profiles = self.storage.load_profiles()
        self.settings = Settings.from_dict(self.storage.load_settings())
        self.storage_notice = self.storage.last_error
        self.active_profile_key = None
        self.welcome_balance_granted_now = False
        self.state = STATE_START
        self.overlay_return = STATE_START
        self.state_before_pause = None
        self.pause_start = 0
        self.state_start_time = 0
        self.current_round_start_time = None
        self.round_history = []
        self.total_time_played = 0
        self.round_result = None
        self.round_difficulty = self.settings.difficulty
        self.selected_card_index = None
        self.selected_card_rect = None
        self.cards = []
        self.card_width, self.card_height, self.card_gap, self.card_area_y = 180,250,60,260
        self.card_img_front = self.card_img_back_red = self.card_img_back_black = None
        self.is_swapping = False
        self.swap_i, self.swap_j = 0,1
        self.swap_start_time = self.last_shuffle_swap = 0
        self.swap_slots = (0,1)
        self.shuffle_interval, self.swap_duration = shuffle_timing(self.settings.difficulty,0)
        self.consecutive_wins = 0
        self.player_name_max_len = 20
        self.active_input = False
        self.focus_action = None
        self.hover_action = None
        self.message = ''
        self.running = True
        self.audio_attempted = False
        self.snd_shuffle = self.snd_win = self.snd_lose = None
        self.shuffle_channel = self.result_channel = None
        self.theme = ThemeResources()
        self.resources = self.theme.for_size((self.w,self.h))
        self.layout = compute_layout((self.w,self.h),self.state)
        self.name_input_rect = None


    def _load_history(self):
        return self.storage.load_history()

    def _save_history(self):
        self.storage.save_history(self.global_history)
        error = self.storage.last_error
        if self.active_profile_key:
            self.player_profiles[self.active_profile_key]['balance'] = self.user.balance
            self.storage.save_profiles(self.player_profiles)
        self.storage_notice = error or self.storage.last_error

    def activate_profile(self):
        self.consecutive_wins = 0
        result = resolve_profile(self.player_profiles, self.user.name)
        self.active_profile_key = result['key']
        self.user.balance = result['balance']
        self.welcome_balance_granted_now = result['welcome_granted_now']
        self.storage.save_profiles(self.player_profiles)
        self.storage_notice = self.storage.last_error
        self.round_history.clear()
        self.total_time_played = 0

    def apply_settings(self, settings: Settings) -> None:
        if self.settings.difficulty != settings.difficulty:
            self.consecutive_wins = 0
        self.settings = settings
        self.storage.save_settings(settings.to_dict())
        self.storage_notice = self.storage.last_error
        if not settings.sound_enabled and pygame.mixer.get_init():
            pygame.mixer.stop()

    def enable_audio(self):
        if self.audio_attempted or not self.settings.sound_enabled:
            return
        self.audio_attempted = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            assets = Path(__file__).parent / 'assets'
            extension = '.ogg' if __import__('sys').platform == 'emscripten' else '.mp3'
            self.snd_shuffle = pygame.mixer.Sound(str(assets / ('shuffle' + extension)))
            self.snd_win = pygame.mixer.Sound(str(assets / ('win' + extension)))
            self.snd_lose = pygame.mixer.Sound(str(assets / ('lose' + extension)))
            self.shuffle_channel = pygame.mixer.Channel(1)
            self.result_channel = pygame.mixer.Channel(2)
        except (pygame.error, OSError):
            self.shuffle_channel = self.result_channel = None

    def play_sound(self, name):
        if not self.settings.sound_enabled:
            return
        sound = getattr(self, 'snd_' + name, None)
        channel = self.shuffle_channel if name == 'shuffle' else self.result_channel
        if sound is not None and channel is not None:
            channel.set_volume(self.settings.volume)
            channel.play(sound, maxtime=self.swap_duration if name == 'shuffle' else 0)

    def start_round(self):
        """Create three cards, choose the red card, and start observation."""
        if not self.bet.is_valid(self.user.balance):
            return
        self.round_difficulty = self.settings.difficulty
        self.shuffle_interval, self.swap_duration = shuffle_timing(self.round_difficulty, self.consecutive_wins)
        self.round_stake = self.bet.stake()
        self.round_bet = self.bet.amount
        self.round_multiplier = self.bet.turbo
        # Compute three evenly spaced card slots centered in the game window.
        total_width = 3 * self.card_width + 2 * self.card_gap
        start_x = (self.w - total_width) // 2

        cards_positions = []
        for idx in range(3):
            x = start_x + idx * (self.card_width + self.card_gap)
            rect = pygame.Rect(x, self.card_area_y, self.card_width, self.card_height)
            cards_positions.append(rect)

        # Card identity stays attached to the object while positions are shuffled.
        red_index = random.randint(0, 2)

        self.cards = []
        for idx in range(3):
            is_red = (idx == red_index)
            card = Card(
                cards_positions[idx],
                is_red,
                img_front=self.card_img_front,
                img_back_red=self.card_img_back_red,
                img_back_black=self.card_img_back_black
            )
            card.face = "BACK"
            card.slot = idx
            self.cards.append(card)

        self.selected_card_index = None
        self.selected_card_rect = None
        self.round_result = None
        self.current_round_start_time = pygame.time.get_ticks()

        self.message = "Watch carefully! Colors are visible for 10 seconds..."
        self.state = STATE_SHOW_BACKS
        self.state_start_time = pygame.time.get_ticks()
        self.last_shuffle_swap = self.state_start_time
        self.is_swapping = False
        self.resize((self.w, self.h))

    def update_show_backs(self):
        """Advance to shuffling after the 10-second observation period."""
        elapsed = pygame.time.get_ticks() - self.state_start_time
        if elapsed >= 10_000:
            for c in self.cards:
                c.face = "FRONT"
            self.state = STATE_SHUFFLE
            self.state_start_time = pygame.time.get_ticks()
            self.last_shuffle_swap = self.state_start_time
            self.is_swapping = False
            self.message = "Shuffling... try to follow the red card!"

    def update_shuffle(self):
        """Animate random pair swaps and transition to card selection."""
        now = pygame.time.get_ticks()
        elapsed = now - self.state_start_time

        if self.is_swapping:
            progress = min(1, (now - self.swap_start_time) / self.swap_duration)
            self._position_swap(progress)
            if progress >= 1:
                self.cards[self.swap_i].slot, self.cards[self.swap_j].slot = self.swap_slots[1], self.swap_slots[0]
                self.is_swapping = False
                self.last_shuffle_swap = now
        elif now - self.last_shuffle_swap >= self.shuffle_interval and elapsed < 10_000:
            self.swap_two_cards()

        if elapsed >= 10_000:
            if self.is_swapping:
                self._position_swap(1)
                self.cards[self.swap_i].slot, self.cards[self.swap_j].slot = self.swap_slots[1], self.swap_slots[0]
                self.is_swapping = False

            if self.shuffle_channel is not None and self.shuffle_channel.get_busy():
                self.shuffle_channel.fadeout(150)

            self.state = STATE_CHOOSE
            self.state_start_time = pygame.time.get_ticks()
            self.message = "Click on the red card! You have 10 seconds."

    def swap_two_cards(self):
        """Start a non-blocking interpolation between two random card slots."""
        if self.is_swapping:
            return

        i, j = random.sample(range(3), 2)
        self.swap_i = i
        self.swap_j = j
        self.swap_start_time = pygame.time.get_ticks()
        self.is_swapping = True
        self.swap_slots = (self.cards[i].slot, self.cards[j].slot)

        self.play_sound('shuffle')

        self.swap_rect_i_start = self.cards[i].rect.copy()
        self.swap_rect_j_start = self.cards[j].rect.copy()
        self.swap_rect_i_end = self.cards[j].rect.copy()
        self.swap_rect_j_end = self.cards[i].rect.copy()

    def resize(self, size):
        self.w, self.h = size
        self.layout = compute_layout(size, self.state)
        self.resources = self.theme.for_size(size)
        self.name_input_rect = self.layout.get('name_input')
        for card in self.cards:
            card.rect = self.layout['card_' + str(card.slot)].copy()
        if self.is_swapping:
            now = self.pause_start if self.state == STATE_PAUSE else pygame.time.get_ticks()
            self._position_swap(min(1, (now - self.swap_start_time) / self.swap_duration))

    def _position_swap(self, progress):
        first, second = (self.layout['card_' + str(slot)] for slot in self.swap_slots)
        eased = progress * progress * (3 - 2 * progress)
        arc = math.sin(math.pi * progress) * min(36, self.h * .05)
        for idx, start, end, direction in [(self.swap_i, first, second, -1), (self.swap_j, second, first, 1)]:
            rect = start.copy()
            rect.x = round(start.x + (end.x-start.x)*eased)
            rect.y = round(start.y + arc*direction)
            self.cards[idx].rect = rect

    def pause(self, now_ms):
        if self.state not in (STATE_SHOW_BACKS, STATE_SHUFFLE, STATE_CHOOSE):
            return
        self.state_before_pause = self.state
        self.pause_start = now_ms
        self.state = STATE_PAUSE
        if pygame.mixer.get_init():
            pygame.mixer.pause()

    def resume(self, now_ms):
        if self.state != STATE_PAUSE or self.state_before_pause is None:
            return
        duration = now_ms - self.pause_start
        self.state_start_time += duration
        if self.current_round_start_time is not None:
            self.current_round_start_time += duration
        self.swap_start_time += duration
        self.last_shuffle_swap += duration
        self.state = self.state_before_pause
        self.state_before_pause = None
        if pygame.mixer.get_init():
            pygame.mixer.unpause()

    def resolve_round(self, index):
        """Resolve win/loss, update balance, persist the round, and choose the next state."""
        if self.state != STATE_CHOOSE or self.round_result is not None:
            return
        if index is not None and (type(index) is not int or not 0 <= index < len(self.cards)):
            return
        if pygame.time.get_ticks() - self.state_start_time >= 10_000:
            index = None
        self.selected_card_index = index
        self.selected_card_rect = self.cards[index].rect.copy() if index is not None else None
        for c in self.cards:
            c.face = "BACK"

        now = pygame.time.get_ticks()
        if self.current_round_start_time is not None:
            duration_sec = (now - self.current_round_start_time) / 1000.0
        else:
            duration_sec = 0.0
        self.total_time_played += duration_sec

        mult = self.round_multiplier
        stake = self.round_stake

        # find red card index
        red_index = None
        for idx, c in enumerate(self.cards):
            if c.is_red:
                red_index = idx
                break

        if index is None:
            
            # ---------- TIMEOUT = LOSE ----------
            self.round_result = "LOSE"
            self.selected_card_index = None
            self.selected_card_rect = None

            loss = self.user.apply_loss(stake)   # balance -= stake
            self.message = f"Time's up! You lose {loss}$ (x{mult})."

            self.play_sound('lose')

        else:
            chosen = self.cards[index]
            if chosen.is_red:
                # ---------- WIN ----------
                self.round_result = "WIN"

                profit = self.user.apply_win(stake)  # balance += stake
                self.message = f"Well done! Red card! Profit: +{profit}$ (x{mult})."

                self.play_sound('win')

            else:
                # ---------- LOSE ----------
                self.round_result = "LOSE"

                loss = self.user.apply_loss(stake)   # balance -= stake
                self.message = f"Missed it, that wasn't the red card. Loss: {loss}$ (x{mult})."

                self.play_sound('lose')

        if self.user.balance < 0:
            self.user.balance = 0

        round_entry = {
            "round": len(self.round_history) + 1,
            "bet": self.round_bet,
            "mult": mult,
            "stake": stake,
            "result": self.round_result,
            "chosen_index": index,
            "red_index": red_index,
            "duration": round(duration_sec, 2),
            "balance_after": self.user.balance,
            "timestamp": time.time(),
            "player": self.user.name or ""
        }
        round_entry["timeout"] = index is None
        round_entry["difficulty"] = self.round_difficulty
        self.consecutive_wins = self.consecutive_wins + 1 if self.round_result == "WIN" else 0
        self.round_history.append(round_entry)

        self.global_history.append(round_entry)
        if len(self.global_history) > 200:
            self.global_history = self.global_history[-200:]

        self._save_history()

        if self.user.balance < self.bet.min:
            self.state = STATE_GAME_OVER
        else:
            self.state = STATE_RESULT

        self.state_start_time = pygame.time.get_ticks()
    def set_state(self, state):
        self.state = state
        self.focus_action = None
        self.hover_action = None
        self.resize((self.w,self.h))
        if state != STATE_MENU:
            self.active_input = False
            pygame.key.stop_text_input()
            menu_input._remove_browser_field()

    def reset_game(self):
        self.bet.amount, self.bet.turbo = 10,1
        self.selected_card_index = None
        self.selected_card_rect = None
        self.round_result = None
        self.round_history.clear()
        self.total_time_played = 0
        self.welcome_balance_granted_now = False
        self.consecutive_wins = 0
        self.cards = []
        self.is_swapping = False

    def enabled(self, action):
        if action == 'continue':
            return 3 <= len(self.user.name) <= self.player_name_max_len
        if action == 'start':
            return self.bet.is_valid(self.user.balance)
        if action.startswith('turbo_'):
            return self.bet.amount * int(action[-1]) <= self.user.balance
        if action == 'plus':
            return (self.bet.amount+5)*self.bet.turbo <= self.user.balance and self.bet.amount+5 <= self.bet.max
        if action == 'minus':
            return self.bet.amount > self.bet.min
        return True

    def activate(self, action):
        if not self.enabled(action):
            return
        if action == 'play':
            self.set_state(STATE_MENU)
        elif action in ('help','settings'):
            self.overlay_return = self.state
            self.set_state(action.upper())
        elif action == 'back':
            self.set_state(self.overlay_return if self.state in ('HELP','SETTINGS') else STATE_START)
        elif action.startswith('avatar_'):
            self.user.avatar_index = int(action[-1])
        elif action == 'continue':
            self.activate_profile()
            self.set_state(STATE_BET if self.user.balance >= self.bet.min else STATE_GAME_OVER)
        elif action == 'menu':
            self.reset_game()
            self.set_state(STATE_MENU)
        elif action in ('easy','normal','expert'):
            self.apply_settings(Settings(action,self.settings.sound_enabled,self.settings.volume))
        elif action == 'sound':
            self.apply_settings(Settings(self.settings.difficulty,not self.settings.sound_enabled,self.settings.volume))
            self.enable_audio()
        elif action in ('volume_down','volume_up'):
            change = .1 if action == 'volume_up' else -.1
            self.apply_settings(Settings(self.settings.difficulty,self.settings.sound_enabled,round(self.settings.volume+change,1)))
        elif action.startswith('turbo_'):
            self.bet.set_turbo(int(action[-1]))
        elif action == 'minus':
            self.bet.decrease()
        elif action == 'plus':
            self.bet.increase(balance=self.user.balance//self.bet.turbo)
        elif action == 'start':
            self.start_round()
            self.set_state(self.state)
        elif action == 'next':
            self.bet.amount,self.bet.turbo=10,1
            self.set_state(STATE_BET)
        elif action == 'pause':
            self.pause(pygame.time.get_ticks())
            self.set_state(self.state)
        elif action == 'resume':
            self.resume(pygame.time.get_ticks())
            self.set_state(self.state)
        elif action == 'quit':
            if sys.platform == 'emscripten':
                self.reset_game()
                self.set_state(STATE_START)
            else:
                self.running=False

    def _click(self, pos):
        if self.state == STATE_MENU and self.name_input_rect and self.name_input_rect.collidepoint(pos):
            self.active_input = True
            self.focus_action = 'name'
            pygame.key.start_text_input()
            field = menu_input._ensure_browser_field(self)
            if field is not None:
                field.focus()
            return
        for key,rect in self.layout.items():
            if key.startswith('btn_') and rect.collidepoint(pos):
                self.active_input=False
                self.activate(key[4:])
                return
        if self.state == STATE_CHOOSE:
            for index,card in enumerate(self.cards):
                if card.rect.collidepoint(pos):
                    self.resolve_round(index)
                    self.set_state(self.state)
                    return

    def handle_menu_event(self,event):
        if event.type == pygame.TEXTINPUT and self.active_input:
            text=''.join(c for c in event.text if c.isprintable())
            self.user.nickname=(self.user.nickname+text)[:self.player_name_max_len]
        elif event.type == pygame.KEYDOWN and self.active_input:
            if event.key == pygame.K_BACKSPACE:
                self.user.nickname=self.user.nickname[:-1]
            elif event.key == pygame.K_RETURN:
                self.activate('continue')

    def handle_event(self,event):
        if event.type == pygame.QUIT:
            self.running=False
            return
        if event.type == pygame.WINDOWFOCUSLOST:
            self.pause(pygame.time.get_ticks())
            self.resize((self.w,self.h))
            return
        if event.type in (pygame.MOUSEBUTTONDOWN,pygame.FINGERDOWN,pygame.KEYDOWN):
            self.enable_audio()
        menu_input._sync_browser_value(self)
        if event.type == pygame.MOUSEMOTION:
            self.hover_action = next((k[4:] for k,r in self.layout.items() if k.startswith('btn_') and r.collidepoint(event.pos)),None)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not getattr(event,'touch',False):
            self._click(event.pos)
        elif event.type == pygame.FINGERDOWN:
            self._click((round(event.x*self.w),round(event.y*self.h)))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                actions = (['name'] if self.state == STATE_MENU else []) + [key[4:] for key in self.layout if key.startswith('btn_') and self.enabled(key[4:])]
                if actions:
                    direction=-1 if getattr(event,'mod',0)&pygame.KMOD_SHIFT else 1
                    current=actions.index(self.focus_action) if self.focus_action in actions else (-1 if direction==1 else 0)
                    self.focus_action=actions[(current+direction)%len(actions)]
                    self.active_input=self.focus_action=='name'
                    if self.active_input:
                        pygame.key.start_text_input()
                        field=menu_input._ensure_browser_field(self)
                        if field is not None: field.focus()
                return
            if self.state==STATE_MENU and self.active_input:
                self.handle_menu_event(event)
                return
            if event.key==pygame.K_RETURN and self.focus_action:
                self.activate(self.focus_action)
            elif event.key==pygame.K_ESCAPE and self.state in ('HELP','SETTINGS'):
                self.activate('back')
            elif event.key==pygame.K_SPACE:
                self.activate('resume' if self.state==STATE_PAUSE else 'pause')
            elif self.state==STATE_CHOOSE and event.key in (pygame.K_1,pygame.K_2,pygame.K_3):
                card=sorted(self.cards,key=lambda c:c.rect.centerx)[event.key-pygame.K_1]
                self.resolve_round(self.cards.index(card))
                self.set_state(self.state)
        elif event.type==pygame.TEXTINPUT and self.state==STATE_MENU:
            self.handle_menu_event(event)

    def update(self):
        previous=self.state
        if self.state==STATE_SHOW_BACKS:
            self.update_show_backs()
        elif self.state==STATE_SHUFFLE:
            self.update_shuffle()
        elif self.state==STATE_CHOOSE and pygame.time.get_ticks()-self.state_start_time >= 10_000:
            self.resolve_round(None)
        if self.state!=previous:
            self.set_state(self.state)
        if self.state==STATE_MENU:
            menu_input.update_native_field(self)
        else:
            menu_input._remove_browser_field()

    def draw(self):
        dashboard.draw_screen(self,self.layout,self.resources)
