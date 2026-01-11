"""Asteroids game main module with strict validation and Tiger Style compliance."""
# pylint: disable=c-extension-no-member,no-member
# Pygame uses C extensions with runtime-only member access

import sys

import pygame
from pydantic import validate_call
from pygame import version

from constants import GAME_AREA
from logger import log_state
from player import Player
from validationfunctions import RectWrapped, SurfaceWrapped

# Tiger Style requirement: Ensure assertions are never disabled
if sys.flags.optimize != 0:
    msg = (  # pylint: disable=invalid-name  # Module-level assignment in guard clause
        "Python optimization mode detected (-O or -OO flag). "
        "Assertions are REQUIRED for Tiger Style compliance. "
        "Never run in optimized mode."
    )
    raise RuntimeError(msg)


@validate_call(validate_return=True)
def print_welcome_message() -> None:
    assert version.ver == "2.6.1", "pygame version must be exactly 2.6.1"
    sys.stdout.write(f"Starting Asteroids with pygame version: {version.ver}\n")
    sys.stdout.write(f"Screen width: {GAME_AREA.SCREEN_WIDTH}\n")
    sys.stdout.write(f"Screen height: {GAME_AREA.SCREEN_HEIGHT}\n")


@validate_call(validate_return=True)
def start_game() -> None:
    game_modules: tuple[int, int] = pygame.init()
    assert isinstance(game_modules, tuple), "pygame.init() must return type tuple"
    success_count, failure_count = game_modules  # Validates exactly 2 elements
    assert success_count > 0, "pygame.init() must have at least one module succeed"
    assert failure_count == 0, "pygame.init() must not have any modules fail"


@validate_call(validate_return=True)
def new_player_center() -> Player:
    player: Player = Player(GAME_AREA.SCREEN_WIDTH / 2, GAME_AREA.SCREEN_HEIGHT / 2)
    return player


@validate_call(validate_return=True)
def fill_background(screen: SurfaceWrapped, color: str) -> RectWrapped:
    assert (
        color in pygame.colordict.THECOLORS
    ), "background color must be listed in pygame.colordict.THECOLORS"

    background: pygame.rect.Rect = screen.object.fill(color)
    assert isinstance(background, pygame.rect.Rect), "screen.fill must return type Rect"

    background_size: tuple[int, int] = screen.object.get_size()
    assert isinstance(background_size, tuple), "get_size must return type tuple"
    width, height = background_size  # Validates exactly 2 elements
    assert width == GAME_AREA.SCREEN_WIDTH, "screen background width must equal game_area width"
    assert height == GAME_AREA.SCREEN_HEIGHT, "screen background height must equal game_area height"

    return RectWrapped.model_validate(background)


def main() -> None:
    """Main game loop with initialization, event handling, and rendering."""
    welcome_message_return: None = print_welcome_message()
    assert welcome_message_return is None, "print_welcome_message must return type None"

    new_game: None = start_game()
    assert new_game is None, "start_game must return type None"

    clock: pygame.time.Clock = pygame.time.Clock()
    assert isinstance(clock, pygame.time.Clock), "pygame.time.Clock must return type Clock"
    dt: float = 0.0

    new_screen: pygame.surface.Surface = pygame.display.set_mode(
        (GAME_AREA.SCREEN_WIDTH, GAME_AREA.SCREEN_HEIGHT),
    )
    assert isinstance(
        new_screen,
        pygame.surface.Surface,
    ), "pygame.display.set_mode must return type Surface"

    wrapped_screen: SurfaceWrapped = SurfaceWrapped.model_validate(new_screen)
    assert isinstance(wrapped_screen, SurfaceWrapped), "model_validate must return SurfaceWrapped"

    # pylint: disable=line-too-long
    updatable: pygame.sprite.Group = (  # type: ignore[type-arg]  # pyright: ignore[reportUnknownVariableType]
        pygame.sprite.Group()
    )
    assert isinstance(updatable, pygame.sprite.Group), "updatable must be a Group"

    drawable: pygame.sprite.Group = (  # type: ignore[type-arg]  # pyright: ignore[reportUnknownVariableType]
        pygame.sprite.Group()
    )
    # pylint: enable=line-too-long
    assert isinstance(drawable, pygame.sprite.Group), "drawable must be a Group"

    Player.containers = (updatable, drawable)  # type: ignore[attr-defined]

    new_player: Player = new_player_center()
    assert isinstance(new_player, Player), "new_player_center() must return type Player"
    assert (
        updatable.has(new_player)  # pyright: ignore[reportUnknownMemberType]
    ), "updatable must contain new_player"
    assert (
        drawable.has(new_player)  # pyright: ignore[reportUnknownMemberType]
    ), "drawable must contain new_player"

    while True:
        log_state_return: None = log_state()  # type: ignore[func-returns-value]
        assert log_state_return is None, "log_state must return type None"

        event_list: list[pygame.event.Event] = pygame.event.get()
        assert isinstance(event_list, list), "pygame.event.get() must return type list"
        for event in event_list:
            if event.type == pygame.QUIT:
                return

        background: RectWrapped = fill_background(wrapped_screen, "black")
        assert isinstance(background, RectWrapped), "fill_background must return type RectWrapped"

        updatable.update(dt)

        player_item: Player
        for player_item in drawable:  # pyright: ignore[reportUnknownVariableType]
            player_item.draw(wrapped_screen)  # pyright: ignore[reportUnknownMemberType]

        pygame.display.flip()

        tick: int = clock.tick(60)
        assert isinstance(tick, int), "clock.tick must return type int"
        assert tick >= 0, "clock.tick must return an integer >= 0"
        dt = tick / 1000


if __name__ == "__main__":
    main()
