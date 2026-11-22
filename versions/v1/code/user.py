"""                                   ╔═══════════════════════════════════════════════════════╗
                                        ║   Rouge Gagne, Noir Perd – 2025/2026                                                  ║    
                                        ║   Author: Denos KUME                                                                                 ║
                                        ║   Collaborator: Sena FUKABE                                                                     ║
                                        ║   Program: M1 CORO DASSIP                                                                     ║
                                        ║   Instructor: Mira Rizkallah                                                                        ║
                                        ║   Motto: "Code with purpose, build with clarity."                                ║
                                        ╚═══════════════════════════════════════════════════════╝                 
user.py"""

class User:
    """
    Represents a player profile:
    - nickname
    - avatar index
    - balance (capital)
    """

    def __init__(self, nickname: str = "", avatar_index: int = 0, initial_balance: int = 30):
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
        """
        Add NET PROFIT (stake) to balance.
        - stake is the amount you risked
        - profit = stake
        So: new_balance = old_balance + stake
        """
        self.balance += stake      # <-- NOT 2 * stake
        return stake               # return profit

"""
                                           ════════════════════════════════════════════════════════
                                               End of file — © Denos KUME, M1 CORO DASSIP (2025–2026)
                                               Collaborator: Sena FUKABE | Instructor: Mira Rizkallah
                                           ════════════════════════════════════════════════════════
"""