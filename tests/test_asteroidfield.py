"""Tests for asteroidfield.py AsteroidField class."""

from unittest.mock import MagicMock, patch

import pygame
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from asteroid import Asteroid
from asteroidfield import AsteroidField
from validationfunctions import Vector2Wrapped


class TestAsteroidFieldInit:
    """Tests for AsteroidField initialization."""

    @pytest.mark.integration
    def test_init_creates_instance(self) -> None:
        """Test AsteroidField initializes correctly."""
        pygame.init()
        updatable = pygame.sprite.Group()
        AsteroidField.containers = (updatable,)

        field = AsteroidField()

        assert isinstance(field, AsteroidField)
        assert isinstance(field, pygame.sprite.Sprite)
        assert field.spawn_timer == 0.0

    @pytest.mark.integration
    def test_init_adds_to_containers(self) -> None:
        """Test AsteroidField is added to containers on init."""
        pygame.init()
        updatable = pygame.sprite.Group()
        AsteroidField.containers = (updatable,)

        field = AsteroidField()

        assert field in updatable.sprites()


class TestAsteroidFieldPydanticValidation:
    """Tests for AsteroidField Pydantic custom validation."""

    def test_pydantic_validator_accepts_asteroidfield(self) -> None:
        """Test AsteroidField._validate accepts AsteroidField instance."""
        pygame.init()
        updatable = pygame.sprite.Group()
        AsteroidField.containers = (updatable,)
        field = AsteroidField()

        validated = AsteroidField._validate(field)

        assert validated is field

    def test_pydantic_validator_rejects_non_asteroidfield(self) -> None:
        """Test AsteroidField._validate rejects non-AsteroidField types."""
        with pytest.raises(TypeError, match="must be of type AsteroidField"):
            AsteroidField._validate("not an asteroid field")

    def test_pydantic_validator_rejects_none(self) -> None:
        """Test AsteroidField._validate rejects None."""
        with pytest.raises(TypeError, match="must be of type AsteroidField"):
            AsteroidField._validate(None)


class TestAsteroidFieldSpawn:
    """Tests for AsteroidField spawn method."""

    @pytest.mark.integration
    def test_spawn_creates_asteroid(self, mocker: MockerFixture) -> None:
        """Test spawn method creates an Asteroid instance."""
        pygame.init()
        updatable = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        Asteroid.containers = (asteroids, updatable, drawable)
        AsteroidField.containers = (updatable,)

        field = AsteroidField()
        position = Vector2Wrapped.model_validate(pygame.Vector2(100.0, 200.0))
        velocity = Vector2Wrapped.model_validate(pygame.Vector2(50.0, 0.0))

        field.spawn(30, position, velocity)

        assert len(asteroids.sprites()) == 1
        asteroid = asteroids.sprites()[0]
        assert isinstance(asteroid, Asteroid)
        assert asteroid.position.x == 100.0
        assert asteroid.position.y == 200.0
        assert asteroid.radius == 30


class TestAsteroidFieldUpdate:
    """Tests for AsteroidField update method."""

    @pytest.mark.integration
    def test_update_increments_spawn_timer(self, mocker: MockerFixture) -> None:
        """Test update increments spawn_timer when below spawn rate."""
        pygame.init()
        updatable = pygame.sprite.Group()
        AsteroidField.containers = (updatable,)

        field = AsteroidField()

        # Set spawn timer to negative value so it won't trigger spawn
        # ASTEROID_SPAWN_RATE_SECONDS is 0, so timer + dt must be <= 0 to not spawn
        field.spawn_timer = -1.0

        field.update(0.5)

        assert field.spawn_timer == -0.5

    @pytest.mark.integration
    def test_update_spawns_asteroid_after_timer_expires(self, mocker: MockerFixture) -> None:
        """Test update spawns asteroid when timer exceeds spawn rate."""
        pygame.init()
        updatable = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        Asteroid.containers = (asteroids, updatable, drawable)
        AsteroidField.containers = (updatable,)

        # Mock random functions for predictable behavior
        mocker.patch("random.choice", return_value=AsteroidField.edges[0])
        mocker.patch("random.randint", side_effect=[50, 0, 1])
        mocker.patch("random.uniform", return_value=0.5)

        field = AsteroidField()
        field.spawn_timer = 2.0  # Set timer close to spawn rate

        # Update with enough time to trigger spawn
        field.update(1.0)

        # Timer should reset
        assert field.spawn_timer == 0.0
        # An asteroid should be spawned
        assert len(asteroids.sprites()) > 0

    @pytest.mark.integration
    def test_update_does_not_spawn_before_timer_expires(self, mocker: MockerFixture) -> None:
        """Test update does not spawn asteroid when timer is below spawn rate."""
        pygame.init()
        updatable = pygame.sprite.Group()
        asteroids = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        Asteroid.containers = (asteroids, updatable, drawable)
        AsteroidField.containers = (updatable,)

        field = AsteroidField()

        # Set spawn timer to negative value so it won't trigger spawn
        # ASTEROID_SPAWN_RATE_SECONDS is 0, so timer + dt must be <= 0 to not spawn
        field.spawn_timer = -1.0

        # Update with small delta, should not spawn
        field.update(0.5)

        # No asteroids should be spawned
        assert len(asteroids.sprites()) == 0
        assert field.spawn_timer == -0.5

    def test_update_invalid_dt_raises_error(self) -> None:
        """Test update raises ValidationError for non-float dt."""
        pygame.init()
        updatable = pygame.sprite.Group()
        AsteroidField.containers = (updatable,)

        field = AsteroidField()

        with pytest.raises(ValidationError):
            field.update("invalid")  # type: ignore[arg-type]


class TestAsteroidFieldEdges:
    """Tests for AsteroidField edges class attribute."""

    def test_edges_has_four_entries(self) -> None:
        """Test edges contains exactly 4 edge definitions."""
        assert len(AsteroidField.edges) == 4

    def test_each_edge_has_direction_and_position_generator(self) -> None:
        """Test each edge has Vector2 direction and position callable."""
        for edge in AsteroidField.edges:
            assert len(edge) == 2
            assert isinstance(edge[0], pygame.Vector2)
            assert callable(edge[1])

    def test_edge_position_generators_return_vector2(self) -> None:
        """Test each edge's position generator returns Vector2."""
        for edge in AsteroidField.edges:
            position_fn = edge[1]
            result = position_fn(0.5)
            assert isinstance(result, pygame.Vector2)
