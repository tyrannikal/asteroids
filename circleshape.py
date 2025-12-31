import pygame

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x: float, y: float, radius: int) -> None:
        assert type(x) == float, "x must be a float"
        assert type(y) == float, "y must be a float"
        assert type(radius) == int, "radius must be a int"

        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position: pygame.Vector2 = pygame.Vector2(x, y)
        self.velocity: pygame.Vector2 = pygame.Vector2(0, 0)
        self.radius: int = radius

        return None

    def draw(self, screen):
        # must override
        pass

    def update(self, dt):
        # must override
        pass

