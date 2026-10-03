"""Styled persistent history table for the start screen."""

import pygame

COLUMNS = ("#", "Player", "Bet", "Result", "Cash", "Goal")


def _event_key(row):
    """Build a stable identity for an exact recorded round."""
    return (
        row.get("round"),
        str(row.get("player", "-") or "-").strip().casefold(),
        int(row.get("bet", 0)),
        int(row.get("stake", row.get("bet", 0))),
        str(row.get("result", "")),
        int(row.get("balance_after", 0)),
    )


def _player_key(row):
    return str(row.get("player", "-") or "-").strip().casefold()


def aggregate_players(history, limit=5):
    """Aggregate every round for each player and return the five most recent players."""
    unique_events = []
    seen_events = set()
    for row in history:
        key = _event_key(row)
        if key in seen_events:
            continue
        seen_events.add(key)
        unique_events.append(row)

    aggregates = {}
    latest_order = []
    for row in unique_events:
        player_key = _player_key(row)
        player_name = str(row.get("player", "-") or "-").strip() or "-"
        result = str(row.get("result", "")).upper()
        bet = int(row.get("bet", 0))
        stake = int(row.get("stake", bet))
        signed_goal = stake if result == "WIN" else -stake if result == "LOSE" else 0

        if player_key not in aggregates:
            aggregates[player_key] = {
                "player": player_name,
                "total_bet": 0,
                "wins": 0,
                "losses": 0,
                "cash": 0,
                "goal": 0,
            }
        aggregate = aggregates[player_key]
        aggregate["player"] = player_name
        aggregate["total_bet"] += bet
        aggregate["wins"] += 1 if result == "WIN" else 0
        aggregate["losses"] += 1 if result == "LOSE" else 0
        aggregate["cash"] = int(row.get("balance_after", aggregate["cash"]))
        aggregate["goal"] += signed_goal

        if player_key in latest_order:
            latest_order.remove(player_key)
        latest_order.append(player_key)

    return [aggregates[key] for key in reversed(latest_order[-limit:])]


def row_values(row, display_index=1):
    return (
        str(display_index),
        str(row.get("player", "-") or "-"),
        f"{int(row.get('total_bet', 0))}$",
        f"{int(row.get('wins', 0))}W / {int(row.get('losses', 0))}L",
        f"{int(row.get('cash', 0))}$",
        f"{int(row.get('goal', 0)):+d}$",
    )


def _cell_color(game, column, row):
    if column == "Result":
        wins = int(row.get("wins", 0))
        losses = int(row.get("losses", 0))
        return game.GREEN if wins > losses else game.RED if losses > wins else game.LIGHT
    if column == "Cash":
        cash = int(row.get("cash", 0))
        return game.GREEN if cash > 0 else game.RED if cash < 0 else game.LIGHT
    if column == "Goal":
        goal = int(row.get("goal", 0))
        return game.GREEN if goal > 0 else game.RED if goal < 0 else game.LIGHT
    return game.LIGHT


def install(dashboard):
    """Replace the start-screen history list with a compact colored table."""
    def draw_start_screen(game):
        dashboard._sync_card_geometry(game)
        cfg = dashboard._layout(game)
        game.screen.fill(game.DARK)
        dashboard._draw_logo_cards(game)
        dashboard._draw_center_text(game, "ROUGE GAGNE, NOIR PERD", game.h * 0.18, game.font_title, game.WHITE)
        dashboard._draw_center_text(game, "Tap or click to continue", game.h * 0.27, game.font_norm, game.LIGHT)

        width = min(game.w - 2 * cfg["margin"], 820)
        panel_h = min(245, int(game.h * 0.37))
        panel = pygame.Rect((game.w - width) // 2, int(game.h * 0.34), width, panel_h)
        pygame.draw.rect(game.screen, (15, 15, 15), panel, border_radius=12)
        pygame.draw.rect(game.screen, game.LIGHT, panel, 2, border_radius=12)

        title = game.font_small.render("Last attempts (all sessions combined):", True, game.LIGHT)
        game.screen.blit(title, (panel.x + 14, panel.y + 10))

        if not game.global_history:
            msg = game.font_small.render("No game has been recorded yet.", True, game.LIGHT)
            game.screen.blit(msg, (panel.x + 14, panel.y + 48))
            return

        rows = aggregate_players(game.global_history, limit=5)
        table_x = panel.x + 12
        table_y = panel.y + 44
        table_w = panel.width - 24
        row_h = max(28, int(game.font_small.get_height() * 1.55))
        col_fracs = (0.08, 0.22, 0.14, 0.18, 0.19, 0.19)
        col_widths = [int(table_w * f) for f in col_fracs]
        col_widths[-1] = table_w - sum(col_widths[:-1])

        x = table_x
        for idx, heading in enumerate(COLUMNS):
            rect = pygame.Rect(x, table_y, col_widths[idx], row_h)
            pygame.draw.rect(game.screen, (18, 22, 35), rect)
            pygame.draw.rect(game.screen, (55, 65, 95), rect, 1)
            surf = game.font_small.render(heading, True, game.WHITE)
            game.screen.blit(surf, surf.get_rect(center=rect.center))
            x += col_widths[idx]

        for r_index, row in enumerate(rows, start=1):
            values = row_values(row, display_index=r_index)
            y = table_y + row_h * r_index
            x = table_x
            for c_index, (heading, value) in enumerate(zip(COLUMNS, values)):
                rect = pygame.Rect(x, y, col_widths[c_index], row_h)
                pygame.draw.rect(game.screen, (10, 12, 22), rect)
                pygame.draw.rect(game.screen, (45, 55, 85), rect, 1)
                color = _cell_color(game, heading, row)
                surf = game.font_small.render(value, True, color)
                game.screen.blit(surf, surf.get_rect(center=rect.center))
                x += col_widths[c_index]

    dashboard.draw_start_screen = draw_start_screen
