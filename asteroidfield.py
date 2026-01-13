import random
from collections.abc import Callable
from typing import Any, ClassVar, cast

import pygame
from pydantic import validate_call
from pydantic_core import core_schema

from asteroid import Asteroid
from constants import ASTEROID_STATS, GAME_AREA
from validationfunctions import Vector2Wrapped


class AsteroidField(pygame.sprite.Sprite):
    containers: tuple[pygame.sprite.Group[Any], ...]

    edges: ClassVar[list[list[pygame.Vector2 | Callable[[float], pygame.Vector2]]]] = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(
                -ASTEROID_STATS.ASTEROID_MAX_RADIUS,  # pylint: disable=invalid-unary-operand-type
                y * GAME_AREA.SCREEN_HEIGHT,
            ),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                GAME_AREA.SCREEN_WIDTH + ASTEROID_STATS.ASTEROID_MAX_RADIUS,
                y * GAME_AREA.SCREEN_HEIGHT,
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(
                x * GAME_AREA.SCREEN_WIDTH,
                -ASTEROID_STATS.ASTEROID_MAX_RADIUS,  # pylint: disable=invalid-unary-operand-type
            ),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * GAME_AREA.SCREEN_WIDTH,
                GAME_AREA.SCREEN_HEIGHT + ASTEROID_STATS.ASTEROID_MAX_RADIUS,
            ),
        ],
    ]

    def __init__(self) -> None:
        pygame.sprite.Sprite.__init__(self, self.containers)  # type: ignore[arg-type]
        self.spawn_timer: float = 0.0

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,  # noqa: ANN401
        _handler: Any,  # noqa: ANN401
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_before_validator_function(
            cls._validate,
            schema=core_schema.any_schema(),
        )

    @staticmethod
    def _validate(value: Any) -> "AsteroidField":  # noqa: ANN401
        if not isinstance(value, AsteroidField):
            msg = "must be of type AsteroidField"
            raise TypeError(msg)
        return value

    @validate_call(validate_return=True)
    def spawn(self, radius: int, position: Vector2Wrapped, velocity: Vector2Wrapped) -> None:
        asteroid: Asteroid = Asteroid(position.object.x, position.object.y, radius)
        assert isinstance(asteroid, Asteroid), "Asteroid must return an Asteroid"
        asteroid.velocity = velocity.object

    @validate_call(validate_return=True)
    def update(self, dt: float) -> None:
        self.spawn_timer += dt
        if self.spawn_timer > ASTEROID_STATS.ASTEROID_SPAWN_RATE_SECONDS:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            assert len(self.edges) > 0, "self.edges cannot be empty"
            edge: list[pygame.Vector2 | Callable[[float], pygame.Vector2]] = random.choice(
                self.edges,
            )
            assert isinstance(edge, list), "edge must be a list"

            speed: int = random.randint(40, 100)
            assert isinstance(speed, int), "speed must be an int"
            direction: pygame.Vector2 = cast("pygame.Vector2", edge[0])
            velocity: pygame.Vector2 = direction * speed
            assert isinstance(velocity, pygame.Vector2), "velocity must be a Vector2"
            velocity = velocity.rotate(random.randint(-30, 30))
            assert isinstance(velocity, pygame.Vector2), "velocity must be a Vector2"
            position_fn: Callable[[float], pygame.Vector2] = cast(
                "Callable[[float], pygame.Vector2]",
                edge[1],
            )
            position: pygame.Vector2 = position_fn(random.uniform(0, 1))
            assert isinstance(position, pygame.Vector2), "position must be a Vector2"
            kind: int = random.randint(1, ASTEROID_STATS.ASTEROID_KINDS)
            assert isinstance(kind, int), "kind must be an int"

            wrapped_position: Vector2Wrapped = Vector2Wrapped.model_validate(position)
            assert isinstance(
                wrapped_position,
                Vector2Wrapped,
            ), "wrapped_position must be Vector2Wrapped"
            wrapped_velocity: Vector2Wrapped = Vector2Wrapped.model_validate(velocity)
            assert isinstance(
                wrapped_velocity,
                Vector2Wrapped,
            ), "wrapped_velocity must be Vector2Wrapped"

            self.spawn(
                ASTEROID_STATS.ASTEROID_MIN_RADIUS * kind,
                wrapped_position,
                wrapped_velocity,
            )
