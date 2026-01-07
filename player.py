"""Player class with triangle rendering and Pydantic validation."""
# pylint: disable=c-extension-no-member  # Pygame uses C extensions

from typing import Any

import pygame
from pydantic import validate_call
from pydantic_core import core_schema

from circleshape import CircleShape
from constants import PLAYER_DIMS
from validationfunctions import SurfaceWrapped


class Player(CircleShape):
    """Player ship represented as a triangle with rotation."""

    def __init__(self, x: float, y: float) -> None:
        assert isinstance(x, float), "x must be a float"
        assert isinstance(y, float), "y must be a float"

        super().__init__(x, y, PLAYER_DIMS.PLAYER_RADIUS)
        self.rotation = 0

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
    def _validate(value: Any) -> "Player":  # noqa: ANN401
        if not isinstance(value, Player):
            msg = "must be of type Player"
            raise TypeError(msg)
        return value

    @validate_call
    def triangle(self) -> list[pygame.Vector2]:
        forward: pygame.Vector2 = pygame.Vector2(0, 1).rotate(self.rotation)
        assert isinstance(forward, pygame.Vector2), "pygame.Vector2.rotate must return a Vector2"

        right: pygame.Vector2 = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        assert isinstance(right, pygame.Vector2), "pygame.Vector2.rotate must return a Vector2"

        new_triangle = [
            self.position + forward * self.radius,
            self.position - forward * self.radius - right,
            self.position - forward * self.radius + right,
        ]
        assert isinstance(new_triangle, list), "new_triangle must be a list"
        assert len(new_triangle) == 3, "new_triangle must have exactly 3 vertices"
        assert all(
            isinstance(v, pygame.Vector2) for v in new_triangle
        ), "all triangle vertices must be Vector2"

        return new_triangle

    @validate_call(validate_return=True)
    def draw(self, screen: SurfaceWrapped) -> None:  # type: ignore[override]
        get_player_triangle: list[pygame.Vector2] = self.triangle()
        assert isinstance(get_player_triangle, list), "self.triangle must return a list"
        assert len(get_player_triangle) == 3, "triangle must have exactly 3 vertices"
        assert all(
            isinstance(v, pygame.Vector2) for v in get_player_triangle
        ), "all triangle vertices must be Vector2"

        draw_player: pygame.rect.Rect = pygame.draw.polygon(
            screen.object,
            "white",
            get_player_triangle,
            PLAYER_DIMS.LINE_WIDTH,
        )
        assert isinstance(
            draw_player,
            pygame.rect.Rect,
        ), "pygame.draw.polygon must return type Rect"
