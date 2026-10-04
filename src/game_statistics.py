"""Session statistics expressed as net profit, not gross payout."""


def summarize_rounds(rows: list[dict]) -> dict:
    wins = sum(row['result'] == 'WIN' for row in rows)
    count = len(rows)
    return {'rounds': count, 'wins': wins, 'losses': count - wins,
            'net': sum(row['stake'] if row['result'] == 'WIN' else -row['stake'] for row in rows),
            'win_rate': 100 * wins / count if count else None}
