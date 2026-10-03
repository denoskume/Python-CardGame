"""Selected-avatar display and return navigation for the bet screen."""

import pygame


def install(dashboard, game_module):
    """Add the chosen avatar and a responsive return button to STATE_BET."""
    original_draw_bet_screen = dashboard.draw_bet_screen
    original_handle_bet_event = game_module.CardGame.handle_bet_event

    def draw_bet_screen(game):
        original_draw_bet_screen(game)
        cfg = dashboard._layout(game)
        width = min(game.w - 2 * cfg["margin"], 820)
        panel = pygame.Rect(
            (game.w - width) // 2,
            cfg["margin"],
            width,
            game.h - 2 * cfg["margin"],
        )

        avatar_size = int(dashboard._clamp(82 * cfg["scale"], 58, 96))
        avatar_x = panel.x + 22
        avatar_y = panel.y + 22
        game.bet_avatar_rect = pygame.Rect(avatar_x, avatar_y, avatar_size, avatar_size)

        avatar_index = max(0, min(game.user.avatar_index, len(game.avatar_imgs) - 1))
        avatar = game.avatar_imgs[avatar_index]
        if avatar is not None:
            scaled = pygame.transform.smoothscale(avatar, game.bet_avatar_rect.size)
            game.screen.blit(scaled, game.bet_avatar_rect)
        pygame.draw.rect(game.screen, game.LIGHT, game.bet_avatar_rect, 2, border_radius=10)

        button_h = max(cfg["min_touch"], 50)
        return_w = int(dashboard._clamp(panel.width * 0.18, 108, 150))
        start_top = game.btn_start_round.y
        if cfg["compact"] or panel.width < 600:
            return_y = max(panel.y + 130, start_top - button_h - 12)
        else:
            return_y = game.btn_start_round.y

        game.btn_bet_return = pygame.Rect(
            panel.x + 22,
            return_y,
            return_w,
            button_h,
        )
        dashboard._draw_button(
            game,
            game.btn_bet_return,
            "← Return",
            game.GREY,
            game.WHITE,
        )

    def handle_bet_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return_rect = getattr(self, "btn_bet_return", None)
            if return_rect is not None and return_rect.collidepoint(event.pos):
                self.state = game_module.STATE_MENU
                return
        original_handle_bet_event(self, event)

    dashboard.draw_bet_screen = draw_bet_screen
    game_module.CardGame.handle_bet_event = handle_bet_event
