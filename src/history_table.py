"""Styled persistent history table for the start screen."""

import pygame

COLUMNS = ("#", "Player", "Bet", "Result", "Cash", "Goal")


def panel_height(viewport_height, panel_y, margin):
    """Use available vertical space while keeping a sensible desktop cap."""
    available = max(180, viewport_height - panel_y - margin)
    return min(330, available)


def visible_row_limit(panel_h, row_h, table_offset=44, bottom_padding=12):
    """Return the maximum number of data rows that fit below the table header."""
    available = max(0, panel_h - table_offset - bottom_padding - row_h)
    return max(1, available // row_h)


def _player_key(row):
    return str(row.get("player", "-") or "-").strip().casefold()


def aggregate_players(history, limit=5):
    """Aggregate every round for each player and return the most recent players."""
    aggregates = {}
    latest_order = []
    for row in history:
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
