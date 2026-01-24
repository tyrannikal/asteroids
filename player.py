# pylint: disable=c-extension-no-member,no-member

from typing import Any

import pygame
from pydantic import validate_call
from pydantic_core import core_schema

from circleshape import CircleShape
from constants import PLAYER_STATS
from shot import Shot
from validationfunctions import SurfaceWrapped


class Player(CircleShape):
    def __init__(self, x: float, y: float) -> None:
        assert isinstance(x, float), "x must be a float"
        assert isinstance(y, float), "y must be a float"

        super().__init__(x, y, PLAYER_STATS.PLAYER_RADIUS)
        self.rotation: float = 0.0
        self.shoot_cooldown: float = 0.0

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
            msg: str = "must be of type Player"
            raise TypeError(msg)
        return value

    @validate_call
    def triangle(self) -> list[pygame.Vector2]:
        forward: pygame.Vector2 = pygame.Vector2(0, 1).rotate(self.rotation)
        assert isinstance(forward, pygame.Vector2), "pygame.Vector2.rotate must return a Vector2"
        right: pygame.Vector2 = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        assert isinstance(right, pygame.Vector2), "pygame.Vector2.rotate must return a Vector2"

        new_triangle: list[pygame.Vector2] = [
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
            PLAYER_STATS.LINE_WIDTH,
        )
        assert isinstance(
            draw_player,
            pygame.rect.Rect,
        ), "pygame.draw.polygon must return type Rect"

    @validate_call(validate_return=True)
    def rotate(self, dt: float) -> None:
        self.rotation += PLAYER_STATS.PLAYER_TURN_SPEED * dt

    @validate_call(validate_return=True)
    def update(self, dt: float) -> None:
        keys: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        assert isinstance(
            keys,
            pygame.key.ScancodeWrapper,
        ), "pygame.key.get_pressed must return a ScancodeWrapper"
        assert isinstance(keys[pygame.K_a], bool), "keys[pygame.K_a] must be a bool"
        assert isinstance(keys[pygame.K_d], bool), "keys[pygame.K_d] must be a bool"

        self.shoot_cooldown -= dt

        if keys[pygame.K_a]:
            self.rotate(dt)
        if keys[pygame.K_d]:
            self.rotate(dt * -1)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(dt * -1)
        if keys[pygame.K_SPACE] and self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = PLAYER_STATS.PLAYER_SHOOT_COOLDOWN_SECONDS

    @validate_call(validate_return=True)
    def move(self, dt: float) -> None:
        unit_vector: pygame.Vector2 = pygame.Vector2(0, 1)
        assert isinstance(unit_vector, pygame.Vector2), "unit_vector must return Vector2"

        assert isinstance(self.rotation, float), "self.rotation must be a float"
        rotated_vector: pygame.Vector2 = unit_vector.rotate(self.rotation)
        assert isinstance(rotated_vector, pygame.Vector2), "rotated_vector must return Vector2"

        assert isinstance(dt, float), "dt must be a float"
        rotated_with_speed_vector: pygame.Vector2 = rotated_vector * PLAYER_STATS.PLAYER_SPEED * dt
        assert isinstance(
            rotated_with_speed_vector,
            pygame.Vector2,
        ), "rotated_with_speed_vector must return Vector2"

        self.position += rotated_with_speed_vector
        assert isinstance(self.position, pygame.Vector2), "self.position must be a Vector2"

    @validate_call(validate_return=True)
    def shoot(self) -> None:
        new_shot: Shot = Shot(self.position[0], self.position[1], self.radius)
        assert isinstance(new_shot, Shot), "new_shot must be a Shot"

        velocity: pygame.Vector2 = pygame.Vector2(0, 1)
        assert isinstance(velocity, pygame.Vector2), "velocity must return Vector2"

        assert isinstance(self.rotation, float), "self.rotation must be a float"
        new_shot.velocity = velocity.rotate(self.rotation)
        assert isinstance(new_shot.velocity, pygame.Vector2), "rotated_vector must return Vector2"

        new_shot.velocity *= PLAYER_STATS.PLAYER_SHOOT_SPEED
