from typing import Any

import pygame
from pydantic import validate_call
from pydantic_core import core_schema

from circleshape import CircleShape
from constants import PLAYER_DIMS
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
            PLAYER_DIMS.LINE_WIDTH,
        )
        assert isinstance(
            draw_asteroid,
            pygame.rect.Rect,
        ), "pygame.draw.circle must return type Rect"

    @validate_call(validate_return=True)
    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
