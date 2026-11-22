"""                                   ╔═══════════════════════════════════════════════════════╗
                                        ║   Rouge Gagne, Noir Perd – 2025/2026                                                  ║    
                                        ║   Author: Denos KUME                                                                                 ║
                                        ║   Collaborator: Sena FUKABE                                                                     ║
                                        ║   Program: M1 CORO DASSIP                                                                     ║
                                        ║   Instructor: Mira Rizkallah                                                                        ║
                                        ║   Motto: "Code with purpose, build with clarity."                                ║
                                        ╚═══════════════════════════════════════════════════════╝                 
main.py"""

import pygame
import user as us
import bet as bt
import game as gm
import dashboard as db  
"""  
Initializes the game window and creates all domain objects.
- Modules: Imports user, bet, game, and dashboard.
- Logic:
       - Starts Pygame and sets window size and caption.
       - Creates User and Bet instances.
        - Instantiates CardGame with screen, user, and bet.
Entry point for launching the game loop
"""
def main():          
    pygame.init()                 # Initialize Pygame and set window title
    pygame.display.set_caption("Rouge gagne, Noir perd")
    screen = pygame.display.set_mode((960, 630))              # Create game window and clock
    clock = pygame.time.Clock()

    # Create domain objects
    player = us.User(nickname="", avatar_index=0, initial_balance=30)                 # player's initial capital = $30   (freebet)
    betting = bt.Bet(min_amount=10, max_amount=100, amount=10, turbo=1)  # bet range   >= $10 ---- <= $100

    # Create game instance
    card_game = gm.CardGame(screen, player, betting)

    running = True       # main loop flag
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False    # quit game
            else:
                card_game.handle_event(event)  # handle input

        # Update
        card_game.update()   # update state

        # Draw
        card_game.draw()        # render visuals
        pygame.display.flip()  # refresh screen
        clock.tick(60)                # 60 FPS 

    pygame.quit()                    # close pygame

# run only if executed directly | when file is run directly, __name__ == "__main__"
if __name__ == "__main__":    # __name__ is a special Python variable (double underscores = system-defined)
    main()                                    # start the game




"""
                                           ════════════════════════════════════════════════════════
                                               End of file — © Denos KUME, M1 CORO DASSIP (2025–2026)
                                               Collaborator: Sena FUKABE | Instructor: Mira Rizkallah
                                           ════════════════════════════════════════════════════════
"""