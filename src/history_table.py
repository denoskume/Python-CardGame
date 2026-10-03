"""Styled persistent history table for the start screen."""

import pygame

COLUMNS = ("#", "Player", "Occ.", "Bet", "Result", "Cash", "Goal")


def _player_key(name):
    return str(name or "-").strip().casefold()


def summarize_players(history, limit=5):
    """Return one summary per player, ordered by most recent activity."""
    summaries = {}
    latest_order = []

    for row in history:
        player = str(row.get("player", "-") or "-").strip() or "-"
        key = _player_key(player)
        if key not in summaries:
            summaries[key] = {
                "player": player,
                "occurrences": 0,
                "total_bet": 0,
                "wins": 0,
                "losses": 0,
                "cash": 0,
                "goal": 0,
            }
        summary = summaries[key]
        summary["player"] = player
        summary["occurrences"] += 1
        summary["total_bet"] += int(row.get("bet", 0))
        result = row.get("result", "")
        stake = int(row.get("stake", row.get("bet", 0)))
        if result == "WIN":
            summary["wins"] += 1
            summary["goal"] += stake
        elif result == "LOSE":
            summary["losses"] += 1
            summary["goal"] -= stake
        summary["cash"] = int(row.get("balance_after", summary["cash"]))

        if key in latest_order:
            latest_order.remove(key)
        latest_order.append(key)

    return [summaries[key] for key in reversed(latest_order[-limit:])]


def result_kind(summary):
    if summary.get("wins", 0) > summary.get("losses", 0):
        return "positive"
    if summary.get("wins", 0) < summary.get("losses", 0):
        return "negative"
    return "neutral"


def row_values(summary, rank):
    return (
        str(rank),
        str(summary.get("player", "-") or "-"),
        str(int(summary.get("occurrences", 0))),
        f"{int(summary.get('total_bet', 0))}$",
        f"{int(summary.get('wins', 0))}W / {int(summary.get('losses', 0))}L",
        f"{int(summary.get('cash', 0))}$",
        f"{int(summary.get('goal', 0)):+d}$",
    )


def _cell_color(game, column, value, summary):
    if column == "Result":
        kind = result_kind(summary)
        return game.GREEN if kind == "positive" else game.RED if kind == "negative" else game.LIGHT
    if column == "Cash":
        cash = int(summary.get("cash", 0))
        return game.GREEN if cash > 0 else game.RED if cash < 0 else game.LIGHT
    if column == "Goal":
        goal = int(summary.get("goal", 0))
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
        panel_h = min(270, int(game.h * 0.40))
        panel = pygame.Rect((game.w - width) // 2, int(game.h * 0.34), width, panel_h)
        pygame.draw.rect(game.screen, (15, 15, 15), panel, border_radius=12)
        pygame.draw.rect(game.screen, game.LIGHT, panel, 2, border_radius=12)

        title = game.font_small.render("Last attempts (all sessions combined):", True, game.LIGHT)
        game.screen.blit(title, (panel.x + 14, panel.y + 10))

        if not game.global_history:
            msg = game.font_small.render("No game has been recorded yet.", True, game.LIGHT)
            game.screen.blit(msg, (panel.x + 14, panel.y + 48))
            return

        rows = summarize_players(game.global_history, limit=5)
        table_x = panel.x + 12
        table_y = panel.y + 44
        table_w = panel.width - 24
        row_h = max(28, int(game.font_small.get_height() * 1.55))
        col_fracs = (0.06, 0.20, 0.10, 0.13, 0.20, 0.15, 0.16)
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

        for r_index, summary in enumerate(rows, start=1):
            values = row_values(summary, r_index)
            y = table_y + row_h * r_index
            x = table_x
            for c_index, (heading, value) in enumerate(zip(COLUMNS, values)):
                rect = pygame.Rect(x, y, col_widths[c_index], row_h)
                pygame.draw.rect(game.screen, (10, 12, 22), rect)
                pygame.draw.rect(game.screen, (45, 55, 85), rect, 1)
                color = _cell_color(game, heading, value, summary)
                surf = game.font_small.render(value, True, color)
                game.screen.blit(surf, surf.get_rect(center=rect.center))
                x += col_widths[c_index]

    dashboard.draw_start_screen = draw_start_screen
