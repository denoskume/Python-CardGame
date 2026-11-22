"""                                   ╔═══════════════════════════════════════════════════════╗
                                        ║   Rouge Gagne, Noir Perd – 2025/2026                                                  ║    
                                        ║   Author: Denos KUME                                                                                 ║
                                        ║   Collaborator: Sena FUKABE                                                                     ║
                                        ║   Program: M1 CORO DASSIP                                                                     ║
                                        ║   Instructor: Mira Rizkallah                                                                        ║
                                        ║   Motto: "Code with purpose, build with clarity."                                ║
                                        ╚═══════════════════════════════════════════════════════╝                 
bet.py"""

class Bet:
    """
    Represents the betting configuration:
    - min / max bet
    - current bet amount
    - turbo multiplier (X1, X2 or X3)
    """
    def __init__(self, min_amount: int = 10, max_amount: int = 100, amount: int = 10, turbo: int = 1):
        self.min = min_amount
        self.max = max_amount
        self.amount = amount
        self.turbo = turbo  

    # ----- Helpers -----

    def increase(self, step: int = 5, balance: int | None = None) -> None:
        """Increase bet by step, respecting max and optional balance."""
        self.amount += step
        if self.amount > self.max:
            self.amount = self.max
        if balance is not None and self.amount > balance:
            self.amount = balance

    def decrease(self, step: int = 5) -> None:
        """Decrease bet by step, respecting min."""
        self.amount -= step
        if self.amount < self.min:
            self.amount = self.min

    def set_turbo(self, value: int) -> None:
        """Set turbo multiplier (clamped between 1 and 3)."""
        self.turbo = max(1, min(3, int(value)))

    def stake(self) -> int:
        """Total stake for this round = bet * turbo."""
        return self.amount * self.turbo

    def is_valid(self, balance: int) -> bool:
        """Check that bet is inside limits and affordable."""
        return self.min <= self.amount <= self.max and self.amount <= balance

"""
                                           ════════════════════════════════════════════════════════
                                               End of file — © Denos KUME, M1 CORO DASSIP (2025–2026)
                                               Collaborator: Sena FUKABE | Instructor: Mira Rizkallah
                                           ════════════════════════════════════════════════════════
"""