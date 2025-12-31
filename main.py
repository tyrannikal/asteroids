from pydantic import validate_call
import pygame
from pygame import version

from constants import GameArea
from validationfunctions import SurfaceWrapped, RectWrapped
from logger import log_state
from player import Player


@validate_call(validate_return=True)
def PrintWelcomeMessage() -> None:
    assert version.ver == "2.6.1", "pygame version must be exactly 2.6.1"
    print(f"Starting Asteroids with pygame version: {version.ver}")
    print(f"Screen width: {GameArea().SCREEN_WIDTH}")
    print(f"Screen height: {GameArea().SCREEN_HEIGHT}")
    return None


@validate_call(validate_return=True)
def StartGame() -> None:
    game_modules: tuple = pygame.init()
    assert type(game_modules) == tuple, "pygame.init() must return type tuple"
    assert len(game_modules) == 2, "pygame.init() must return a tuple of length 2"
    assert game_modules[0] > 0, "pygame.init() must have at least one module succeed"
    assert game_modules[1] == 0, "pygame.init() must not have any modules fail"
    return None


@validate_call(validate_return=True)
def NewPlayerCenter() -> Player:
    player: Player = Player(GameArea().SCREEN_WIDTH / 2, GameArea().SCREEN_HEIGHT / 2)
    return player


@validate_call(validate_return=True)
def FillBackground(screen: SurfaceWrapped, color: str) -> RectWrapped:
    assert color in pygame.colordict.THECOLORS, (
        "background color must be listed in pygame.colordict.THECOLORS"
    )

    background: pygame.rect.Rect = screen.object.fill(color)

    assert type(background) == pygame.rect.Rect
    background_size: tuple = pygame.Surface.get_size(screen.object)
    assert type(background_size) == tuple, "get_size must return type tuple"
    assert len(background_size) == 2, "get_size must return a tuple of length 2"
    assert background_size[0] == GameArea().SCREEN_WIDTH, (
        "screen background width must equal game_area width"
    )
    assert background_size[1] == GameArea().SCREEN_HEIGHT, (
        "screen background height must equal game_area height"
    )

    return RectWrapped.model_validate(background)


def main() -> None:
    welcome_message_return: None = PrintWelcomeMessage()
    assert welcome_message_return == None, "PrintWelcomeMessage must return type None"

    new_game: None = StartGame()
    assert new_game == None, "StartGame must return type None"

    clock: pygame.time.Clock = pygame.time.Clock()
    assert type(clock) == pygame.time.Clock, "pygame.time.Clock must return type Clock"
    dt: float = 0.0

    new_screen: pygame.surface.Surface = pygame.display.set_mode(
        (GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT)
    )
    assert type(new_screen) == pygame.surface.Surface, (
        "pygame.display.set_mode must return type Surface"
    )

    wrapped_screen: SurfaceWrapped = SurfaceWrapped.model_validate(new_screen)

    new_player: Player = NewPlayerCenter()
    assert type(new_player) == Player, "NewPlayerCenter() must return type Player"

    while True:
        log_current_state: None = log_state()
        assert log_current_state == None, "log_state() must return type None"

        event_list: list = pygame.event.get()
        assert type(event_list) == list, "pygame.event.get() must return type list"
        for event in event_list:
            if event.type == pygame.QUIT:
                return None

        background: RectWrapped = FillBackground(wrapped_screen, "black")
        assert type(background) == RectWrapped, "FillBackground must return type RectWrapped"

        draw_player: None = new_player.draw(wrapped_screen)
        assert draw_player == None, "player.draw must return type None"

        pygame.display.flip()

        tick: int = clock.tick(60)
        assert type(tick) == int, "clock.tick must return type int"
        assert tick >= 0, "clock.tick must return an inteter >= 0"
        dt = tick / 1000


if __name__ == "__main__":
    main()
