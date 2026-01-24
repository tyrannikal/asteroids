"""Tests for shot.py Shot class."""

import math
from unittest.mock import MagicMock

import pygame
import pytest
from pytest_mock import MockerFixture

from circleshape import CircleShape
from constants import PLAYER_STATS
from shot import Shot
from validationfunctions import SurfaceWrapped


@pytest.mark.unit
class TestShotInit:
    """Tests for Shot initialization."""

    def test_init_valid_parameters(self) -> None:
        """Test Shot initializes with valid float x, y and int radius."""
        shot = Shot(100.0, 200.0, 5)
        assert shot.position.x == 100.0
        assert shot.position.y == 200.0
        assert shot.radius == 5

    def test_init_non_float_x_raises_assertion(self) -> None:
        """Test Shot raises AssertionError for non-float x."""
        with pytest.raises(AssertionError, match="x must be a float"):
            Shot(100, 200.0, 5)  # type: ignore[arg-type]

    def test_init_non_float_y_raises_assertion(self) -> None:
        """Test Shot raises AssertionError for non-float y."""
        with pytest.raises(AssertionError, match="y must be a float"):
            Shot(100.0, 200, 5)  # type: ignore[arg-type]

    def test_init_non_int_radius_raises_assertion(self) -> None:
        """Test Shot raises AssertionError for non-int radius."""
        with pytest.raises(AssertionError, match="radius must be a int"):
            Shot(100.0, 200.0, 5.0)  # type: ignore[arg-type]

    def test_inherits_circleshape(self) -> None:
        """Test Shot is instance of CircleShape."""
        shot = Shot(0.0, 0.0, 5)
        assert isinstance(shot, CircleShape)

    def test_inherits_sprite(self) -> None:
        """Test Shot is instance of pygame.sprite.Sprite."""
        shot = Shot(0.0, 0.0, 5)
        assert isinstance(shot, pygame.sprite.Sprite)

    def test_initial_velocity_zero(self) -> None:
        """Test velocity initializes to (0, 0)."""
        shot = Shot(100.0, 200.0, 5)
        assert shot.velocity.x == 0.0
        assert shot.velocity.y == 0.0

    def test_position_is_vector2(self) -> None:
        """Test position is pygame.Vector2."""
        shot = Shot(50.0, 75.0, 5)
        assert isinstance(shot.position, pygame.Vector2)

    def test_velocity_is_vector2(self) -> None:
        """Test velocity is pygame.Vector2."""
        shot = Shot(50.0, 75.0, 5)
        assert isinstance(shot.velocity, pygame.Vector2)

    def test_negative_coordinates(self) -> None:
        """Test Shot accepts negative coordinates."""
        shot = Shot(-100.0, -200.0, 5)
        assert shot.position.x == -100.0
        assert shot.position.y == -200.0

    def test_zero_coordinates(self) -> None:
        """Test Shot accepts zero coordinates."""
        shot = Shot(0.0, 0.0, 5)
        assert shot.position.x == 0.0
        assert shot.position.y == 0.0

    def test_large_coordinates(self) -> None:
        """Test Shot accepts large coordinates."""
        shot = Shot(10000.0, 20000.0, 5)
        assert shot.position.x == 10000.0
        assert shot.position.y == 20000.0


@pytest.mark.unit
class TestShotPydanticValidation:
    """Tests for Shot Pydantic custom validation."""

    def test_pydantic_validator_accepts_shot(self) -> None:
        """Test Shot._validate accepts Shot instance."""
        shot = Shot(100.0, 200.0, 5)
        validated = Shot._validate(shot)  # noqa: SLF001
        assert validated is shot

    def test_pydantic_validator_rejects_non_shot(self) -> None:
        """Test Shot._validate rejects non-Shot types."""
        with pytest.raises(TypeError, match="must be of type Shot"):
            Shot._validate("not a shot")  # noqa: SLF001

    def test_pydantic_validator_rejects_none(self) -> None:
        """Test Shot._validate rejects None."""
        with pytest.raises(TypeError, match="must be of type Shot"):
            Shot._validate(None)  # noqa: SLF001

    def test_pydantic_validator_rejects_int(self) -> None:
        """Test Shot._validate rejects integer."""
        with pytest.raises(TypeError, match="must be of type Shot"):
            Shot._validate(42)  # noqa: SLF001

    def test_pydantic_validator_rejects_circleshape(self) -> None:
        """Test Shot._validate rejects CircleShape (parent class)."""
        circle = CircleShape(100.0, 200.0, 5)
        with pytest.raises(TypeError, match="must be of type Shot"):
            Shot._validate(circle)  # noqa: SLF001


@pytest.mark.unit
class TestShotDraw:
    """Tests for Shot draw method."""

    def test_draw_calls_circle(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() calls pygame.draw.circle with correct args."""
        mock_circle = mocker.patch(
            "pygame.draw.circle",
            return_value=pygame.rect.Rect(0, 0, 10, 10),
        )

        shot = Shot(100.0, 200.0, 5)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        shot.draw(wrapped)

        mock_circle.assert_called_once()

        call_args = mock_circle.call_args
        assert call_args[0][0] is mock_surface  # Surface object
        assert call_args[0][1] == "white"  # Color
        assert call_args[0][2] == shot.position  # Position
        assert call_args[0][3] == shot.radius  # Radius
        assert call_args[0][4] == PLAYER_STATS.LINE_WIDTH  # Line width

    def test_draw_returns_none(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() returns None."""
        mocker.patch("pygame.draw.circle", return_value=pygame.rect.Rect(0, 0, 10, 10))

        shot = Shot(100.0, 200.0, 5)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        result = shot.draw(wrapped)

        assert result is None

    def test_draw_uses_white_color(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() uses 'white' color."""
        mock_circle = mocker.patch(
            "pygame.draw.circle",
            return_value=pygame.rect.Rect(0, 0, 10, 10),
        )

        shot = Shot(100.0, 200.0, 5)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        shot.draw(wrapped)

        call_args = mock_circle.call_args
        assert call_args[0][1] == "white"

    def test_draw_uses_line_width(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() uses PLAYER_STATS.LINE_WIDTH."""
        mock_circle = mocker.patch(
            "pygame.draw.circle",
            return_value=pygame.rect.Rect(0, 0, 10, 10),
        )

        shot = Shot(100.0, 200.0, 5)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        shot.draw(wrapped)

        call_args = mock_circle.call_args
        assert call_args[0][4] == 2  # Default LINE_WIDTH

    def test_draw_at_different_positions(
        self,
        mocker: MockerFixture,
        mock_surface: MagicMock,
    ) -> None:
        """Test draw() uses shot's current position."""
        mock_circle = mocker.patch(
            "pygame.draw.circle",
            return_value=pygame.rect.Rect(0, 0, 10, 10),
        )

        shot = Shot(500.0, 300.0, 5)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        shot.draw(wrapped)

        call_args = mock_circle.call_args
        assert call_args[0][2].x == 500.0
        assert call_args[0][2].y == 300.0


@pytest.mark.unit
class TestShotUpdate:
    """Tests for Shot update method."""

    def test_update_moves_shot_by_velocity(self) -> None:
        """Test update() moves shot position by velocity * dt."""
        shot = Shot(100.0, 100.0, 5)
        shot.velocity = pygame.Vector2(100.0, 50.0)
        shot.update(1.0)

        assert shot.position.x == pytest.approx(200.0, abs=0.01)
        assert shot.position.y == pytest.approx(150.0, abs=0.01)

    def test_update_with_zero_velocity(self) -> None:
        """Test update() with zero velocity doesn't move shot."""
        shot = Shot(100.0, 100.0, 5)
        shot.velocity = pygame.Vector2(0.0, 0.0)
        shot.update(1.0)

        assert shot.position.x == pytest.approx(100.0, abs=0.01)
        assert shot.position.y == pytest.approx(100.0, abs=0.01)

    def test_update_with_zero_dt(self) -> None:
        """Test update() with zero dt doesn't move shot."""
        shot = Shot(100.0, 100.0, 5)
        shot.velocity = pygame.Vector2(500.0, 500.0)
        shot.update(0.0)

        assert shot.position.x == pytest.approx(100.0, abs=0.01)
        assert shot.position.y == pytest.approx(100.0, abs=0.01)

    def test_update_with_small_dt(self) -> None:
        """Test update() with typical frame time (~60fps)."""
        shot = Shot(100.0, 100.0, 5)
        shot.velocity = pygame.Vector2(500.0, 0.0)
        shot.update(0.0167)  # ~60fps frame time

        # 100 + 500 * 0.0167 = 108.35
        assert shot.position.x == pytest.approx(108.35, abs=0.1)
        assert shot.position.y == pytest.approx(100.0, abs=0.01)

    def test_update_with_negative_velocity(self) -> None:
        """Test update() with negative velocity moves in opposite direction."""
        shot = Shot(100.0, 100.0, 5)
        shot.velocity = pygame.Vector2(-200.0, -100.0)
        shot.update(1.0)

        assert shot.position.x == pytest.approx(-100.0, abs=0.01)
        assert shot.position.y == pytest.approx(0.0, abs=0.01)

    def test_update_accumulates_over_multiple_calls(self) -> None:
        """Test multiple update() calls accumulate position changes."""
        shot = Shot(100.0, 100.0, 5)
        shot.velocity = pygame.Vector2(100.0, 0.0)

        shot.update(0.1)  # +10
        shot.update(0.1)  # +10
        shot.update(0.1)  # +10

        assert shot.position.x == pytest.approx(130.0, abs=0.01)

    def test_update_with_diagonal_velocity(self) -> None:
        """Test update() with diagonal velocity."""
        shot = Shot(0.0, 0.0, 5)
        # 45 degree angle at speed ~141.4
        shot.velocity = pygame.Vector2(100.0, 100.0)
        shot.update(1.0)

        assert shot.position.x == pytest.approx(100.0, abs=0.01)
        assert shot.position.y == pytest.approx(100.0, abs=0.01)

    def test_update_returns_none(self) -> None:
        """Test update() returns None."""
        shot = Shot(100.0, 100.0, 5)
        shot.velocity = pygame.Vector2(100.0, 100.0)
        result = shot.update(1.0)

        assert result is None

    def test_update_with_large_velocity(self) -> None:
        """Test update() with very high velocity."""
        shot = Shot(0.0, 0.0, 5)
        shot.velocity = pygame.Vector2(10000.0, 5000.0)
        shot.update(1.0)

        assert shot.position.x == pytest.approx(10000.0, abs=0.01)
        assert shot.position.y == pytest.approx(5000.0, abs=0.01)


@pytest.mark.unit
class TestShotVelocityDirection:
    """Tests for Shot velocity direction calculations (relevant to shooting)."""

    def test_velocity_rotate_zero_degrees(self) -> None:
        """Test velocity pointing up (0 degrees rotation)."""
        shot = Shot(0.0, 0.0, 5)
        shot.velocity = pygame.Vector2(0, 1).rotate(0) * 500

        # At 0 degrees, (0, 1) stays (0, 1)
        assert shot.velocity.x == pytest.approx(0.0, abs=0.01)
        assert shot.velocity.y == pytest.approx(500.0, abs=0.01)

    def test_velocity_rotate_90_degrees(self) -> None:
        """Test velocity pointing left (90 degrees rotation in pygame)."""
        shot = Shot(0.0, 0.0, 5)
        shot.velocity = pygame.Vector2(0, 1).rotate(90) * 500

        # pygame rotates counter-clockwise, so 90 degrees points left (-1, 0)
        assert shot.velocity.x == pytest.approx(-500.0, abs=0.01)
        assert shot.velocity.y == pytest.approx(0.0, abs=0.01)

    def test_velocity_rotate_180_degrees(self) -> None:
        """Test velocity pointing down (180 degrees rotation)."""
        shot = Shot(0.0, 0.0, 5)
        shot.velocity = pygame.Vector2(0, 1).rotate(180) * 500

        # 180 degrees rotates (0, 1) to (0, -1)
        assert shot.velocity.x == pytest.approx(0.0, abs=0.01)
        assert shot.velocity.y == pytest.approx(-500.0, abs=0.01)

    def test_velocity_rotate_270_degrees(self) -> None:
        """Test velocity pointing right (270 degrees rotation)."""
        shot = Shot(0.0, 0.0, 5)
        shot.velocity = pygame.Vector2(0, 1).rotate(270) * 500

        # 270 degrees rotates (0, 1) to (1, 0)
        assert shot.velocity.x == pytest.approx(500.0, abs=0.01)
        assert shot.velocity.y == pytest.approx(0.0, abs=0.01)

    def test_velocity_rotate_45_degrees(self) -> None:
        """Test velocity at 45 degrees."""
        shot = Shot(0.0, 0.0, 5)
        shot.velocity = pygame.Vector2(0, 1).rotate(45) * 500

        # 45 degrees gives approximately (-0.707, 0.707) * 500
        expected_x = -500 * math.sin(math.radians(45))
        expected_y = 500 * math.cos(math.radians(45))

        assert shot.velocity.x == pytest.approx(expected_x, abs=0.1)
        assert shot.velocity.y == pytest.approx(expected_y, abs=0.1)

    def test_velocity_rotate_negative_angle(self) -> None:
        """Test velocity with negative rotation angle."""
        shot = Shot(0.0, 0.0, 5)
        shot.velocity = pygame.Vector2(0, 1).rotate(-90) * 500

        # -90 degrees rotates (0, 1) to (1, 0) - clockwise
        assert shot.velocity.x == pytest.approx(500.0, abs=0.01)
        assert shot.velocity.y == pytest.approx(0.0, abs=0.01)

    def test_velocity_magnitude_preserved(self) -> None:
        """Test velocity magnitude is preserved after rotation."""
        shot = Shot(0.0, 0.0, 5)
        shot.velocity = pygame.Vector2(0, 1).rotate(37) * 500

        magnitude = shot.velocity.length()
        assert magnitude == pytest.approx(500.0, abs=0.01)


@pytest.mark.unit
class TestShotCollision:
    """Tests for Shot collision detection (inherited from CircleShape)."""

    def test_collides_with_overlapping_circleshape(self) -> None:
        """Test collision detection with overlapping circles."""
        shot = Shot(100.0, 100.0, 5)
        other = CircleShape(102.0, 100.0, 5)  # 2 pixels apart, radii sum = 10

        assert shot.collides_with(other) is True

    def test_no_collision_with_distant_circleshape(self) -> None:
        """Test no collision with distant circles."""
        shot = Shot(100.0, 100.0, 5)
        other = CircleShape(200.0, 200.0, 5)  # Far away

        assert shot.collides_with(other) is False

    def test_collision_at_exact_boundary(self) -> None:
        """Test collision when circles exactly touch."""
        shot = Shot(100.0, 100.0, 5)
        # Place other exactly at distance = sum of radii (10)
        other = CircleShape(110.0, 100.0, 5)

        # distance_to = 10, radii sum = 10, so < returns False
        assert shot.collides_with(other) is False

    def test_collision_just_inside_boundary(self) -> None:
        """Test collision when circles just overlap."""
        shot = Shot(100.0, 100.0, 5)
        # Place other just inside sum of radii
        other = CircleShape(109.9, 100.0, 5)

        assert shot.collides_with(other) is True
