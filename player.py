from pydantic_core import CoreSchema, core_schema
from pydantic import validate_call

from circleshape import CircleShape
import pygame

from constants import PlayerDimensions 
from validationfunctions import SurfaceWrapped


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        assert type(x) == float, "x must be a float"
        assert type (y) == float, "y must be a float"

        player = super().__init__(x, y, PlayerDimensions().PLAYER_RADIUS)
        assert player == None, "super().__init__ must return None"

        self.rotation = 0

        return None


    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler) -> core_schema.CoreSchema:
        return (core_schema.no_info_before_validator_function(cls._validate, schema=core_schema.any_schema(),))

    @staticmethod
    def _validate(value):
        if not isinstance(value, Player):
            raise ValidationError("must be of type Player")
        return value

    @validate_call(validate_return=True)
    def triangle(self) -> list:
        forward: pygame.Vector2 = pygame.Vector2(0, 1).rotate(self.rotation)
        assert type(forward) == pygame.Vector2, "pygame.Vector2.rotate must return a Vector2"

        right: pygame.Vector2 = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        assert type(right) == pygame.Vector2, "pygame.Vector2.rotate must return a Vector2"

        a: pygame.Vector2 = self.position + forward * self.radius
        b: pygame.Vector2 = self.position - forward * self.radius - right
        c: pygame.Vector2 = self.position - forward * self.radius + right

        return [a, b, c]


    @validate_call(validate_return=True)
    def draw(self, screen: SurfaceWrapped) -> None:
        get_player_triangle: list = self.triangle()
        assert type(get_player_triangle) == list, "self.triangle must return a list"
        assert len(get_player_triangle) == 3, "self.triangle must return a list of length 3"
        assert type(get_player_triangle[0]) == pygame.Vector2, "each list index must be a Vector2"
        assert type(get_player_triangle[1]) == pygame.Vector2, "each list index must be a Vector2"
        assert type(get_player_triangle[2]) == pygame.Vector2, "each list index must be a Vector2"

        draw_player: pygame.rect.Rect = pygame.draw.polygon(screen.object, "white", get_player_triangle, PlayerDimensions().LINE_WIDTH)
        assert type(draw_player) == pygame.rect.Rect, "pygame.draw.polygon must return type Rect"

        return None

