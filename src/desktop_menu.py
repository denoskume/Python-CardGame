"""Desktop-specific menu layout while preserving the existing compact mobile menu."""

import pygame


def install(dashboard):
    """Replace dashboard.draw_menu with a full-size desktop variant."""
    original_draw_menu = dashboard.draw_menu

    def draw_menu(game):
        cfg = dashboard._layout(game)
        if cfg["compact"]:
            return original_draw_menu(game)

        dashboard._sync_card_geometry(game)
        game.screen.fill(game.DARK)

        title_y = cfg["margin"] + max(28, game.font_title.get_height() // 2)
        title_clearance = game.font_title.get_height() // 2 + 18
        dashboard._draw_center_text(game, "GAME MENU", title_y, game.font_title, game.WHITE)

        panel_top = max(96, title_y + title_clearance)
        panel_width = game.w - 2 * cfg["margin"]
        panel = pygame.Rect(
            cfg["margin"],
            panel_top,
            panel_width,
            game.h - panel_top - cfg["margin"],
        )
        pygame.draw.rect(game.screen, (15, 15, 15), panel, border_radius=14)
        pygame.draw.rect(game.screen, game.LIGHT, panel, 2, border_radius=14)

        input_width = min(420, panel.width - 100)
        input_height = max(cfg["min_touch"], 52)
        input_y = panel.y + max(48, int(panel.height * 0.11))
        input_rect = pygame.Rect(
            panel.centerx - input_width // 2,
            input_y,
            input_width,
            input_height,
        )
        pygame.draw.rect(
            game.screen,
            game.WHITE if game.active_input else game.GREY,
            input_rect,
            border_radius=8,
        )
        pygame.draw.rect(game.screen, game.BLACK, input_rect, 2, border_radius=8)

        value = game.user.nickname if game.user.nickname else "Tap here to type..."
        color = game.BLACK if game.user.nickname else (150, 150, 150)
        text = game.font_norm.render(value, True, color)
        game.screen.blit(
            text,
            (input_rect.x + 12, input_rect.centery - text.get_height() // 2),
        )

        avatar_size = int(dashboard._clamp(min(game.w * 0.075, game.h * 0.15), 76, 96))
        spacing = int(dashboard._clamp(game.w * 0.045, 38, 74))
        total_width = 3 * avatar_size + 2 * spacing
        start_x = panel.centerx - total_width // 2
        avatar_y = panel.y + int(panel.height * 0.42)

        game.avatar_rects = [
            pygame.Rect(
                start_x + index * (avatar_size + spacing),
                avatar_y,
                avatar_size,
                avatar_size,
            )
            for index in range(3)
        ]

        for index, rect in enumerate(game.avatar_rects):
            if game.avatar_imgs[index] is not None:
                game.screen.blit(
                    pygame.transform.smoothscale(game.avatar_imgs[index], rect.size),
                    rect,
                )
            pygame.draw.rect(
                game.screen,
                game.GREEN if index == game.user.avatar_index else game.WHITE,
                rect,
                3 if index == game.user.avatar_index else 1,
                border_radius=9,
            )

        enabled = 3 <= len(game.user.nickname.strip()) <= game.player_name_max_len
        btn_w = min(320, panel.width - 100)
        btn_h = max(cfg["min_touch"], 54)
        button_y = min(
            panel.bottom - btn_h - 30,
            avatar_y + avatar_size + max(56, int(panel.height * 0.10)),
        )
        game.btn_continue = pygame.Rect(
            panel.centerx - btn_w // 2,
            button_y,
            btn_w,
            btn_h,
        )
        dashboard._draw_button(
            game,
            game.btn_continue,
            "Next",
            game.GREEN if enabled else game.GREY,
            game.BLACK,
        )

    dashboard.draw_menu = draw_menu
