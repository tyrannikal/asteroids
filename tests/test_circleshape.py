"""Tests for circleshape.py CircleShape base class."""

from typing import Any
from unittest.mock import MagicMock

import pygame
import pytest
from pytest_mock import MockerFixture

from circleshape import CircleShape


class TestCircleShapeInit:
    """Tests for CircleShape initialization."""

    def test_init_valid_parameters(self) -> None:
        """Test CircleShape initializes with valid float x, y and int radius."""
        shape = CircleShape(100.0, 200.0, 20)
        assert shape.position.x == 100.0
        assert shape.position.y == 200.0
        assert shape.radius == 20

    def test_init_non_float_x_raises_assertion(self) -> None:
        """Test CircleShape raises AssertionError for non-float x."""
        with pytest.raises(AssertionError, match="x must be a float"):
            CircleShape(100, 200.0, 20)  # type: ignore[arg-type]

    def test_init_non_float_y_raises_assertion(self) -> None:
        """Test CircleShape raises AssertionError for non-float y."""
        with pytest.raises(AssertionError, match="y must be a float"):
            CircleShape(100.0, 200, 20)  # type: ignore[arg-type]

    def test_init_non_int_radius_raises_assertion(self) -> None:
        """Test CircleShape raises AssertionError for non-int radius."""
        with pytest.raises(AssertionError, match="radius must be an int"):
            CircleShape(100.0, 200.0, 20.5)  # type: ignore[arg-type]

    def test_position_is_vector2(self) -> None:
        """Test position is initialized as pygame.Vector2."""
        shape = CircleShape(50.0, 75.0, 15)
        assert isinstance(shape.position, pygame.Vector2)
        assert shape.position.x == 50.0
        assert shape.position.y == 75.0

    def test_velocity_is_vector2(self) -> None:
        """Test velocity is initialized as pygame.Vector2(0, 0)."""
        shape = CircleShape(10.0, 20.0, 5)
        assert isinstance(shape.velocity, pygame.Vector2)
        assert shape.velocity.x == 0
        assert shape.velocity.y == 0

    def test_velocity_initially_zero(self) -> None:
        """Test velocity starts at zero."""
        shape = CircleShape(0.0, 0.0, 10)
        assert shape.velocity == pygame.Vector2(0, 0)

    def test_radius_stored_correctly(self) -> None:
        """Test radius is stored as int attribute."""
        shape = CircleShape(0.0, 0.0, 42)
        assert shape.radius == 42
        assert isinstance(shape.radius, int)

    def test_inherits_sprite(self) -> None:
        """Test CircleShape is instance of pygame.sprite.Sprite."""
        shape = CircleShape(0.0, 0.0, 1)
        assert isinstance(shape, pygame.sprite.Sprite)

    def test_containers_none_no_error(self) -> None:
        """Test initialization with no containers attribute."""
        # Should not raise any error
        shape = CircleShape(0.0, 0.0, 10)
        assert not hasattr(shape, "containers")

    def test_negative_coordinates(self) -> None:
        """Test CircleShape accepts negative coordinates."""
        shape = CircleShape(-50.0, -100.0, 10)
        assert shape.position.x == -50.0
        assert shape.position.y == -100.0

    def test_zero_coordinates(self) -> None:
        """Test CircleShape accepts zero coordinates."""
        shape = CircleShape(0.0, 0.0, 1)
        assert shape.position.x == 0.0
        assert shape.position.y == 0.0

    def test_string_x_raises_assertion(self) -> None:
        """Test CircleShape rejects string x coordinate."""
        with pytest.raises(AssertionError, match="x must be a float"):
            CircleShape("100", 200.0, 20)  # type: ignore[arg-type]

    def test_string_y_raises_assertion(self) -> None:
        """Test CircleShape rejects string y coordinate."""
        with pytest.raises(AssertionError, match="y must be a float"):
            CircleShape(100.0, "200", 20)  # type: ignore[arg-type]

    def test_string_radius_raises_assertion(self) -> None:
        """Test CircleShape rejects string radius."""
        with pytest.raises(AssertionError, match="radius must be an int"):
            CircleShape(100.0, 200.0, "20")  # type: ignore[arg-type]


class TestCircleShapeMethods:
    """Tests for CircleShape methods."""

    def test_draw_method_exists(self) -> None:
        """Test draw method signature (placeholder)."""
        shape = CircleShape(0.0, 0.0, 10)
        assert hasattr(shape, "draw")
        assert callable(shape.draw)

    def test_update_method_exists(self) -> None:
        """Test update method signature (placeholder)."""
        shape = CircleShape(0.0, 0.0, 10)
        assert hasattr(shape, "update")
        assert callable(shape.update)

    def test_draw_accepts_surface(self, mock_surface: MagicMock) -> None:
        """Test draw method accepts surface parameter."""
        shape = CircleShape(0.0, 0.0, 10)
        # Should not raise any error (placeholder implementation)
        result = shape.draw(mock_surface)
        assert result is None

    def test_update_accepts_dt(self) -> None:
        """Test update method accepts dt parameter."""
        shape = CircleShape(0.0, 0.0, 10)
        # Should not raise any error (placeholder implementation)
        result = shape.update(0.016)
        assert result is None


class TestCircleShapeWithContainers:
    """Tests for CircleShape with sprite containers."""

    def test_containers_with_group(self, mocker: MockerFixture) -> None:
        """Test initialization with containers class attribute."""

        # Create a subclass with containers
        class ShapeWithContainers(CircleShape):
            containers: Any = None

        mock_group = mocker.MagicMock(spec=pygame.sprite.Group)
        ShapeWithContainers.containers = mock_group

        shape = ShapeWithContainers(100.0, 200.0, 15)

        # Verify it was initialized with the container
        assert isinstance(shape, pygame.sprite.Sprite)
        assert shape.position.x == 100.0
        assert shape.position.y == 200.0

    def test_velocity_modification(self) -> None:
        """Test velocity can be modified after initialization."""
        shape = CircleShape(0.0, 0.0, 10)
        shape.velocity = pygame.Vector2(5.0, 10.0)
        assert shape.velocity.x == 5.0
        assert shape.velocity.y == 10.0

    def test_position_modification(self) -> None:
        """Test position can be modified after initialization."""
        shape = CircleShape(100.0, 200.0, 10)
        shape.position = pygame.Vector2(300.0, 400.0)
        assert shape.position.x == 300.0
        assert shape.position.y == 400.0

    def test_radius_modification(self) -> None:
        """Test radius can be modified after initialization."""
        shape = CircleShape(0.0, 0.0, 10)
        shape.radius = 25
        assert shape.radius == 25
