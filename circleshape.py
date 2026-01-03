"""Base class for circular game objects with position and velocity."""

import pygame


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

    def draw(self, screen: "pygame.Surface") -> None:
        pass

    def update(self, dt: float) -> None:
        _ = dt  # Parameter reserved for future use
