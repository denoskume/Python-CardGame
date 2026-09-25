"""Core game logic and finite-state controller.

CardGame owns the round lifecycle, timers, card animation, input dispatch,
result resolution, pause/resume behavior, optional audio, and JSON history.
Rendering is delegated to dashboard.py.
"""

import pygame
import random
import time
import os
import json

import user as us
import bet as bt
import dashboard as db

# ===================== GAME STATES =====================
STATE_START = "START_SCREEN"
STATE_MENU = "MENU"
STATE_BET = "BET_SETUP"
STATE_SHOW_BACKS = "SHOW_BACKS"
STATE_SHUFFLE = "SHUFFLE"
STATE_CHOOSE = "CHOOSE"
STATE_RESULT = "RESULT"
STATE_GAME_OVER = "GAME_OVER"
STATE_PAUSE = "PAUSE"


# ===================== CARD CLASS =====================
class Card:
    """Represent one logical card while its rectangle moves during shuffling."""

    def __init__(self, rect, is_red: bool, img_front=None, 
        img_back_red=None, img_back_black=None):
        """Create a card with logical color identity and optional image assets."""
        self.rect = rect                            
        self.is_red = is_red                 
        self.face = "BACK"                  
                            
        # Optional images
        self.img_front = img_front
        self.img_back_red = img_back_red
        self.img_back_black = img_back_black

    def draw(self, screen, fonts):
        """Draw the card asset or a fallback rectangle when images are unavailable."""
        # If images are available, use them
        if self.img_front is not None and self.img_back_red is not None and self.img_back_black is not None:
            if self.face == "BACK":
                img = self.img_back_red if self.is_red else self.img_back_black
            else:
                img = self.img_front
            screen.blit(img, self.rect)
        else:
            # Fallback rectangles
            if self.face == "BACK":
                color = (200, 40, 40) if self.is_red else (20, 20, 20)
                pygame.draw.rect(screen, color, self.rect, border_radius=10)
                pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)
                txt = fonts["small"].render("RED" if self.is_red else "BLACK", True, (255, 255, 255))
                screen.blit(txt, txt.get_rect(center=self.rect.center))
            else:
                pygame.draw.rect(screen, (230, 230, 230), self.rect, border_radius=10)
                pygame.draw.rect(screen, (0, 0, 0), self.rect, 2, border_radius=10)
                txt = fonts["small"].render("CARD", True, (0, 0, 0))
                screen.blit(txt, txt.get_rect(center=self.rect.center))


# ===================== CARD GAME CLASS =====================
class CardGame:
    """Coordinate the complete game lifecycle through explicit runtime states."""

    def __init__(self, screen, user: us.User, bet: bt.Bet):
        """Initialize UI geometry, assets, audio, timers, history, and state."""
        self.screen = screen
        self.w, self.h = screen.get_size()

        # External domain objects
        self.user = user
        self.bet = bet

        # Buttons
        self.btn_restart = pygame.Rect(self.w // 2 - 100, self.h - 120, 200, 50)
        self.btn_main_menu = pygame.Rect(self.w // 2 - 220, self.h - 100, 200, 50)
        self.btn_exit = pygame.Rect(self.w // 2 + 20, self.h - 100, 200, 50)

        self.btn_continue = pygame.Rect(self.w // 2 - 100, self.h - 100, 200, 50)
        self.btn_start_round = pygame.Rect(self.w // 2 - 100, self.h - 120, 200, 50)
        self.btn_menu = pygame.Rect(self.w // 2 - 310, self.h - 70, 200, 50)
        self.btn_quit = pygame.Rect(self.w // 2 + 110, self.h - 70, 200, 50)

        # Fonts
        self.font_title = pygame.font.SysFont("arial", 40, bold=True)
        self.font_big = pygame.font.SysFont("arial", 28, bold=True)
        self.font_norm = pygame.font.SysFont("arial", 22)
        self.font_small = pygame.font.SysFont("arial", 18)
        self.font_mono = pygame.font.SysFont("consolas", 18)

        self.fonts = {"big": self.font_big, "small": self.font_small}

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (200, 40, 40)
        self.GREY = (60, 60, 60)
        self.DARK = (25, 25, 25)
        self.GREEN = (40, 160, 60)
        self.LIGHT = (220, 220, 220)
        self.YELLOW = (250, 230, 70)

        # Global state
        self.state = STATE_START

        # Menu / player
        self.player_name_max_len = 20
        self.active_input = False
        self.avatar_rects = [
            pygame.Rect(self.w // 2 - 150, 220, 70, 70),
            pygame.Rect(self.w // 2 - 35, 220, 70, 70),
            pygame.Rect(self.w // 2 + 80, 220, 70, 70),
        ]

        # Attempts buttons
        self.attempt_rects = [
            pygame.Rect(self.w // 2 - 150, 200, 80, 40),
            pygame.Rect(self.w // 2 - 40, 200, 80, 40),
            pygame.Rect(self.w // 2 + 70, 200, 80, 40),
        ]

        # Cards
        self.cards = []
        self.card_area_y = 260
        self.card_width = 180
        self.card_height = 250
        self.card_gap = 60

        # Assets
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")

        # Card images
        try:
            front = pygame.image.load(os.path.join(assets_dir, "card_front.png")).convert_alpha()
            back_red = pygame.image.load(os.path.join(assets_dir, "card_back_red.png")).convert_alpha()
            back_black = pygame.image.load(os.path.join(assets_dir, "card_back_black.png")).convert_alpha()

            self.card_img_front = pygame.transform.smoothscale(front, (self.card_width, self.card_height))
            self.card_img_back_red = pygame.transform.smoothscale(back_red, (self.card_width, self.card_height))
            self.card_img_back_black = pygame.transform.smoothscale(back_black, (self.card_width, self.card_height))
        except Exception as e:
            print("⚠ Could not load card images:", e)
            self.card_img_front = None
            self.card_img_back_red = None
            self.card_img_back_black = None

        # Avatars
        try:
            self.avatar_imgs = []
            for name in ["avatar1.png", "avatar2.png", "avatar3.png"]:
                img = pygame.image.load(os.path.join(assets_dir, name)).convert_alpha()
                img = pygame.transform.smoothscale(img, (70, 70))
                self.avatar_imgs.append(img)
        except Exception as e:
            print("⚠ Could not load avatars:", e)
            self.avatar_imgs = [None, None, None]

        # Logo cards for start screen
        try:
            self.logo_back = pygame.image.load(os.path.join(assets_dir, "card_logo_back.png")).convert_alpha()
            self.logo_front = pygame.image.load(os.path.join(assets_dir, "card_logo_front.png")).convert_alpha()

            self.logo_back = pygame.transform.smoothscale(self.logo_back, (70, 100))
            self.logo_front = pygame.transform.smoothscale(self.logo_front, (70, 100))
        except Exception as e:
            print("⚠ Could not load logo cards:", e)
            self.logo_back = None
            self.logo_front = None

        # Sounds (optional: the game still runs when no audio device is available)
        self.snd_shuffle = None
        self.snd_win = None
        self.snd_lose = None
        self.shuffle_channel = None
        self.result_channel = None

        if pygame.mixer.get_init() is not None:
            try:
                self.snd_shuffle = pygame.mixer.Sound(os.path.join(assets_dir, "shuffle.mp3"))
                self.snd_win = pygame.mixer.Sound(os.path.join(assets_dir, "win.mp3"))
                self.snd_lose = pygame.mixer.Sound(os.path.join(assets_dir, "lose.mp3"))

                self.snd_shuffle.set_volume(0.6)
                self.snd_win.set_volume(0.8)
                self.snd_lose.set_volume(0.8)

                self.shuffle_channel = pygame.mixer.Channel(1)
                self.result_channel = pygame.mixer.Channel(2)
            except pygame.error as e:
                print(f"⚠ Audio disabled: {e}")
        else:
            print("⚠ Audio disabled: pygame mixer is not available.")

        # Timers
        self.state_start_time = 0
        self.shuffle_interval = 300
        self.last_shuffle_swap = 0

        # Swap animation
        self.is_swapping = False
        self.swap_i = 0
        self.swap_j = 1
        self.swap_start_time = 0
        self.swap_duration = 300
        self.swap_rect_i_start = None
        self.swap_rect_j_start = None
        self.swap_rect_i_end = None
        self.swap_rect_j_end = None

        # Result
        self.message = ""
        self.round_result = None  # "WIN" / "LOSE"
        self.selected_card_index = None
        self.selected_card_rect = None

        # Stats
        self.round_history = []
        self.current_round_start_time = None
        self.total_time_played = 0.0

        # Pause
        self.state_before_pause = None
        self.pause_start = 0

        # JSON history (runtime data stored outside source code)
        project_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(project_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        self.history_file = os.path.join(data_dir, "history.json")
        self.global_history = self._load_history()

        # For bet widgets
        self._bet_minus_rect = None
        self._bet_plus_rect = None

    # ---------- JSON HISTORY ----------
    def _load_history(self):
        """Load persisted rounds, returning an empty list if history is unavailable."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
        except Exception as e:
            print("⚠ Error loading history.json:", e)
        return []

    def _save_history(self):
        """Persist the bounded global round history as readable JSON."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.global_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("⚠ Error saving history.json:", e)

    # ---------- EVENT HANDLERS FOR MENU ----------
    def handle_start_event(self, event):
        """Leave the splash screen after any keyboard or mouse input."""
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
            self.state = STATE_MENU

    def handle_menu_event(self, event):
        """Handle nickname editing, avatar selection, and profile validation."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            input_width = 300
            input_rect = pygame.Rect(self.w // 2 - input_width // 2, 155, input_width, 40)
            if input_rect.collidepoint(event.pos):
                self.active_input = True
            else:
                self.active_input = False

            for idx, rect in enumerate(self.avatar_rects):
                if rect.collidepoint(event.pos):
                    self.user.avatar_index = idx

            if self.btn_continue.collidepoint(event.pos):
                name_len = len(self.user.nickname.strip())
                if 3 <= name_len <= self.player_name_max_len:
                    self.state = STATE_BET

        elif event.type == pygame.KEYDOWN and self.active_input:
            if event.key == pygame.K_BACKSPACE:
                self.user.nickname = self.user.nickname[:-1]
            elif event.key == pygame.K_RETURN:
                name_len = len(self.user.nickname.strip())
                if 3 <= name_len <= self.player_name_max_len:
                    self.state = STATE_BET
            else:
                if len(self.user.nickname) < self.player_name_max_len:
                    if event.unicode.isprintable():
                        self.user.nickname += event.unicode

    # ---------- BET SCREEN EVENTS ----------
    def handle_bet_event(self, event):
        """Handle turbo selection, bet adjustment, and round start requests."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Choose turbo
            for idx, rect in enumerate(self.attempt_rects):
                if rect.collidepoint(pos):
                    self.bet.set_turbo(idx + 1)

            # Bet -
            if self._bet_minus_rect is not None and self._bet_minus_rect.collidepoint(pos):
                self.bet.decrease(step=5)

            # Bet +
            elif self._bet_plus_rect is not None and self._bet_plus_rect.collidepoint(pos):
                self.bet.increase(step=5, balance=self.user.balance)

            # START round
            can_start = self.bet.is_valid(self.user.balance)
            if can_start and self.btn_start_round.collidepoint(pos):
                self.start_round()

    # ---------- START A ROUND ----------
    def start_round(self):
        """Create three cards, choose the red card, and start observation."""
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

    # ---------- SHOW BACKS UPDATE ----------
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

    # ---------- SHUFFLE UPDATE ----------
    def update_shuffle(self):
        """Animate random pair swaps and transition to card selection."""
        now = pygame.time.get_ticks()
        elapsed = now - self.state_start_time

        if self.is_swapping:
            t = (now - self.swap_start_time) / self.swap_duration
            if t >= 1.0:
                self.cards[self.swap_i].rect = self.swap_rect_i_end
                self.cards[self.swap_j].rect = self.swap_rect_j_end
                self.is_swapping = False
                self.last_shuffle_swap = now
            else:
                def lerp(a, b, u):
                    return a + (b - a) * u

                x_i = lerp(self.swap_rect_i_start.x, self.swap_rect_i_end.x, t)
                y_i = lerp(self.swap_rect_i_start.y, self.swap_rect_i_end.y, t)
                self.cards[self.swap_i].rect.x = int(x_i)
                self.cards[self.swap_i].rect.y = int(y_i)

                x_j = lerp(self.swap_rect_j_start.x, self.swap_rect_j_end.x, t)
                y_j = lerp(self.swap_rect_j_start.y, self.swap_rect_j_end.y, t)
                self.cards[self.swap_j].rect.x = int(x_j)
                self.cards[self.swap_j].rect.y = int(y_j)
        else:
            if now - self.last_shuffle_swap >= self.shuffle_interval:
                self.swap_two_cards()

        if elapsed >= 10_000:
            if self.is_swapping:
                self.cards[self.swap_i].rect = self.swap_rect_i_end
                self.cards[self.swap_j].rect = self.swap_rect_j_end
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

        if self.snd_shuffle is not None and self.shuffle_channel is not None:
            self.shuffle_channel.stop()
            self.shuffle_channel.play(self.snd_shuffle, maxtime=self.swap_duration)

        self.swap_rect_i_start = self.cards[i].rect.copy()
        self.swap_rect_j_start = self.cards[j].rect.copy()
        self.swap_rect_i_end = self.cards[j].rect.copy()
        self.swap_rect_j_end = self.cards[i].rect.copy()

    # ---------- CHOOSE UPDATE / EVENTS ----------
    def update_choose(self):
        """Resolve a timeout as a loss when no card is selected in time."""
        elapsed = pygame.time.get_ticks() - self.state_start_time
        if elapsed >= 10_000 and self.selected_card_index is None:
            self.resolve_round(None)

    def handle_choose_event(self, event):
        """Resolve the round when the player clicks one of the cards."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.selected_card_index is not None:
                return
            pos = event.pos
            for idx, c in enumerate(self.cards):
                if c.rect.collidepoint(pos):
                    self.selected_card_index = idx
                    self.selected_card_rect = c.rect.copy()
                    self.resolve_round(idx)
                    break

    # ---------- RESOLVE ROUND ----------
    def resolve_round(self, index):
        """Resolve win/loss, update balance, persist the round, and choose the next state."""
        for c in self.cards:
            c.face = "BACK"

        now = pygame.time.get_ticks()
        if self.current_round_start_time is not None:
            duration_sec = (now - self.current_round_start_time) / 1000.0
        else:
            duration_sec = 0.0
        self.total_time_played += duration_sec

        mult = self.bet.turbo
        stake = self.bet.stake()
        if stake > self.user.balance:
            stake = self.user.balance

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

            if self.snd_lose is not None and self.result_channel is not None:
                self.result_channel.stop()
                self.result_channel.play(self.snd_lose)

        else:
            chosen = self.cards[index]
            if chosen.is_red:
                # ---------- WIN ----------
                self.round_result = "WIN"

                profit = self.user.apply_win(stake)  # balance += stake
                self.message = f"Well done! Red card! Profit: +{profit}$ (x{mult})."

                if self.snd_win is not None and self.result_channel is not None:
                    self.result_channel.stop()
                    self.result_channel.play(self.snd_win)

            else:
                # ---------- LOSE ----------
                self.round_result = "LOSE"

                loss = self.user.apply_loss(stake)   # balance -= stake
                self.message = f"Missed it, that wasn't the red card. Loss: {loss}$ (x{mult})."

                if self.snd_lose is not None and self.result_channel is not None:
                    self.result_channel.stop()
                    self.result_channel.play(self.snd_lose)

        if self.user.balance < 0:
            self.user.balance = 0

        round_entry = {
            "round": len(self.round_history) + 1,
            "bet": self.bet.amount,
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


    # ---------- RESULT / GAME OVER EVENTS ----------
    def handle_result_event(self, event):
        """Handle next-round, menu, and quit actions from the result screen."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.result_channel is not None and self.result_channel.get_busy():
                self.result_channel.fadeout(150)

            pos = event.pos

            if self.state == STATE_RESULT:
                if self.btn_continue.collidepoint(pos) and self.user.balance >= self.bet.min:
                    self.state = STATE_BET
                elif self.btn_main_menu.collidepoint(pos):
                    self.reset_game()
                    self.state = STATE_MENU
                elif self.btn_exit.collidepoint(pos):
                    pygame.quit()
                    import sys
                    sys.exit()

            elif self.state == STATE_GAME_OVER:
                if self.btn_main_menu.collidepoint(pos):
                    self.reset_game()
                    self.state = STATE_MENU
                elif self.btn_exit.collidepoint(pos):
                    pygame.quit()
                    import sys
                    sys.exit()

    # ---------- RESET ----------
    def reset_game(self):
        """Reset session-level player, bet, round, and timer state."""
        self.user.reset()
        self.bet.amount = max(self.bet.min, min(self.bet.max, 10))
        self.bet.turbo = 1

        self.selected_card_index = None
        self.selected_card_rect = None
        self.round_result = None
        self.round_history.clear()
        self.total_time_played = 0.0

    # ---------- GLOBAL EVENTS ----------
    def handle_event(self, event):
        """Dispatch input to the handler associated with the active state."""
        # Pause toggle
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.state == STATE_PAUSE and self.state_before_pause is not None:
                pause_duration = pygame.time.get_ticks() - self.pause_start

                if self.state_before_pause in (STATE_SHOW_BACKS, STATE_SHUFFLE, STATE_CHOOSE, STATE_RESULT):
                    self.state_start_time += pause_duration
                    if self.state_before_pause == STATE_SHUFFLE and self.is_swapping:
                        self.swap_start_time += pause_duration
                        self.last_shuffle_swap += pause_duration

                self.state = self.state_before_pause
                self.state_before_pause = None

            elif self.state in (
                STATE_SHOW_BACKS, STATE_SHUFFLE, STATE_CHOOSE,
                STATE_RESULT, STATE_BET, STATE_MENU, STATE_START
            ):
                self.state_before_pause = self.state
                self.pause_start = pygame.time.get_ticks()
                self.state = STATE_PAUSE

            return

        # State-specific events
        if self.state == STATE_START:
            self.handle_start_event(event)
        elif self.state == STATE_MENU:
            self.handle_menu_event(event)
        elif self.state == STATE_BET:
            self.handle_bet_event(event)
        elif self.state == STATE_CHOOSE:
            self.handle_choose_event(event)
        elif self.state in (STATE_RESULT, STATE_GAME_OVER):
            self.handle_result_event(event)

    # ---------- UPDATE & DRAW ----------
    def update(self):
        """Advance time-dependent logic for the active state."""
        if self.state == STATE_PAUSE:
            return

        if self.state == STATE_SHOW_BACKS:
            self.update_show_backs()
        elif self.state == STATE_SHUFFLE:
            self.update_shuffle()
        elif self.state == STATE_CHOOSE:
            self.update_choose()

    def draw(self):
        """Delegate rendering to dashboard.py for the active state."""
        if self.state == STATE_PAUSE and self.state_before_pause is not None:
            # Draw the underlying state
            if self.state_before_pause == STATE_START:
                db.draw_start_screen(self)
            elif self.state_before_pause == STATE_MENU:
                db.draw_menu(self)
            elif self.state_before_pause == STATE_BET:
                db.draw_bet_screen(self)
            elif self.state_before_pause == STATE_SHOW_BACKS:
                db.draw_show_backs(self)
            elif self.state_before_pause == STATE_SHUFFLE:
                db.draw_shuffle(self)
            elif self.state_before_pause == STATE_CHOOSE:
                db.draw_choose(self)
            elif self.state_before_pause == STATE_RESULT:
                db.draw_result(self)
            elif self.state_before_pause == STATE_GAME_OVER:
                db.draw_game_over(self)

            db.draw_pause_overlay(self)
            return

        if self.state == STATE_START:
            db.draw_start_screen(self)
        elif self.state == STATE_MENU:
            db.draw_menu(self)
        elif self.state == STATE_BET:
            db.draw_bet_screen(self)
        elif self.state == STATE_SHOW_BACKS:
            db.draw_show_backs(self)
        elif self.state == STATE_SHUFFLE:
            db.draw_shuffle(self)
        elif self.state == STATE_CHOOSE:
            db.draw_choose(self)
        elif self.state == STATE_RESULT:
            db.draw_result(self)
        elif self.state == STATE_GAME_OVER:
            db.draw_game_over(self)

