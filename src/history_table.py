"""Styled persistent history table for the start screen."""

import pygame

COLUMNS = ("#", "Player", "Bet", "Result", "Cash", "Goal")


def result_kind(row):
    return "positive" if row.get("result") == "WIN" else "negative"


def row_values(row):
    result = row.get("result", "")
    stake = int(row.get("stake", row.get("bet", 0)))
    goal = stake if result == "WIN" else -stake
    return (
        str(row.get("round", "?")),
        str(row.get("player", "-") or "-"),
        f"{int(row.get('bet', 0))}$",
        result,
        f"{int(row.get('balance_after', 0))}$",
        f"{goal:+d}$",
    )


def _cell_color(game, column, value, row):
    if column == "Result":
        return game.GREEN if row.get("result") == "WIN" else game.RED
    if column == "Cash":
        cash = int(row.get("balance_after", 0))
        return game.GREEN if cash > 0 else game.RED if cash < 0 else game.LIGHT
    if column == "Goal":
        return game.GREEN if row.get("result") == "WIN" else game.RED
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

        width = min(game.w - 2 * cfg["margin"], 760)
        panel_h = min(300, int(game.h * 0.42))
        panel = pygame.Rect((game.w - width) // 2, int(game.h * 0.34), width, panel_h)
        pygame.draw.rect(game.screen, (15, 15, 15), panel, border_radius=12)
        pygame.draw.rect(game.screen, game.LIGHT, panel, 2, border_radius=12)

        title = game.font_small.render("Last attempts (all sessions combined):", True, game.LIGHT)
        game.screen.blit(title, (panel.x + 14, panel.y + 10))

        if not game.global_history:
            msg = game.font_small.render("No game has been recorded yet.", True, game.LIGHT)
            game.screen.blit(msg, (panel.x + 14, panel.y + 48))
            return

        rows = game.global_history[-3 if cfg["compact"] else 5:][::-1]
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

        for r_index, row in enumerate(rows):
            values = row_values(row)
            y = table_y + row_h * (r_index + 1)
            x = table_x
            for c_index, (heading, value) in enumerate(zip(COLUMNS, values)):
                rect = pygame.Rect(x, y, col_widths[c_index], row_h)
                pygame.draw.rect(game.screen, (10, 12, 22), rect)
                pygame.draw.rect(game.screen, (45, 55, 85), rect, 1)
                color = _cell_color(game, heading, value, row)
                surf = game.font_small.render(value, True, color)
                game.screen.blit(surf, surf.get_rect(center=rect.center))
                x += col_widths[c_index]

    dashboard.draw_start_screen = draw_start_screen
