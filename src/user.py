"""Player domain model.

The User class owns identity and balance state only; UI and game-state
logic remain in the controller and dashboard modules.
"""

class User:
    """Store player identity and balance state for the current session."""

    def __init__(self, nickname: str = "", avatar_index: int = 0, initial_balance: int = 30):
        """Create a player with a selected avatar and starting balance."""
        self.nickname = nickname
        self.avatar_index = avatar_index

        self.initial_balance = initial_balance
        self.balance = initial_balance

    @property
    def name(self) -> str:
        """Trimmed nickname."""
        return self.nickname.strip()

    def reset(self) -> None:
        """Reset balance to initial value."""
        self.balance = self.initial_balance

    def can_afford(self, amount: int) -> bool:
        """Return True if the user has enough capital."""
        return amount <= self.balance

    def apply_loss(self, stake: int) -> int:
        """Subtract stake from balance. Return amount lost (positive)."""
        self.balance -= stake
        return stake

    def apply_win(self, stake: int) -> int:
        """Add the net profit for a winning round and return it."""
        self.balance += stake
        return stake

