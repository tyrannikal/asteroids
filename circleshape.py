"""Base class for circular game objects with position and velocity."""

from typing import Any

import pygame
from pydantic_core import core_schema


class CircleShape(pygame.sprite.Sprite):
    """Base class for game objects with circular collision detection."""

    def __init__(self, x: float, y: float, radius: int) -> None:
        assert isinstance(x, float), "x must be a float"
        assert isinstance(y, float), "y must be a float"
        assert isinstance(radius, int), "radius must be an int"

        containers = getattr(self, "containers", None)
        if containers is not None:
            super().__init__(containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity: pygame.Vector2 = pygame.Vector2(0, 0)
        self.radius: int = radius

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
    def _validate(value: Any) -> "CircleShape":  # noqa: ANN401
        if not isinstance(value, CircleShape):
            msg = "must be of type CircleShape"
            raise TypeError(msg)
        return value

    def draw(self, screen: "pygame.Surface") -> None:
        _ = screen  # Abstract method - to be implemented by subclasses

    def update(self, dt: float) -> None:
        _ = dt  # Abstract method - to be implemented by subclasses

    def collides_with(self, other: "CircleShape") -> bool:
        return self.position.distance_to(other.position) < self.radius + other.radius
