"""Asteroids game main module with strict validation and Tiger Style compliance."""
# pylint: disable=c-extension-no-member,no-member
# Pygame uses C extensions with runtime-only member access

import sys

import pygame
from pydantic import validate_call
from pygame import version

from constants import GameArea
from logger import log_state
from player import Player
from validationfunctions import RectWrapped, SurfaceWrapped

# Tiger Style requirement: Ensure assertions are never disabled
if sys.flags.optimize != 0:
    msg = (  # pylint: disable=invalid-name  # Error message variable
        "Python optimization mode detected (-O or -OO flag). "
        "Assertions are REQUIRED for Tiger Style compliance. "
        "Never run in optimized mode."
    )
    raise RuntimeError(msg)


@validate_call(validate_return=True)
def print_welcome_message() -> None:
    """Print game startup information with version and screen dimensions."""
    assert version.ver == "2.6.1", "pygame version must be exactly 2.6.1"
    sys.stdout.write(f"Starting Asteroids with pygame version: {version.ver}\n")
    sys.stdout.write(f"Screen width: {GameArea().SCREEN_WIDTH}\n")
    sys.stdout.write(f"Screen height: {GameArea().SCREEN_HEIGHT}\n")


@validate_call(validate_return=True)
def start_game() -> None:
    """Initialize pygame and validate all modules loaded successfully."""
    game_modules: tuple[int, int] = pygame.init()
    assert isinstance(game_modules, tuple), "pygame.init() must return type tuple"
    success_count, failure_count = game_modules  # Validates exactly 2 elements
    assert success_count > 0, "pygame.init() must have at least one module succeed"
    assert failure_count == 0, "pygame.init() must not have any modules fail"


@validate_call(validate_return=True)
def new_player_center() -> Player:
    """Create a new player at the center of the screen."""
    player: Player = Player(GameArea().SCREEN_WIDTH / 2, GameArea().SCREEN_HEIGHT / 2)
    return player


@validate_call(validate_return=True)
def fill_background(screen: SurfaceWrapped, color: str) -> RectWrapped:
    """Fill screen with specified color and validate dimensions."""
    assert (
        color in pygame.colordict.THECOLORS
    ), "background color must be listed in pygame.colordict.THECOLORS"

    background: pygame.rect.Rect = screen.object.fill(color)

    assert isinstance(background, pygame.rect.Rect)
    background_size: tuple[int, int] = screen.object.get_size()
    assert isinstance(background_size, tuple), "get_size must return type tuple"
    width, height = background_size  # Validates exactly 2 elements
    assert width == GameArea().SCREEN_WIDTH, "screen background width must equal game_area width"
    assert (
        height == GameArea().SCREEN_HEIGHT
    ), "screen background height must equal game_area height"

    return RectWrapped.model_validate(background)


def main() -> None:
    """Main game loop with initialization, event handling, and rendering."""
    welcome_message_return: None = print_welcome_message()
    assert welcome_message_return is None, "print_welcome_message must return type None"

    new_game: None = start_game()
    assert new_game is None, "start_game must return type None"

    clock: pygame.time.Clock = pygame.time.Clock()
    assert isinstance(clock, pygame.time.Clock), "pygame.time.Clock must return type Clock"
    _dt: float = 0.0  # Reserved for future game logic

    new_screen: pygame.surface.Surface = pygame.display.set_mode(
        (GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT),
    )
    assert isinstance(
        new_screen,
        pygame.surface.Surface,
    ), "pygame.display.set_mode must return type Surface"

    wrapped_screen: SurfaceWrapped = SurfaceWrapped.model_validate(new_screen)

    new_player: Player = new_player_center()
    assert isinstance(new_player, Player), "new_player_center() must return type Player"

    while True:
        log_state()

        event_list: list[pygame.event.Event] = pygame.event.get()
        assert isinstance(event_list, list), "pygame.event.get() must return type list"
        for event in event_list:
            if event.type == pygame.QUIT:
                return

        background: RectWrapped = fill_background(wrapped_screen, "black")
        assert isinstance(background, RectWrapped), "fill_background must return type RectWrapped"

        draw_player: None = new_player.draw(wrapped_screen)
        assert draw_player is None, "player.draw must return type None"

        pygame.display.flip()

        tick: int = clock.tick(60)
        assert isinstance(tick, int), "clock.tick must return type int"
        assert tick >= 0, "clock.tick must return an integer >= 0"
        _dt = tick / 1000  # Reserved for future game logic


if __name__ == "__main__":
    main()
