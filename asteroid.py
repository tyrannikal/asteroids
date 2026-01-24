import random
from typing import Any

import pygame
from pydantic import validate_call
from pydantic_core import core_schema

from circleshape import CircleShape
from constants import ASTEROID_STATS, PLAYER_STATS
from logger import log_event
from validationfunctions import SurfaceWrapped


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, radius: int) -> None:
        assert isinstance(x, float), "x must be a float"
        assert isinstance(y, float), "y must be a float"
        assert isinstance(radius, int), "radius must be a int"

        super().__init__(x, y, radius)

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
    def _validate(value: Any) -> "Asteroid":  # noqa: ANN401
        if not isinstance(value, Asteroid):
            msg = "must be of type Asteroid"
            raise TypeError(msg)
        return value

    @validate_call(validate_return=True)
    def draw(self, screen: SurfaceWrapped) -> None:  # type: ignore[override]
        draw_asteroid: pygame.rect.Rect = pygame.draw.circle(
            screen.object,
            "white",
            self.position,
            self.radius,
            PLAYER_STATS.LINE_WIDTH,
        )
        assert isinstance(
            draw_asteroid,
            pygame.rect.Rect,
        ), "pygame.draw.circle must return type Rect"

    @validate_call(validate_return=True)
    def update(self, dt: float) -> None:
        self.position += self.velocity * dt

    @validate_call(validate_return=True)
    def split(self) -> None:
        self.kill()

        if self.radius <= ASTEROID_STATS.ASTEROID_MIN_RADIUS:
            return

        log_event("asteroid_split")

        new_angle: float = random.uniform(20, 50)
        assert isinstance(new_angle, float), "new_angle must be a float"
        assert 20.0 <= new_angle <= 50.0, "new_angle must be between 20 and 50"  # noqa: PLR2004

        new_velocity_1: pygame.Vector2 = self.velocity.rotate(new_angle)
        assert isinstance(new_velocity_1, pygame.Vector2), "new_velocity_1 must be a Vector2"
        new_velocity_2: pygame.Vector2 = self.velocity.rotate(-new_angle)
        assert isinstance(new_velocity_2, pygame.Vector2), "new_velocity_2 must be a Vector2"

        new_radius: int = self.radius - ASTEROID_STATS.ASTEROID_MIN_RADIUS

        new_asteroid_1: Asteroid = Asteroid(self.position[0], self.position[1], new_radius)
        assert isinstance(new_asteroid_1, Asteroid), "new_asteroid_1, must be an Asteroid"
        new_asteroid_2: Asteroid = Asteroid(self.position[0], self.position[1], new_radius)
        assert isinstance(new_asteroid_2, Asteroid), "new_asteroid_2, must be an Asteroid"

        new_asteroid_1.velocity = new_velocity_1 * 1.2
        new_asteroid_2.velocity = new_velocity_2 * 1.2
