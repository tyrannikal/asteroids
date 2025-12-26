import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT 
from logger import log_state
from player import Player

def main():
    print(f"Starting Asteroids with pygame version: {pygame.__version__}")

    if(not (type(SCREEN_WIDTH) == int and SCREEN_WIDTH > 0)):
        print(f"{main.__name__}: SCREEN_WIDTH must be an int > 0")
    print(f"Screen width: {SCREEN_WIDTH}")

    if(not (type(SCREEN_HEIGHT) == int and SCREEN_HEIGHT > 0)):
        print(f"{main.__name__}: SCREEN_HEIGHT must be an int > 0")
    print(f"Screen height: {SCREEN_HEIGHT}")

    game_modules = pygame.init()
    if(not (type(game_modules) == tuple and len(game_modules) == 2)):
        print(f"{main.__name__}: pygame.init must return a tuple of length 2")
    if(not (game_modules[0] > 0 and game_modules[1] == 0)):
        print(f"{main.__name__}: pygame.init must have at least 1 module succeed and have 0 failures")

    clock = pygame.time.Clock()
    if(not (type(clock) == pygame.time.Clock)):
        print(f"{main.__name__}: pygame.time.Clock must return a clock")
    dt = 0

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    if(not (type(screen) == pygame.surface.Surface)):
        print(f"{main.__name__}: pygame.display.set_mode must return a Surface type")

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    if(not (type(player) == Player)):
        print(f"{main.__name__}: player must be of type Player")

    while(True):
        current_log_state = log_state()
        if(not (type(current_log_state) == type(None))):
            print(f"{main.__name__}: log_state must return None type")

        event_list = pygame.event.get()
        if(not (type(event_list) == list and len(event_list) >= 0)):
            print(f"{main.__name__}: pygame.event.get must return an list >= 0")
        for event in range(0, len(event_list)):
            if event_list[event].type == pygame.QUIT:
                return

        all_black_surface = screen.fill("black")
        if(not (type(all_black_surface) == pygame.rect.Rect
                and all_black_surface.width == SCREEN_WIDTH
                and all_black_surface.height == SCREEN_HEIGHT)):
            print(f"{main.__name__}: screen.fill must return a Rect with dimensions matching SCREEN_WIDTH and SCREEN_HEIGHT")

        draw_player = player.draw(screen)
        if(not (type(draw_player) == type(None))):        
            print(f"{main.__name__}: player.draw must return None type")

        refresh_screen = pygame.display.flip()
        if(not (type(refresh_screen) == type(None))):
            print(f"{main.__name__}: screen.display.flip must return None type")

        tick = clock.tick(60)
        if(not (type(tick) == int and tick >= 0)):
            print(f"{main.__name__}: clock.tick() must return the int >= 0 milliseconds passed since last tick")
        dt = tick / 1000


if __name__ == "__main__":
    main()

