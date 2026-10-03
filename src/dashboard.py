"""Responsive rendering for every CardGame screen."""

import pygame

# QA viewports: 1440x900, 1024x768, 768x1024, 390x844, 844x390
_BASE_CARD_IMAGES = {}
_BASE_AVATARS = {}
_BASE_LOGOS = {}


def _clamp(value, low, high):
    return max(low, min(high, value))


def _layout(game):
    """Return adaptive geometry flags and spacing for the current viewport."""
    portrait = game.h > game.w
    compact = game.w < 700 or game.h < 520
    very_small = game.w <= 430
    scale = _clamp(min(game.w / 960, game.h / 630), 0.65, 1.45)
    margin = int(_clamp(game.w * 0.035, 12, 42))
    min_touch = 48 if compact else 42
    return {
        "portrait": portrait,
        "compact": compact,
        "very_small": very_small,
        "scale": scale,
        "margin": margin,
        "min_touch": min_touch,
    }


def _sync_fonts(game):
    cfg = _layout(game)
    s = cfg["scale"]
    game.font_title = pygame.font.SysFont("arial", int(_clamp(40 * s, 25, 50)), bold=True)
    game.font_big = pygame.font.SysFont("arial", int(_clamp(28 * s, 20, 36)), bold=True)
    game.font_norm = pygame.font.SysFont("arial", int(_clamp(22 * s, 17, 28)))
    game.font_small = pygame.font.SysFont("arial", int(_clamp(18 * s, 14, 22)))
    game.font_mono = pygame.font.SysFont("consolas", int(_clamp(18 * s, 14, 22)))
    game.fonts = {"big": game.font_big, "small": game.font_small}


def _remember_assets(game):
    key = id(game)
    if key not in _BASE_CARD_IMAGES:
        _BASE_CARD_IMAGES[key] = (
            game.card_img_front.copy() if game.card_img_front is not None else None,
            game.card_img_back_red.copy() if game.card_img_back_red is not None else None,
            game.card_img_back_black.copy() if game.card_img_back_black is not None else None,
        )
        _BASE_AVATARS[key] = [img.copy() if img is not None else None for img in game.avatar_imgs]
        _BASE_LOGOS[key] = (
            game.logo_back.copy() if game.logo_back is not None else None,
            game.logo_front.copy() if game.logo_front is not None else None,
        )


def _sync_card_geometry(game):
    """Keep cards readable and tappable across landscape and portrait layouts."""
    _sync_fonts(game)
    _remember_assets(game)
    cfg = _layout(game)
    margin = cfg["margin"]
    gap = int(_clamp(game.w * (0.025 if cfg["portrait"] else 0.04), 8, 60))
    max_w = 180 if not cfg["compact"] else 135
    card_w = int(min(max_w, (game.w - 2 * margin - 2 * gap) / 3))
    card_w = max(78, card_w)
    card_h = int(card_w * 250 / 180)
    max_h = int(game.h * (0.37 if cfg["portrait"] else 0.43))
    if card_h > max_h:
        card_h = max(110, max_h)
        card_w = int(card_h * 180 / 250)

    changed = card_w != game.card_width or card_h != game.card_height or gap != game.card_gap
    game.card_width, game.card_height, game.card_gap = card_w, card_h, gap

    key = id(game)
    front, red, black = _BASE_CARD_IMAGES[key]
    if front is not None:
        game.card_img_front = pygame.transform.smoothscale(front, (card_w, card_h))
        game.card_img_back_red = pygame.transform.smoothscale(red, (card_w, card_h))
        game.card_img_back_black = pygame.transform.smoothscale(black, (card_w, card_h))

    avatar_size = int(_clamp(70 * cfg["scale"], 48, 82))
    game.avatar_imgs = [
        pygame.transform.smoothscale(img, (avatar_size, avatar_size)) if img is not None else None
        for img in _BASE_AVATARS[key]
    ]

    logo_w = int(_clamp(70 * cfg["scale"], 42, 80))
    logo_h = int(logo_w * 100 / 70)
    logo_back, logo_front = _BASE_LOGOS[key]
    game.logo_back = pygame.transform.smoothscale(logo_back, (logo_w, logo_h)) if logo_back is not None else None
    game.logo_front = pygame.transform.smoothscale(logo_front, (logo_w, logo_h)) if logo_front is not None else None

    if changed and game.cards:
        total = 3 * card_w + 2 * gap
        start_x = (game.w - total) // 2
        card_y = int(game.h * (0.48 if cfg["portrait"] else 0.43))
        ordered = sorted(game.cards, key=lambda card: card.rect.centerx)
        for index, card in enumerate(ordered):
            card.rect = pygame.Rect(start_x + index * (card_w + gap), card_y, card_w, card_h)
            card.img_front = game.card_img_front
            card.img_back_red = game.card_img_back_red
            card.img_back_black = game.card_img_back_black
        game.is_swapping = False


def _draw_center_text(game, text, y, font, color):
    surf = font.render(text, True, color)
    game.screen.blit(surf, surf.get_rect(center=(game.w // 2, int(y))))


def _draw_button(game, rect, text, bg_color, text_color):
    pygame.draw.rect(game.screen, bg_color, rect, border_radius=10)
    pygame.draw.rect(game.screen, game.BLACK, rect, 2, border_radius=10)
    label = game.font_norm.render(text, True, text_color)
    game.screen.blit(label, label.get_rect(center=rect.center))


def _draw_circle_timer(game, center, total_ms, elapsed_ms):
    cfg = _layout(game)
    radius = int(_clamp(40 * cfg["scale"], 28, 44))
    pygame.draw.circle(game.screen, game.GREY, center, radius, 3)
    remaining = max(0, total_ms - elapsed_ms)
    seconds = (remaining // 1000) % 60
    txt = game.font_big.render(f"00:{seconds:02d}", True, game.WHITE)
    game.screen.blit(txt, txt.get_rect(center=center))


def _draw_logo_cards(game):
    if game.logo_back is None or game.logo_front is None:
        return
    cfg = _layout(game)
    x = cfg["margin"] + 8
    y = cfg["margin"] + 36
    game.screen.blit(game.logo_back, (x + 28, y - 25))
    game.screen.blit(game.logo_front, (x, y))


def _draw_player_info(game):
    if not game.user.nickname.strip():
        return
    cfg = _layout(game)
    size = 48 if cfg["compact"] else 60
    idx = game.user.avatar_index
    x, y = cfg["margin"], cfg["margin"]
    if game.avatar_imgs[idx] is not None:
        avatar = pygame.transform.smoothscale(game.avatar_imgs[idx], (size, size))
        game.screen.blit(avatar, (x, y))
    name = game.font_big.render(game.user.nickname, True, game.WHITE)
    game.screen.blit(name, (x + size + 12, y + size // 2 - name.get_height() // 2))


def _phase_panel(game, title, subtitle):
    cfg = _layout(game)
    width = min(game.w - 2 * cfg["margin"], 620)
    height = 120 if not cfg["compact"] else 105
    top = cfg["margin"] + (62 if game.user.nickname.strip() else 10)
    rect = pygame.Rect((game.w - width) // 2, top, width, height)
    pygame.draw.rect(game.screen, (15, 15, 15), rect, border_radius=12)
    pygame.draw.rect(game.screen, game.LIGHT, rect, 2, border_radius=12)
    game.screen.blit(game.font_big.render(title, True, game.WHITE), (rect.x + 16, rect.y + 15))
    sub = game.font_small.render(subtitle, True, game.LIGHT)
    game.screen.blit(sub, (rect.x + 16, rect.y + height - sub.get_height() - 15))
    elapsed = pygame.time.get_ticks() - game.state_start_time
    _draw_circle_timer(game, (rect.right - 55, rect.centery), 10_000, elapsed)
    return rect


def draw_pause_overlay(game):
    _sync_card_geometry(game)
    overlay = pygame.Surface((game.w, game.h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    game.screen.blit(overlay, (0, 0))
    _draw_center_text(game, "PAUSE", game.h * 0.42, game.font_title, game.YELLOW)
    _draw_center_text(game, "Press SPACE to resume", game.h * 0.50, game.font_norm, game.LIGHT)


def draw_start_screen(game):
    _sync_card_geometry(game)
    cfg = _layout(game)
    game.screen.fill(game.DARK)
    _draw_logo_cards(game)
    _draw_center_text(game, "ROUGE GAGNE, NOIR PERD", game.h * 0.20, game.font_title, game.WHITE)
    _draw_center_text(game, "Tap or click to continue", game.h * 0.29, game.font_norm, game.LIGHT)

    width = min(game.w - 2 * cfg["margin"], 680)
    panel_h = min(240, int(game.h * 0.36))
    panel = pygame.Rect((game.w - width) // 2, int(game.h * 0.38), width, panel_h)
    pygame.draw.rect(game.screen, (15, 15, 15), panel, border_radius=12)
    pygame.draw.rect(game.screen, game.LIGHT, panel, 2, border_radius=12)
    title = game.font_small.render("Recent attempts", True, game.LIGHT)
    game.screen.blit(title, (panel.x + 16, panel.y + 12))
    if not game.global_history:
        msg = game.font_small.render("No game has been recorded yet.", True, game.LIGHT)
        game.screen.blit(msg, (panel.x + 16, panel.y + 48))
        return
    rows = game.global_history[-3 if cfg["compact"] else 5:][::-1]
    y = panel.y + 46
    for row in rows:
        text = f"#{row.get('round','?')}  {row.get('player','-') or '-'}  {row.get('result','')}  {row.get('bet',0)}$ ×{row.get('mult',1)}  → {row.get('balance_after',0)}$"
        surf = game.font_small.render(text, True, game.LIGHT)
        game.screen.blit(surf, (panel.x + 16, y))
        y += surf.get_height() + 8


def draw_menu(game):
    _sync_card_geometry(game)
    cfg = _layout(game)
    game.screen.fill(game.DARK)
    _draw_center_text(game, "GAME MENU", cfg["margin"] + 28, game.font_title, game.WHITE)
    width = min(game.w - 2 * cfg["margin"], 760)
    panel_top = 90 if game.h >= 600 else 62
    panel = pygame.Rect((game.w - width) // 2, panel_top, width, game.h - panel_top - cfg["margin"])
    pygame.draw.rect(game.screen, (15, 15, 15), panel, border_radius=14)
    pygame.draw.rect(game.screen, game.LIGHT, panel, 2, border_radius=14)

    input_width = min(300, game.w - 2 * cfg["margin"] - 30)
    input_rect = pygame.Rect(game.w // 2 - input_width // 2, 155, input_width, cfg["min_touch"])
    pygame.draw.rect(game.screen, game.WHITE if game.active_input else game.GREY, input_rect, border_radius=8)
    pygame.draw.rect(game.screen, game.BLACK, input_rect, 2, border_radius=8)
    value = game.user.nickname if game.user.nickname else "Tap here to type..."
    color = game.BLACK if game.user.nickname else (150, 150, 150)
    txt = game.font_norm.render(value, True, color)
    game.screen.blit(txt, (input_rect.x + 10, input_rect.centery - txt.get_height() // 2))

    avatar_size = int(_clamp(game.w * 0.16, 54, 74))
    spacing = max(16, int(game.w * 0.04))
    total = 3 * avatar_size + 2 * spacing
    start = (game.w - total) // 2
    avatar_y = input_rect.bottom + 54
    game.avatar_rects = [pygame.Rect(start + i * (avatar_size + spacing), avatar_y, avatar_size, avatar_size) for i in range(3)]
    for idx, rect in enumerate(game.avatar_rects):
        if game.avatar_imgs[idx] is not None:
            game.screen.blit(pygame.transform.smoothscale(game.avatar_imgs[idx], rect.size), rect)
        pygame.draw.rect(game.screen, game.GREEN if idx == game.user.avatar_index else game.WHITE, rect, 3 if idx == game.user.avatar_index else 1, border_radius=9)

    enabled = 3 <= len(game.user.nickname.strip()) <= game.player_name_max_len
    btn_w = min(240, game.w - 2 * cfg["margin"] - 30)
    game.btn_continue = pygame.Rect((game.w - btn_w) // 2, min(panel.bottom - cfg["min_touch"] - 22, avatar_y + avatar_size + 70), btn_w, max(cfg["min_touch"], 50))
    _draw_button(game, game.btn_continue, "Next", game.GREEN if enabled else game.GREY, game.BLACK)


def draw_bet_screen(game):
    _sync_card_geometry(game)
    cfg = _layout(game)
    game.screen.fill(game.DARK)
    width = min(game.w - 2 * cfg["margin"], 820)
    panel = pygame.Rect((game.w - width) // 2, cfg["margin"], width, game.h - 2 * cfg["margin"])
    pygame.draw.rect(game.screen, (15, 15, 15), panel, border_radius=14)
    pygame.draw.rect(game.screen, game.LIGHT, panel, 2, border_radius=14)
    _draw_center_text(game, f"Hello {game.user.nickname}!", panel.y + 35, game.font_big, game.WHITE)
    _draw_center_text(game, f"Balance: {game.user.balance}$", panel.y + 76, game.font_norm, game.LIGHT)

    y = panel.y + 118
    _draw_center_text(game, "Turbo", y, game.font_norm, game.WHITE)
    button_w = int(_clamp((panel.width - 80) / 3, 70, 110))
    gap = int(_clamp(panel.width * 0.035, 10, 24))
    total = 3 * button_w + 2 * gap
    start_x = panel.centerx - total // 2
    game.attempt_rects = []
    for idx, mult in enumerate((1, 2, 3)):
        rect = pygame.Rect(start_x + idx * (button_w + gap), y + 28, button_w, cfg["min_touch"])
        game.attempt_rects.append(rect)
        affordable = game.bet.amount * mult <= game.user.balance
        selected = game.bet.turbo == mult
        color = game.GREEN if selected and affordable else game.GREY if affordable else (40, 40, 40)
        _draw_button(game, rect, f"×{mult}", color, game.BLACK if affordable else game.LIGHT)

    y += 100
    _draw_center_text(game, f"Bet: {game.bet.amount}$", y, game.font_big, game.WHITE)
    side = cfg["min_touch"]
    minus = pygame.Rect(panel.centerx - 120, y + 30, side, side)
    plus = pygame.Rect(panel.centerx + 120 - side, y + 30, side, side)
    game._bet_minus_rect, game._bet_plus_rect = minus, plus
    _draw_button(game, minus, "−", game.RED, game.WHITE)
    _draw_button(game, plus, "+", game.GREEN, game.WHITE)

    can_start = game.bet.is_valid(game.user.balance)
    btn_w = min(260, panel.width - 40)
    game.btn_start_round = pygame.Rect(panel.centerx - btn_w // 2, panel.bottom - cfg["min_touch"] - 20, btn_w, max(cfg["min_touch"], 50))
    _draw_button(game, game.btn_start_round, "START", game.GREEN if can_start else game.GREY, game.BLACK)


def _draw_phase_cards(game, title, subtitle):
    _sync_card_geometry(game)
    game.screen.fill(game.DARK)
    _draw_player_info(game)
    panel = _phase_panel(game, title, subtitle)
    if game.cards and max(card.rect.bottom for card in game.cards) > game.h - 15:
        offset = max(card.rect.bottom for card in game.cards) - (game.h - 15)
        for card in game.cards:
            card.rect.y -= offset
    for card in game.cards:
        card.img_front = game.card_img_front
        card.img_back_red = game.card_img_back_red
        card.img_back_black = game.card_img_back_black
        card.draw(game.screen, game.fonts)
    return panel


def draw_show_backs(game):
    _draw_phase_cards(game, "Step 1: watch the red card", "Cards are visible for 10 seconds.")


def draw_shuffle(game):
    _draw_phase_cards(game, "Step 2: card shuffling", "Track the red card as the positions change.")


def draw_choose(game):
    _draw_phase_cards(game, "Step 3: make your choice", "Tap a card before the timer ends.")
    if game.selected_card_rect is not None:
        pygame.draw.rect(game.screen, game.YELLOW, game.selected_card_rect.inflate(8, 8), 4, border_radius=12)


def draw_result(game):
    _sync_card_geometry(game)
    cfg = _layout(game)
    game.screen.fill(game.DARK)
    title = "WON!" if game.round_result == "WIN" else "LOST..."
    color = game.GREEN if game.round_result == "WIN" else game.RED
    _draw_center_text(game, title, cfg["margin"] + 30, game.font_title, color)

    last = game.round_history[-1] if game.round_history else {}
    summary = f"Balance {game.user.balance}$   •   Bet {game.bet.amount}$ ×{game.bet.turbo}   •   {last.get('duration', 0):.2f}s"
    _draw_center_text(game, summary, cfg["margin"] + 76, game.font_small, game.LIGHT)

    for card in game.cards:
        card.draw(game.screen, game.fonts)
    if game.selected_card_rect is not None:
        pygame.draw.rect(game.screen, game.YELLOW, game.selected_card_rect.inflate(8, 8), 4, border_radius=12)

    button_h = max(cfg["min_touch"], 50)
    gap = 12
    labels = [("Menu", game.btn_main_menu, game.LIGHT), ("New round", game.btn_continue, game.GREEN), ("Quit", game.btn_exit, game.RED)]
    if cfg["portrait"] or game.w < 700:
        width = min(260, game.w - 2 * cfg["margin"])
        y = game.h - (button_h * 3 + gap * 2 + cfg["margin"])
        for label, rect, fill in labels:
            rect.update((game.w - width) // 2, y, width, button_h)
            if label != "New round" or game.user.balance >= game.bet.min:
                _draw_button(game, rect, label, fill, game.BLACK if fill != game.RED else game.WHITE)
            y += button_h + gap
    else:
        width = min(200, (game.w - 2 * cfg["margin"] - 2 * gap) // 3)
        total = 3 * width + 2 * gap
        x = (game.w - total) // 2
        y = game.h - button_h - cfg["margin"]
        for label, rect, fill in labels:
            rect.update(x, y, width, button_h)
            if label != "New round" or game.user.balance >= game.bet.min:
                _draw_button(game, rect, label, fill, game.BLACK if fill != game.RED else game.WHITE)
            x += width + gap


def draw_game_over(game):
    _sync_card_geometry(game)
    cfg = _layout(game)
    game.screen.fill(game.DARK)
    _draw_center_text(game, "GAME OVER", cfg["margin"] + 34, game.font_title, game.RED)
    total = len(game.round_history)
    wins = sum(1 for row in game.round_history if row["result"] == "WIN")
    losses = total - wins
    net = sum((row["stake"] * 2 if row["result"] == "WIN" else -row["stake"]) for row in game.round_history)
    lines = [
        f"Rounds: {total}",
        f"Wins: {wins}   Losses: {losses}",
        f"Final balance: {game.user.balance}$",
        f"Net gain: {net}$",
    ]
    y = int(game.h * 0.24)
    for line in lines:
        _draw_center_text(game, line, y, game.font_norm, game.LIGHT)
        y += game.font_norm.get_height() + 16

    button_h = max(cfg["min_touch"], 50)
    width = min(250, game.w - 2 * cfg["margin"])
    game.btn_main_menu.update((game.w - width) // 2, game.h - 2 * button_h - cfg["margin"] - 12, width, button_h)
    game.btn_exit.update((game.w - width) // 2, game.h - button_h - cfg["margin"], width, button_h)
    _draw_button(game, game.btn_main_menu, "Main menu", game.GREEN, game.BLACK)
    _draw_button(game, game.btn_exit, "Quit", game.RED, game.WHITE)
