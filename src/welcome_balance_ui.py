"""Render the one-time welcome balance label on the first bet screen only."""

import pygame


def install(dashboard):
    """Overlay the balance line only when the welcome balance was just granted."""
    original_draw_bet_screen = dashboard.draw_bet_screen

    def draw_bet_screen(game):
        original_draw_bet_screen(game)
        if not getattr(game, "welcome_balance_granted_now", False):
            return

        cfg = dashboard._layout(game)
        width = min(game.w - 2 * cfg["margin"], 820)
        panel = pygame.Rect(
            (game.w - width) // 2,
            cfg["margin"],
            width,
            game.h - 2 * cfg["margin"],
        )
        line_y = panel.y + 76
        cover = pygame.Rect(panel.centerx - 230, line_y - 20, 460, 40)
        pygame.draw.rect(game.screen, (15, 15, 15), cover)
        dashboard._draw_center_text(
            game,
            f"Welcome Balance: {game.user.balance}$",
            line_y,
            game.font_norm,
            game.LIGHT,
        )

    dashboard.draw_bet_screen = draw_bet_screen
