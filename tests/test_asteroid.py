"""Tests for asteroid.py Asteroid class."""

from unittest.mock import MagicMock

import pygame
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from asteroid import Asteroid
from circleshape import CircleShape
from validationfunctions import SurfaceWrapped


class TestAsteroidInit:
    """Tests for Asteroid initialization."""

    def test_init_valid_parameters(self) -> None:
        """Test Asteroid initializes with valid float x, y and int radius."""
        asteroid = Asteroid(100.0, 200.0, 30)
        assert asteroid.position.x == 100.0
        assert asteroid.position.y == 200.0
        assert asteroid.radius == 30

    def test_init_non_float_x_raises_assertion(self) -> None:
        """Test Asteroid raises AssertionError for non-float x."""
        with pytest.raises(AssertionError, match="x must be a float"):
            Asteroid(100, 200.0, 30)  # type: ignore[arg-type]

    def test_init_non_float_y_raises_assertion(self) -> None:
        """Test Asteroid raises AssertionError for non-float y."""
        with pytest.raises(AssertionError, match="y must be a float"):
            Asteroid(100.0, 200, 30)  # type: ignore[arg-type]

    def test_init_non_int_radius_raises_assertion(self) -> None:
        """Test Asteroid raises AssertionError for non-int radius."""
        with pytest.raises(AssertionError, match="radius must be a int"):
            Asteroid(100.0, 200.0, 30.0)  # type: ignore[arg-type]

    def test_inherits_circleshape(self) -> None:
        """Test Asteroid is instance of CircleShape."""
        asteroid = Asteroid(0.0, 0.0, 20)
        assert isinstance(asteroid, CircleShape)


class TestAsteroidPydanticValidation:
    """Tests for Asteroid Pydantic custom validation."""

    def test_pydantic_validator_accepts_asteroid(self) -> None:
        """Test Asteroid._validate accepts Asteroid instance."""
        asteroid = Asteroid(100.0, 200.0, 30)
        validated = Asteroid._validate(asteroid)
        assert validated is asteroid

    def test_pydantic_validator_rejects_non_asteroid(self) -> None:
        """Test Asteroid._validate rejects non-Asteroid types."""
        with pytest.raises(TypeError, match="must be of type Asteroid"):
            Asteroid._validate("not an asteroid")

    def test_pydantic_validator_rejects_none(self) -> None:
        """Test Asteroid._validate rejects None."""
        with pytest.raises(TypeError, match="must be of type Asteroid"):
            Asteroid._validate(None)


class TestAsteroidDraw:
    """Tests for Asteroid draw method."""

    @pytest.mark.integration
    def test_draw_calls_pygame_circle(self, mocker: MockerFixture) -> None:
        """Test draw method calls pygame.draw.circle with correct parameters."""
        pygame.init()
        screen = pygame.Surface((800, 600))
        wrapped_screen = SurfaceWrapped.model_validate(screen)

        mock_circle = mocker.patch("pygame.draw.circle", return_value=pygame.Rect(0, 0, 10, 10))

        asteroid = Asteroid(100.0, 200.0, 30)
        asteroid.draw(wrapped_screen)

        mock_circle.assert_called_once()
        args = mock_circle.call_args[0]
        assert args[0] is screen
        assert args[1] == "white"
        assert args[2] == asteroid.position
        assert args[3] == 30


class TestAsteroidUpdate:
    """Tests for Asteroid update method."""

    def test_update_moves_asteroid(self) -> None:
        """Test update method moves asteroid based on velocity and delta time."""
        asteroid = Asteroid(100.0, 100.0, 30)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        asteroid.update(1.0)

        assert asteroid.position.x == pytest.approx(150.0)
        assert asteroid.position.y == pytest.approx(100.0)

    def test_update_with_partial_delta(self) -> None:
        """Test update with fractional delta time."""
        asteroid = Asteroid(100.0, 100.0, 30)
        asteroid.velocity = pygame.Vector2(100.0, 100.0)

        asteroid.update(0.5)

        assert asteroid.position.x == pytest.approx(150.0)
        assert asteroid.position.y == pytest.approx(150.0)

    def test_update_invalid_dt_raises_error(self) -> None:
        """Test update raises ValidationError for non-float dt."""
        asteroid = Asteroid(100.0, 100.0, 30)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        with pytest.raises(ValidationError):
            asteroid.update("invalid")  # type: ignore[arg-type]
