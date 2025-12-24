import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT 
from logger import log_state

def main():
    print(f"Starting Asteroids with pygame version: {pygame.__version__}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    game_modules = pygame.init()
    if(not (type(game_modules) == tuple and len(game_modules) == 2)):
        print(f"{main.__name__}: pygame.init must return a tuple of length 2")
    if(not (game_modules[0] > 0 and game_modules[1] == 0)):
        print(f"{main.__name__}: pygame.init must have at least 1 module succeed with 0 failures")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    if(not (type(screen) == pygame.surface.Surface)):
        print(f"{main.__name__}: pygame.display.set_mode must return a Surface type")

    while(True):
        current_log_state = log_state()
        if(not (type(current_log_state) == type(None))):
            print(f"{main.__name__}: log_state must return None type")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        all_black_surface = screen.fill("black")
        if(not (type(all_black_surface) == pygame.rect.Rect
                and all_black_surface.width == SCREEN_WIDTH
                and all_black_surface.height == SCREEN_HEIGHT)):
            print(f"{main.__name__}: screen.fill must return a Rect with dimensions matching SCREEN_WIDTH and SCREEN_HEIGHT")

        refresh_screen = pygame.display.flip()
        if(not (type(refresh_screen) == type(None))):
            print(f"{main.__name__}: screen.display.flip must return None type")

if __name__ == "__main__":
    main()

