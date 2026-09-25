"""Rendering functions for every CardGame screen.

This module contains presentation logic only. It reads game state and draws
controls, timers, cards, summaries, and overlays without owning round rules.
"""

import pygame

# ---------- Small helpers ----------

def _draw_center_text(game, text, y, font, color):
    """Render a text label centered horizontally at the requested y-position."""
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(game.w // 2, y))
    game.screen.blit(surf, rect)


def _draw_button(game, rect, text, bg_color, text_color):
    """Draw a reusable rounded button with centered text."""
    pygame.draw.rect(game.screen, bg_color, rect, border_radius=10)
    pygame.draw.rect(game.screen, (0, 0, 0), rect, 2, border_radius=10)
    label = game.font_norm.render(text, True, text_color)
    game.screen.blit(label, label.get_rect(center=rect.center))


def _draw_circle_timer(game, center, total_ms, elapsed_ms):
    """Render the remaining phase time inside a circular timer."""
    x, y = center
    radius = 40

    pygame.draw.circle(game.screen, game.GREY, (x, y), radius, 3)

    remaining = max(0, total_ms - elapsed_ms)
    minutes = remaining // 60000
    seconds = (remaining // 1000) % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    txt = game.font_big.render(time_str, True, game.WHITE)
    txt_rect = txt.get_rect(center=(x, y))
    game.screen.blit(txt, txt_rect)


def draw_pause_overlay(game):
    """Draw a translucent pause overlay above the current screen."""
    overlay = pygame.Surface((game.w, game.h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    game.screen.blit(overlay, (0, 0))

    _draw_center_text(game, "PAUSE", 120, game.font_title, game.YELLOW)
    _draw_center_text(game, "Press SPACE to resume", 170,
                      game.font_norm, game.LIGHT)


def _draw_logo_cards(game):
    """Draw the decorative card logo when both assets are available."""
    if game.logo_back is None or game.logo_front is None:
        return
    x, y = 110, 145
    game.screen.blit(game.logo_back, (x + 30, y - 35))
    game.screen.blit(game.logo_front, (x, y))


def _draw_player_info(game):
    """Draw the current player avatar and nickname in the screen header."""
    if game.user.nickname.strip() == "":
        return

    avatar_pos = (20, 20)
    idx = game.user.avatar_index

    if game.avatar_imgs[idx] is not None:
        game.screen.blit(
            game.avatar_imgs[idx],
            game.avatar_imgs[idx].get_rect(topleft=avatar_pos)
        )
    else:
        fallback_rect = pygame.Rect(20, 20, 60, 60)
        pygame.draw.rect(game.screen, game.GREY, fallback_rect)
        pygame.draw.rect(game.screen, game.WHITE, fallback_rect, 2)

    name_text = game.font_big.render(game.user.nickname, True, game.WHITE)
    game.screen.blit(name_text, (100, 35))


# ---------- START SCREEN ----------

def draw_start_screen(game):
    """Render the splash screen and the five most recent persisted rounds."""
    game.screen.fill(game.DARK)
    _draw_logo_cards(game)

    _draw_center_text(game, "ROUGE GAGNE, NOIR PERD", 150, game.font_title, game.WHITE)
    _draw_center_text(game, "Press any key or click to continue", 220,
                      game.font_norm, game.LIGHT)

    panel_w, panel_h = 620, 200
    panel_rect = pygame.Rect(game.w // 2 - panel_w // 2, 260, panel_w, panel_h)

    pygame.draw.rect(game.screen, (15, 15, 15), panel_rect, border_radius=10)
    pygame.draw.rect(game.screen, game.LIGHT, panel_rect, 2, border_radius=10)

    title = "Last attempts (all sessions combined):"
    title_surf = game.font_small.render(title, True, game.LIGHT)
    game.screen.blit(title_surf, (panel_rect.x + 20, panel_rect.y + 15))

    if not game.global_history:
        msg = "No game has been recorded yet."
        msg_surf = game.font_small.render(msg, True, game.LIGHT)
        game.screen.blit(msg_surf, (panel_rect.x + 20, panel_rect.y + 50))
        return

    y = panel_rect.y + 50
    line_h = 22

    headers = ["#", "Player", "Bet", "x", "Result", "Time(s)", "Capital"]
    col_x = [
        panel_rect.x + 20,
        panel_rect.x + 60,
        panel_rect.x + 200,
        panel_rect.x + 260,
        panel_rect.x + 310,
        panel_rect.x + 410,
        panel_rect.x + 500,
    ]

    for txt, x in zip(headers, col_x):
        h_surf = game.font_small.render(txt, True, game.WHITE)
        game.screen.blit(h_surf, (x, y))

    y += line_h
    pygame.draw.line(game.screen, game.LIGHT,
                     (panel_rect.x + 20, y),
                     (panel_rect.right - 20, y), 1)
    y += 5

    last5 = game.global_history[-5:][::-1]

    for r in last5:
        player = r.get("player", "") or "-"
        row_values = [
            str(r.get("round", "?")),
            player,
            f"{r.get('bet', 0)}$",
            f"x{r.get('mult', 1)}",
            r.get("result", ""),
            f"{r.get('duration', 0):.2f}",
            f"{r.get('balance_after', 0)}$"
        ]

        for txt, x in zip(row_values, col_x):
            v_surf = game.font_small.render(txt, True, game.LIGHT)
            game.screen.blit(v_surf, (x, y))
        y += line_h
        if y > panel_rect.bottom - 10:
            break


# ---------- MENU (nickname + avatar) ----------

def draw_menu(game):
    """Render nickname input, avatar selection, and validation feedback."""
    game.screen.fill(game.DARK)
    _draw_logo_cards(game)   # small side logo on the left (keep as before)

    _draw_center_text(game, "GAME MENU", 80, game.font_title, game.WHITE)

    panel_w, panel_h = 750, 430
    panel_rect = pygame.Rect(game.w // 2 - panel_w // 2, 110, panel_w, panel_h)

    pygame.draw.rect(game.screen, (15, 15, 15), panel_rect, border_radius=14)
    pygame.draw.rect(game.screen, game.LIGHT, panel_rect, 2, border_radius=14)

    subtitle = "Create your player profile to start."
    sub_surf = game.font_small.render(subtitle, True, game.LIGHT)
    game.screen.blit(sub_surf, sub_surf.get_rect(
        midtop=(panel_rect.centerx, panel_rect.y + 15)
    ))

    # ---------- Nickname ----------
    label_pseudo = game.font_norm.render("Nickname:", True, game.LIGHT)
    game.screen.blit(label_pseudo, (panel_rect.x + 40, panel_rect.y + 50))

    input_width = 300
    input_rect = pygame.Rect(game.w // 2 - input_width // 2, 155, input_width, 40)

    pygame.draw.rect(game.screen,
                     game.WHITE if game.active_input else game.GREY,
                     input_rect, border_radius=8)
    pygame.draw.rect(game.screen, game.BLACK, input_rect, 2, border_radius=8)

    name_stripped = game.user.nickname.strip()
    name_len = len(name_stripped)
    pseudo_display = game.user.nickname if game.user.nickname else "Click here to type..."
    color = game.BLACK if game.user.nickname else (150, 150, 150)
    txt = game.font_norm.render(pseudo_display, True, color)
    game.screen.blit(txt, (input_rect.x + 10, input_rect.y + 8))

    if 0 < name_len < 3:
        warn = game.font_small.render("Minimum 3 characters required.", True, game.RED)
        warn_rect = warn.get_rect(center=(game.w // 2, input_rect.bottom + 10))
        game.screen.blit(warn, warn_rect)

    # ---------- Avatars ----------
    label_avatar = game.font_norm.render("Avatar:", True, game.LIGHT)
    game.screen.blit(label_avatar, (panel_rect.x + 40, panel_rect.y + 125))

    for idx, rect in enumerate(game.avatar_rects):
        slot_rect = rect.inflate(12, 12)
        pygame.draw.rect(game.screen, (20, 20, 20), slot_rect, border_radius=10)

        if game.avatar_imgs[idx] is not None:
            game.screen.blit(game.avatar_imgs[idx], rect)
        else:
            avatar_colors = [(200, 50, 50), (50, 150, 250), (250, 200, 50)]
            pygame.draw.rect(game.screen, avatar_colors[idx], rect, border_radius=8)

        border_color = game.GREEN if idx == game.user.avatar_index else game.WHITE
        border_width = 3 if idx == game.user.avatar_index else 1
        pygame.draw.rect(game.screen, border_color, rect, border_width, border_radius=8)

    # ---------- CARD LOGO BETWEEN AVATARS & CONTINUE ----------
    if game.logo_back is not None and game.logo_front is not None:
        # place it horizontally centered, a bit under the avatars
        avatars_bottom = max(r.bottom for r in game.avatar_rects)
        logo_center_y = avatars_bottom + 80  # spacing down from avatars

        # slightly overlapped cards like on the start screen
        back_rect = game.logo_back.get_rect()
        front_rect = game.logo_front.get_rect()

        back_rect.center = (panel_rect.centerx + 35, logo_center_y - 10)
        front_rect.center = (panel_rect.centerx - 35, logo_center_y + 10)

        game.screen.blit(game.logo_back, back_rect)
        game.screen.blit(game.logo_front, front_rect)

    # ---------- Continue button ----------
    enabled = (3 <= name_len <= game.player_name_max_len)
    btn_color = game.GREEN if enabled else game.GREY

    game.btn_continue.width = 220
    game.btn_continue.height = 50
    game.btn_continue.x = panel_rect.centerx - game.btn_continue.width // 2
    game.btn_continue.y = panel_rect.bottom - 70

    _draw_button(game, game.btn_continue, "Next", btn_color, game.BLACK)

    hint = "Press Enter or click <<Next>> to go to the betting screen."
    hint_surf = game.font_small.render(hint, True, (160, 160, 160))
    game.screen.blit(hint_surf, hint_surf.get_rect(
        midtop=(panel_rect.centerx, panel_rect.bottom + 8)
    ))


# ---------- BET SCREEN ----------

def draw_bet_screen(game):
    """Render balance, turbo selection, bet controls, and start availability."""
    game.screen.fill(game.DARK)

    panel_w, panel_h = 800, 500
    panel_rect = pygame.Rect(game.w // 2 - panel_w // 2, 50, panel_w, panel_h)

    pygame.draw.rect(game.screen, (15, 15, 15), panel_rect, border_radius=14)
    pygame.draw.rect(game.screen, game.LIGHT, panel_rect, 2, border_radius=14)

    cx = panel_rect.centerx
    y = panel_rect.y + 25

    # Avatar + Hello
    avatar_size = 60
    avatar_rect = pygame.Rect(panel_rect.x + 30, y, avatar_size, avatar_size)

    idx = game.user.avatar_index
    if game.avatar_imgs[idx] is not None:
        avatar_img = pygame.transform.smoothscale(game.avatar_imgs[idx], (avatar_size, avatar_size))
        game.screen.blit(avatar_img, avatar_rect)
    else:
        pygame.draw.rect(game.screen, game.GREY, avatar_rect, border_radius=10)
        pygame.draw.rect(game.screen, game.WHITE, avatar_rect, 2, border_radius=10)

    greet_text = f"Hello {game.user.nickname} !"
    try:
        font_emoji = pygame.font.SysFont("Segoe UI Emoji", 28)
    except Exception:
        font_emoji = game.font_big

    greet_surf = game.font_big.render(greet_text, True, game.WHITE)
    emoji_surf = font_emoji.render("👋", True, game.WHITE)

    emoji_rect = emoji_surf.get_rect(midleft=(avatar_rect.right + 20,
                                              avatar_rect.centery - 10))
    greet_rect = greet_surf.get_rect(midleft=(emoji_rect.right + 10,
                                              avatar_rect.centery - 10))

    game.screen.blit(emoji_surf, emoji_rect)
    game.screen.blit(greet_surf, greet_rect)

    sub_surf = game.font_small.render("Configure your next round.",
                                      True, (180, 180, 180))
    sub_rect = sub_surf.get_rect(midleft=(avatar_rect.right + 20,
                                          avatar_rect.centery + 12))
    game.screen.blit(sub_surf, sub_rect)

    y = avatar_rect.bottom + 25

    # Dashboard table
    table_h = 90
    table_rect = pygame.Rect(panel_rect.x + 30, y,
                             panel_rect.width - 60, table_h)
    pygame.draw.rect(game.screen, (10, 10, 10), table_rect, border_radius=10)
    pygame.draw.rect(game.screen, game.LIGHT, table_rect, 1, border_radius=10)

    col_w = table_rect.width // 3

    def draw_kpi(col_idx, label, value, color=(255, 255, 255)):
        x_center = table_rect.x + col_w * col_idx + col_w // 2
        label_s = game.font_small.render(label, True, (180, 180, 180))
        label_r = label_s.get_rect(center=(x_center, table_rect.y + 22))
        game.screen.blit(label_s, label_r)

        value_s = game.font_big.render(value, True, color)
        value_r = value_s.get_rect(center=(x_center, table_rect.y + 55))
        game.screen.blit(value_s, value_r)

    # Keep the selected multiplier affordable whenever the base bet changes.
    affordable_mults = [m for m in (1, 2, 3) if game.bet.amount * m <= game.user.balance]
    if not affordable_mults:
        max_affordable = 1
    else:
        max_affordable = max(affordable_mults)
    if game.bet.turbo > max_affordable:
        game.bet.turbo = max_affordable

    draw_kpi(0, "Current Balance", f"{game.user.balance}$", game.LIGHT)
    draw_kpi(1, "Multiplier", f"x{game.bet.turbo}", game.GREEN)
    draw_kpi(2, "Selected Turbo", f"{game.bet.turbo}", game.LIGHT)

    pygame.draw.line(game.screen, (60, 60, 60),
                     (table_rect.x + col_w, table_rect.y + 10),
                     (table_rect.x + col_w, table_rect.bottom - 10), 1)
    pygame.draw.line(game.screen, (60, 60, 60),
                     (table_rect.x + 2 * col_w, table_rect.y + 10),
                     (table_rect.x + 2 * col_w, table_rect.bottom - 10), 1)

    y = table_rect.bottom + 30

    # Turbo buttons
    _draw_center_text(game, "Turbo", y, game.font_norm, game.WHITE)
    y += 30

    btn_w, btn_h = 90, 40
    spacing = 20
    total_w = 3 * btn_w + 2 * spacing
    start_x = cx - total_w // 2
    attempts_y = y

    labels = ["x1", "x2", "x3"]
    for idx, rect in enumerate(game.attempt_rects):
        mult = idx + 1
        rect.width = btn_w
        rect.height = btn_h
        rect.x = start_x + idx * (btn_w + spacing)
        rect.y = attempts_y

        affordable = (game.bet.amount * mult <= game.user.balance)
        selected = (mult == game.bet.turbo)

        if not affordable:
            color = (40, 40, 40)
            text_col = (130, 130, 130)
        elif selected:
            color = game.GREEN
            text_col = game.BLACK
        else:
            color = game.GREY
            text_col = game.BLACK

        pygame.draw.rect(game.screen, color, rect, border_radius=10)
        pygame.draw.rect(game.screen, (0, 0, 0), rect, 2, border_radius=10)
        label_surf = game.font_norm.render(labels[idx], True, text_col)
        game.screen.blit(label_surf, label_surf.get_rect(center=rect.center))

    y = attempts_y + btn_h + 35

    # Bet block
    _draw_center_text(game, f"Bet (min {game.bet.min}$, max {game.bet.max}$)", y,
                      game.font_norm, game.WHITE)
    y += 28

    bet_w, bet_h = 150, 46
    bet_rect = pygame.Rect(cx - bet_w // 2, y, bet_w, bet_h)
    pygame.draw.rect(game.screen, game.WHITE, bet_rect, border_radius=12)
    pygame.draw.rect(game.screen, game.BLACK, bet_rect, 3, border_radius=12)
    bet_txt = game.font_big.render(f"{game.bet.amount}$", True, game.BLACK)
    game.screen.blit(bet_txt, bet_txt.get_rect(center=bet_rect.center))

    btn_side = 46
    btn_space = 20
    btn_minus = pygame.Rect(bet_rect.left - btn_side - btn_space,
                            y, btn_side, bet_h)
    btn_plus = pygame.Rect(bet_rect.right + btn_space,
                           y, btn_side, bet_h)

    def draw_round_btn(rect, label):
        if label == "-":
            fill = game.RED
        elif label == "+":
            fill = game.GREEN
        else:
            fill = (50, 50, 50)

        pygame.draw.rect(game.screen, fill, rect, border_radius=12)
        pygame.draw.rect(game.screen, game.WHITE, rect, 2, border_radius=12)
        txt = game.font_big.render(label, True, game.WHITE)
        game.screen.blit(txt, txt.get_rect(center=rect.center))

    draw_round_btn(btn_minus, "-")
    draw_round_btn(btn_plus, "+")

    game._bet_minus_rect = btn_minus
    game._bet_plus_rect = btn_plus

    y = bet_rect.bottom + 35

    can_start = game.bet.is_valid(game.user.balance)
    help_msg = '' \
               if can_start else "Adjust your bet to stay within your capital."
    help_color = game.LIGHT if can_start else game.RED
    _draw_center_text(game, help_msg, y, game.font_small, help_color)

    btn_w, btn_h = 230, 40
    game.btn_start_round.width = btn_w
    game.btn_start_round.height = btn_h
    game.btn_start_round.x = cx - btn_w // 2
    game.btn_start_round.y = panel_rect.bottom - btn_h - 5

    start_color = game.GREEN if can_start else game.GREY
    _draw_button(game, game.btn_start_round, "START", start_color, game.BLACK)

    hint = "Click <<Start>> to play a round."
    hint_surf = game.font_small.render(hint, True, (160, 160, 160))
    game.screen.blit(hint_surf, hint_surf.get_rect(
        midtop=(panel_rect.centerx, panel_rect.bottom + 8)
    ))

# ---------- SHARED STEPS (SHOW_BACKS / SHUFFLE / CHOOSE) ----------

def draw_show_backs(game):
    """Render the observation phase with card identities visible."""
    game.screen.fill(game.DARK)
    _draw_player_info(game)

    panel_w, panel_h = 540, 140
    panel_rect = pygame.Rect(game.w // 2 - panel_w // 2, 80, panel_w, panel_h)

    pygame.draw.rect(game.screen, (15, 15, 15), panel_rect, border_radius=10)
    pygame.draw.rect(game.screen, game.LIGHT, panel_rect, 2, border_radius=10)

    title_surf = game.font_big.render("Step 1: watch the red card!", True, game.WHITE)
    subtitle_surf = game.font_norm.render("Cards are visible for 10 seconds.", True, game.LIGHT)

    game.screen.blit(title_surf, (panel_rect.x + 20, panel_rect.y + 20))
    game.screen.blit(subtitle_surf, (panel_rect.x + 20, panel_rect.y + 80))

    elapsed = pygame.time.get_ticks() - game.state_start_time
    timer_center = (panel_rect.right - 80, panel_rect.centery)

    _draw_circle_timer(game, timer_center, 10_000, elapsed)

    for c in game.cards:
        c.draw(game.screen, game.fonts)


def draw_shuffle(game):
    """Render the shuffle phase while all cards share the same visible face."""
    game.screen.fill(game.DARK)
    _draw_player_info(game)

    panel_w, panel_h = 540, 140
    panel_rect = pygame.Rect(game.w // 2 - panel_w // 2, 80, panel_w, panel_h)

    pygame.draw.rect(game.screen, (15, 15, 15), panel_rect, border_radius=10)
    pygame.draw.rect(game.screen, game.LIGHT, panel_rect, 2, border_radius=10)

    title_surf = game.font_big.render("Step 2: card shuffling", True, game.WHITE)
    subtitle_surf = game.font_norm.render(
        "Mentally track the position of the red card...",
        True, game.LIGHT
    )

    game.screen.blit(title_surf, (panel_rect.x + 20, panel_rect.y + 20))
    game.screen.blit(subtitle_surf, (panel_rect.x + 20, panel_rect.y + 80))

    elapsed = pygame.time.get_ticks() - game.state_start_time
    timer_center = (panel_rect.right - 80, panel_rect.centery)

    _draw_circle_timer(game, timer_center, 10_000, elapsed)

    for c in game.cards:
        c.draw(game.screen, game.fonts)


def draw_choose(game):
    """Render the timed selection phase and highlight a chosen card."""
    game.screen.fill(game.DARK)
    _draw_player_info(game)

    panel_w, panel_h = 540, 140
    panel_rect = pygame.Rect(game.w // 2 - panel_w // 2, 80, panel_w, panel_h)

    pygame.draw.rect(game.screen, (15, 15, 15), panel_rect, border_radius=10)
    pygame.draw.rect(game.screen, game.LIGHT, panel_rect, 2, border_radius=10)

    title_surf = game.font_big.render("Step 3: make your choice!", True, game.WHITE)
    subtitle_surf = game.font_norm.render(
        "Click on a card (you have 10 seconds).",
        True, game.LIGHT
    )

    game.screen.blit(title_surf, (panel_rect.x + 20, panel_rect.y + 20))
    game.screen.blit(subtitle_surf, (panel_rect.x + 20, panel_rect.y + 80))

    elapsed = pygame.time.get_ticks() - game.state_start_time
    timer_center = (panel_rect.right - 80, panel_rect.centery)

    _draw_circle_timer(game, timer_center, 10_000, elapsed)

    for c in game.cards:
        c.draw(game.screen, game.fonts)

    if game.selected_card_rect is not None:
        halo_rect = game.selected_card_rect.inflate(-12, -12)
        pygame.draw.rect(game.screen, game.YELLOW, halo_rect, 4, border_radius=12)


# ---------- RESULT SCREEN ----------

def draw_result(game):
    """Render outcome, stake impact, balance, cards, and navigation actions."""
    game.screen.fill(game.DARK)
    _draw_player_info(game)

    title = "WON!" if game.round_result == "WIN" else "LOST..."
    color = game.GREEN if game.round_result == "WIN" else game.RED
    _draw_center_text(game, title, 60, game.font_title, color)

    panel_w, panel_h = 480, 150
    panel_rect = pygame.Rect(game.w // 2 - panel_w // 2, 90, panel_w, panel_h)

    pygame.draw.rect(game.screen, (15, 15, 15), panel_rect, border_radius=10)
    pygame.draw.rect(game.screen, game.LIGHT, panel_rect, 2, border_radius=10)

    cx = panel_rect.centerx
    y = panel_rect.y + 15
    line_h = 26

    def kpi_line(label, value, color_val=game.WHITE):
        nonlocal y
        label_surf = game.font_small.render(label, True, game.LIGHT)
        value_surf = game.font_small.render(value, True, color_val)

        game.screen.blit(label_surf, (panel_rect.x + 20, y))
        game.screen.blit(value_surf,
                         (panel_rect.right - 20 - value_surf.get_width(), y))
        y += line_h

    last_round = game.round_history[-1] if game.round_history else None
    duration = last_round["duration"] if last_round else 0.0
    stake = last_round["stake"] if last_round else 0

    result_label = "Victory" if game.round_result == "WIN" else "Defeat"
    result_color = game.GREEN if game.round_result == "WIN" else game.RED

    kpi_line("Result:", result_label, result_color)
    kpi_line("Bet:", f"{game.bet.amount}$  x{game.bet.turbo}")
    if game.round_result == "WIN":
        gain = stake * 2
        kpi_line("Gain:", f"+{gain}$", game.GREEN)
    else:
        loss = stake
        kpi_line("Loss:", f"-{loss}$", game.RED)
    kpi_line("New Balance:", f"{game.user.balance}$")
    kpi_line("Round duration:", f"{duration:.2f} s")

    for c in game.cards:
        c.draw(game.screen, game.fonts)

    if game.selected_card_rect is not None:
        halo_rect = game.selected_card_rect.inflate(12, 12)
        pygame.draw.rect(game.screen, game.YELLOW, halo_rect, 6, border_radius=18)

    if game.cards:
        max_card_bottom = max(c.rect.bottom for c in game.cards)
    else:
        max_card_bottom = game.h // 2

    btn_y = max_card_bottom + 30

    game.btn_continue.y = btn_y
    game.btn_main_menu.y = btn_y
    game.btn_exit.y = btn_y

    game.btn_continue.x = game.w // 2 - 100
    game.btn_main_menu.x = game.btn_continue.x - 230
    game.btn_exit.x = game.btn_continue.x + 230

    if game.user.balance >= game.bet.min:
        _draw_button(game, game.btn_continue, "New round", game.GREEN, game.BLACK)

    _draw_button(game, game.btn_main_menu, "Menu", game.LIGHT, game.BLACK)
    _draw_button(game, game.btn_exit, "Quit", game.RED, game.WHITE)


# ---------- GAME OVER DASHBOARD ----------

def draw_game_over(game):
    """Render the end-of-session summary and recent round breakdown."""
    game.screen.fill(game.DARK)
    _draw_player_info(game)

    _draw_center_text(game, "GAME OVER", 80, game.font_title, game.RED)

    panel_w, panel_h = 520, 320
    panel_rect = pygame.Rect(game.w // 2 - panel_w // 2, 120, panel_w, panel_h)

    pygame.draw.rect(game.screen, (15, 15, 15), panel_rect, border_radius=12)
    pygame.draw.rect(game.screen, game.LIGHT, panel_rect, 2, border_radius=12)

    cx = panel_rect.centerx
    y = panel_rect.y + 30
    line_h = 26

    total_rounds = len(game.round_history)
    wins = sum(1 for r in game.round_history if r["result"] == "WIN")
    losses = total_rounds - wins
    total_stake = sum(r["stake"] for r in game.round_history)
    net_gain = sum((r["stake"] * 2 if r["result"] == "WIN" else -r["stake"])
                   for r in game.round_history)
    avg_time = (game.total_time_played / total_rounds) if total_rounds > 0 else 0.0

    def center_line(text, font, color):
        nonlocal y
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(cx, y))
        game.screen.blit(surf, rect)
        y += line_h

    center_line(f"Rounds Played: {total_rounds}", game.font_norm, game.LIGHT)
    center_line(f"Wins: {wins}   |   Losses: {losses}", game.font_norm, game.LIGHT)
    center_line(f"Total Bet: {total_stake}$", game.font_norm, game.LIGHT)
    center_line(f"Net Gain: {net_gain}$",
                game.font_norm, game.GREEN if net_gain >= 0 else game.RED)
    center_line(f"Average Round Time: {avg_time:.2f} s", game.font_norm, game.LIGHT)

    y += 10
    title_surf = game.font_small.render("Round Breakdown:", True, game.LIGHT)
    game.screen.blit(title_surf, title_surf.get_rect(midleft=(panel_rect.x + 30, y)))
    y += 22

    col_x = {
        "n": panel_rect.x + 40,
        "bet": panel_rect.x + 90,
        "mult": panel_rect.x + 150,
        "res": panel_rect.x + 230,
        "time": panel_rect.x + 320,
        "bal": panel_rect.x + 410,
    }

    header_color = game.WHITE

    def draw_text(txt, x, y2, align="left", font=None, color=header_color):
        if font is None:
            font = game.font_small
        surf = font.render(txt, True, color)
        rect = surf.get_rect()
        if align == "left":
            rect.topleft = (x, y2)
        elif align == "center":
            rect.midtop = (x, y2)
        game.screen.blit(surf, rect)

    draw_text("#",      col_x["n"],   y)
    draw_text("Bet",    col_x["bet"], y)
    draw_text("x",      col_x["mult"], y)
    draw_text("Result", col_x["res"], y)
    draw_text("Time",   col_x["time"], y)
    draw_text("Capital", col_x["bal"], y)
    y += 4

    pygame.draw.line(game.screen, game.LIGHT,
                     (panel_rect.x + 30, y + 18),
                     (panel_rect.right - 30, y + 18), 1)
    y += 24

    last_rounds = game.round_history[-6:]
    for r in last_rounds:
        draw_text(str(r["round"]),          col_x["n"],   y)
        draw_text(f"{r['bet']}$",           col_x["bet"], y)
        draw_text(f"x{r['mult']}",          col_x["mult"], y)
        draw_text(r["result"],              col_x["res"], y)
        draw_text(f"{r['duration']:.2f}",   col_x["time"], y)
        draw_text(f"{r['balance_after']}$", col_x["bal"], y)
        y += 20

    _draw_button(game, game.btn_main_menu, "Main menu", game.GREEN, game.BLACK)
    _draw_button(game, game.btn_exit, "Quit", game.RED, game.WHITE)


