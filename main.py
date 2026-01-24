# pylint: disable=c-extension-no-member,no-member

import sys
from typing import Any, cast

import pygame
from pydantic import validate_call
from pygame import version

from asteroid import Asteroid
from asteroidfield import AsteroidField
from circleshape import CircleShape
from constants import GAME_AREA
from logger import log_event, log_state
from player import Player
from shot import Shot
from validationfunctions import RectWrapped, SurfaceWrapped

if sys.flags.optimize != 0:
    msg = (  # pylint: disable=invalid-name
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
    success_count, failure_count = game_modules
    assert success_count > 0, "pygame.init() must have at least one module succeed"
    assert failure_count == 0, "pygame.init() must not have any modules fail"


@validate_call(validate_return=True)
def new_player_center() -> Player:
    player: Player = Player(GAME_AREA.SCREEN_WIDTH / 2, GAME_AREA.SCREEN_HEIGHT / 2)
    return player


@validate_call(validate_return=True)
def initialize_display() -> SurfaceWrapped:
    new_screen: pygame.surface.Surface = pygame.display.set_mode(
        (GAME_AREA.SCREEN_WIDTH, GAME_AREA.SCREEN_HEIGHT),
    )
    assert isinstance(
        new_screen,
        pygame.surface.Surface,
    ), "pygame.display.set_mode must return type Surface"

    wrapped_screen: SurfaceWrapped = SurfaceWrapped.model_validate(new_screen)
    assert isinstance(wrapped_screen, SurfaceWrapped), "model_validate must return SurfaceWrapped"

    return wrapped_screen


def setup_sprite_groups() -> Any:  # noqa: ANN401
    updatable: pygame.sprite.Group = pygame.sprite.Group()  # type: ignore[type-arg]
    drawable: pygame.sprite.Group = pygame.sprite.Group()  # type: ignore[type-arg]
    shots: pygame.sprite.Group = pygame.sprite.Group()  # type: ignore[type-arg]
    asteroids: pygame.sprite.Group = pygame.sprite.Group()  # type: ignore[type-arg]

    for group in (  # pyright: ignore[reportUnknownVariableType]
        updatable,
        drawable,
        shots,
        asteroids,
    ):
        assert isinstance(group, pygame.sprite.Group), "sprite groups must be Group instances"

    Player.containers = (updatable, drawable)  # type: ignore[attr-defined]
    Shot.containers = (shots, updatable, drawable)  # type: ignore[attr-defined]
    Asteroid.containers = (asteroids, updatable, drawable)  # type: ignore[attr-defined]
    AsteroidField.containers = (updatable,)

    return updatable, drawable, shots, asteroids


def create_game_entities(
    updatable: pygame.sprite.Group,  # type: ignore[type-arg]
    drawable: pygame.sprite.Group,  # type: ignore[type-arg]
) -> Player:
    new_player: Player = new_player_center()
    assert isinstance(new_player, Player), "new_player_center() must return type Player"
    assert (
        updatable.has(new_player)  # pyright: ignore[reportUnknownMemberType]
    ), "updatable must contain new_player"
    assert (
        drawable.has(new_player)  # pyright: ignore[reportUnknownMemberType]
    ), "drawable must contain new_player"

    new_asteroid_field: AsteroidField = AsteroidField()
    assert isinstance(
        new_asteroid_field,
        AsteroidField,
    ), "new_asteroid_field must be an AsteroidField"
    assert (
        updatable.has(new_asteroid_field)  # pyright: ignore[reportUnknownMemberType]
    ), "updatable must contain new_asteroid_field"

    return new_player


def check_player_asteroid_collisions(
    asteroids: pygame.sprite.Group,  # type: ignore[type-arg]
    player: Player,
) -> None:
    for asteroid_sprite in asteroids:  # pyright: ignore[reportUnknownVariableType]
        asteroid = cast(Asteroid, asteroid_sprite)
        if asteroid.collides_with(player):
            log_event("player_hit")
            sys.stdout.write("Game over!\n")
            sys.exit()


def draw_all_sprites(
    drawable: pygame.sprite.Group,  # type: ignore[type-arg]
    screen: SurfaceWrapped,
) -> None:
    for drawable_sprite in drawable:  # pyright: ignore[reportUnknownVariableType]
        drawable_item = cast(CircleShape, drawable_sprite)
        drawable_item.draw(screen)  # type: ignore[arg-type]  # pyright: ignore[reportArgumentType]


def check_shot_asteroid_collisions(
    asteroids: pygame.sprite.Group,  # type: ignore[type-arg]
    shots: pygame.sprite.Group,  # type: ignore[type-arg]
) -> None:
    for asteroid_sprite in asteroids:  # pyright: ignore[reportUnknownVariableType]
        some_asteroid = cast(Asteroid, asteroid_sprite)
        for shot_sprite in shots:  # pyright: ignore[reportUnknownVariableType]
            shot = cast(Shot, shot_sprite)
            if shot.collides_with(some_asteroid):
                log_event("asteroid_shot")
                shot.kill()
                some_asteroid.kill()


@validate_call(validate_return=True)
def fill_background(screen: SurfaceWrapped, color: str) -> RectWrapped:
    assert (
        color in pygame.colordict.THECOLORS
    ), "background color must be listed in pygame.colordict.THECOLORS"

    background: pygame.rect.Rect = screen.object.fill(color)
    assert isinstance(background, pygame.rect.Rect), "screen.fill must return type Rect"

    background_size: tuple[int, int] = screen.object.get_size()
    assert isinstance(background_size, tuple), "get_size must return type tuple"
    width, height = background_size
    assert width == GAME_AREA.SCREEN_WIDTH, "screen background width must equal game_area width"
    assert height == GAME_AREA.SCREEN_HEIGHT, "screen background height must equal game_area height"

    return RectWrapped.model_validate(background)


def main() -> None:
    welcome_message_return: None = print_welcome_message()
    assert welcome_message_return is None, "print_welcome_message must return type None"

    new_game: None = start_game()
    assert new_game is None, "start_game must return type None"

    wrapped_screen: SurfaceWrapped = initialize_display()
    updatable, drawable, shots, asteroids = setup_sprite_groups()
    player = create_game_entities(updatable, drawable)

    clock: pygame.time.Clock = pygame.time.Clock()
    assert isinstance(clock, pygame.time.Clock), "pygame.time.Clock must return type Clock"
    dt: float = 0.0

    while True:
        log_state()

        event_list: list[pygame.event.Event] = pygame.event.get()
        assert isinstance(event_list, list), "pygame.event.get() must return type list"
        for event in event_list:
            if event.type == pygame.QUIT:
                return

        background: RectWrapped = fill_background(wrapped_screen, "black")
        assert isinstance(background, RectWrapped), "fill_background must return type RectWrapped"

        updatable.update(dt)

        check_player_asteroid_collisions(asteroids, player)
        check_shot_asteroid_collisions(asteroids, shots)
        draw_all_sprites(drawable, wrapped_screen)

        pygame.display.flip()

        tick: int = clock.tick(60)
        assert isinstance(tick, int), "clock.tick must return type int"
        assert tick >= 0, "clock.tick must return an integer >= 0"
        dt = tick / 1000


if __name__ == "__main__":
    main()
