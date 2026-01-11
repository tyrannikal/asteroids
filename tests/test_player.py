"""Tests for player.py Player class with geometric calculations."""

import math
from unittest.mock import MagicMock

import pygame
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from circleshape import CircleShape
from constants import PlayerDimensions
from player import Player
from validationfunctions import SurfaceWrapped


class TestPlayerInit:
    """Tests for Player initialization."""

    def test_init_valid_parameters(self) -> None:
        """Test Player initializes with valid float x, y."""
        player = Player(640.0, 360.0)
        assert player.position.x == 640.0
        assert player.position.y == 360.0

    def test_init_non_float_x_raises_assertion(self) -> None:
        """Test Player raises AssertionError for non-float x."""
        with pytest.raises(AssertionError, match="x must be a float"):
            Player(640, 360.0)  # type: ignore[arg-type]

    def test_init_non_float_y_raises_assertion(self) -> None:
        """Test Player raises AssertionError for non-float y."""
        with pytest.raises(AssertionError, match="y must be a float"):
            Player(640.0, 360)  # type: ignore[arg-type]

    def test_inherits_circleshape(self) -> None:
        """Test Player is instance of CircleShape."""
        player = Player(0.0, 0.0)
        assert isinstance(player, CircleShape)

    def test_initial_rotation_zero(self) -> None:
        """Test rotation initializes to 0."""
        player = Player(100.0, 200.0)
        assert player.rotation == 0

    def test_radius_uses_player_dimensions(self) -> None:
        """Test radius comes from PlayerDimensions.PLAYER_RADIUS."""
        player = Player(0.0, 0.0)
        expected_radius = PlayerDimensions().PLAYER_RADIUS
        assert player.radius == expected_radius
        assert player.radius == 20


class TestPlayerPydanticValidation:
    """Tests for Player Pydantic custom validation."""

    def test_pydantic_validator_accepts_player(self) -> None:
        """Test Player._validate accepts Player instance."""
        player = Player(100.0, 200.0)
        validated = Player._validate(player)
        assert validated is player

    def test_pydantic_validator_rejects_non_player(self) -> None:
        """Test Player._validate rejects non-Player types."""
        with pytest.raises(TypeError, match="must be of type Player"):
            Player._validate("not a player")

    def test_pydantic_validator_rejects_none(self) -> None:
        """Test Player._validate rejects None."""
        with pytest.raises(TypeError, match="must be of type Player"):
            Player._validate(None)

    def test_pydantic_validator_rejects_int(self) -> None:
        """Test Player._validate rejects integer."""
        with pytest.raises(TypeError, match="must be of type Player"):
            Player._validate(42)


class TestPlayerTriangle:
    """Critical tests for geometric triangle calculation."""

    def test_triangle_at_zero_rotation(self) -> None:
        """Test triangle vertices at rotation=0 (pointing up)."""
        player = Player(100.0, 100.0)
        player.rotation = 0
        vertices = player.triangle()

        # At rotation 0, forward is (0, 1)
        # Front vertex should be at position + (0, 1) * radius
        # = (100, 100) + (0, 20) = (100, 120)
        assert vertices[0].x == pytest.approx(100.0, abs=0.01)
        assert vertices[0].y == pytest.approx(120.0, abs=0.01)

    def test_triangle_at_90_degrees(self) -> None:
        """Test triangle vertices at rotation=90 (pointing right)."""
        player = Player(100.0, 100.0)
        player.rotation = 90
        vertices = player.triangle()

        # At rotation 90, forward is (-1, 0) after pygame rotation
        # Front vertex should be roughly at (100 - 20, 100) = (80, 100)
        # Note: pygame rotates counter-clockwise, so 90° points left in standard coords
        # But pygame's y-axis points down, so it's actually pointing right on screen
        assert vertices[0].x == pytest.approx(80.0, abs=0.01)
        assert vertices[0].y == pytest.approx(100.0, abs=0.01)

    def test_triangle_at_180_degrees(self) -> None:
        """Test triangle vertices at rotation=180 (pointing down)."""
        player = Player(100.0, 100.0)
        player.rotation = 180
        vertices = player.triangle()

        # At rotation 180, forward is (0, -1)
        # Front vertex should be at (100, 100) + (0, -20) = (100, 80)
        assert vertices[0].x == pytest.approx(100.0, abs=0.01)
        assert vertices[0].y == pytest.approx(80.0, abs=0.01)

    def test_triangle_at_270_degrees(self) -> None:
        """Test triangle vertices at rotation=270 (pointing left)."""
        player = Player(100.0, 100.0)
        player.rotation = 270
        vertices = player.triangle()

        # At rotation 270, forward is (1, 0)
        # Front vertex should be at (100, 100) + (20, 0) = (120, 100)
        assert vertices[0].x == pytest.approx(120.0, abs=0.01)
        assert vertices[0].y == pytest.approx(100.0, abs=0.01)

    def test_triangle_at_45_degrees(self) -> None:
        """Test triangle vertices at non-cardinal angle."""
        player = Player(0.0, 0.0)
        player.rotation = 45
        vertices = player.triangle()

        # At 45 degrees, forward should be at roughly 45° angle
        # Using pygame's rotation: (0, 1).rotate(45) gives roughly (-0.707, 0.707)
        expected_x = -20 * math.sin(math.radians(45))
        expected_y = 20 * math.cos(math.radians(45))

        assert vertices[0].x == pytest.approx(expected_x, abs=0.1)
        assert vertices[0].y == pytest.approx(expected_y, abs=0.1)

    def test_triangle_returns_three_vertices(self) -> None:
        """Test triangle() always returns list of exactly 3 Vector2."""
        player = Player(50.0, 75.0)
        vertices = player.triangle()

        assert isinstance(vertices, list)
        assert len(vertices) == 3

    def test_triangle_vertices_are_vector2(self) -> None:
        """Test all triangle vertices are pygame.Vector2 instances."""
        player = Player(0.0, 0.0)
        vertices = player.triangle()

        assert all(isinstance(v, pygame.Vector2) for v in vertices)

    def test_triangle_front_vertex_distance(self) -> None:
        """Test front vertex is exactly radius distance from center."""
        player = Player(100.0, 100.0)
        player.rotation = 0
        vertices = player.triangle()

        # Front vertex (vertices[0]) should be radius distance from position
        distance = player.position.distance_to(vertices[0])
        assert distance == pytest.approx(player.radius, abs=0.01)

    def test_triangle_symmetry(self) -> None:
        """Test back two vertices are symmetric relative to forward direction."""
        player = Player(100.0, 100.0)
        player.rotation = 0
        vertices = player.triangle()

        # At rotation 0 (forward points up), back vertices should have same y coordinate
        assert vertices[1].y == pytest.approx(vertices[2].y, abs=0.01)

    def test_triangle_changes_with_rotation(self) -> None:
        """Test triangle updates when rotation changes."""
        player = Player(100.0, 100.0)

        player.rotation = 0
        vertices_0 = player.triangle()

        player.rotation = 90
        vertices_90 = player.triangle()

        # Vertices should be different after rotation change
        assert vertices_0[0] != vertices_90[0]

    def test_triangle_negative_rotation(self) -> None:
        """Test triangle with negative rotation angle."""
        player = Player(100.0, 100.0)
        player.rotation = -90
        vertices = player.triangle()

        # Should still return 3 valid Vector2 instances
        assert len(vertices) == 3
        assert all(isinstance(v, pygame.Vector2) for v in vertices)

    def test_triangle_rotation_360(self) -> None:
        """Test triangle at 360 degrees equals 0 degrees."""
        player = Player(100.0, 100.0)

        player.rotation = 0
        vertices_0 = player.triangle()

        player.rotation = 360
        vertices_360 = player.triangle()

        # Should be approximately equal
        for v0, v360 in zip(vertices_0, vertices_360, strict=True):
            assert v0.x == pytest.approx(v360.x, abs=0.01)
            assert v0.y == pytest.approx(v360.y, abs=0.01)

    def test_triangle_at_origin(self) -> None:
        """Test triangle calculation when player at origin."""
        player = Player(0.0, 0.0)
        player.rotation = 0
        vertices = player.triangle()

        # Front vertex should be at (0, radius)
        assert vertices[0].x == pytest.approx(0.0, abs=0.01)
        assert vertices[0].y == pytest.approx(20.0, abs=0.01)


class TestPlayerDraw:
    """Tests for Player draw method."""

    def test_draw_calls_polygon(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() calls pygame.draw.polygon with correct args."""
        mock_polygon = mocker.patch(
            "pygame.draw.polygon",
            return_value=pygame.rect.Rect(0, 0, 100, 100),
        )

        player = Player(640.0, 360.0)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        player.draw(wrapped)

        # Verify polygon was called
        mock_polygon.assert_called_once()

        # Verify arguments
        call_args = mock_polygon.call_args
        assert call_args[0][0] is mock_surface  # Surface object
        assert call_args[0][1] == "white"  # Color
        assert isinstance(call_args[0][2], list)  # Triangle vertices
        assert len(call_args[0][2]) == 3
        assert call_args[0][3] == PlayerDimensions().LINE_WIDTH  # Line width

    def test_draw_returns_none(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() returns None."""
        mocker.patch("pygame.draw.polygon", return_value=pygame.rect.Rect(0, 0, 100, 100))

        player = Player(100.0, 200.0)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        result = player.draw(wrapped)

        assert result is None

    def test_draw_uses_white_color(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() uses 'white' color."""
        mock_polygon = mocker.patch(
            "pygame.draw.polygon",
            return_value=pygame.rect.Rect(0, 0, 100, 100),
        )

        player = Player(100.0, 100.0)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        player.draw(wrapped)

        call_args = mock_polygon.call_args
        assert call_args[0][1] == "white"

    def test_draw_uses_line_width(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() uses PlayerDimensions.LINE_WIDTH."""
        mock_polygon = mocker.patch(
            "pygame.draw.polygon",
            return_value=pygame.rect.Rect(0, 0, 100, 100),
        )

        player = Player(100.0, 100.0)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        player.draw(wrapped)

        call_args = mock_polygon.call_args
        assert call_args[0][3] == 2  # Default LINE_WIDTH

    def test_draw_validates_triangle_output(
        self,
        mocker: MockerFixture,
        mock_surface: MagicMock,
    ) -> None:
        """Test draw() validates triangle() returns 3 Vector2s."""
        mocker.patch("pygame.draw.polygon", return_value=pygame.rect.Rect(0, 0, 100, 100))

        player = Player(100.0, 100.0)
        wrapped = SurfaceWrapped.model_validate(mock_surface)

        # Should not raise assertion errors
        player.draw(wrapped)

    def test_draw_with_rotated_player(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test draw() works correctly with rotated player."""
        mock_polygon = mocker.patch(
            "pygame.draw.polygon",
            return_value=pygame.rect.Rect(0, 0, 100, 100),
        )

        player = Player(100.0, 100.0)
        player.rotation = 45
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        player.draw(wrapped)

        # Verify polygon was called with rotated triangle
        mock_polygon.assert_called_once()
        call_args = mock_polygon.call_args
        vertices = call_args[0][2]
        assert len(vertices) == 3


class TestPlayerRotate:
    """Tests for Player rotate method."""

    def test_rotate_positive_dt_increases_rotation(self) -> None:
        """Test rotate with positive dt increases rotation."""
        player = Player(100.0, 100.0)
        player.rotation = 0
        player.rotate(1.0)

        # PLAYER_TURN_SPEED is 300, so rotation should increase by 300 * 1.0 = 300
        assert player.rotation == pytest.approx(300.0, abs=0.01)

    def test_rotate_negative_dt_decreases_rotation(self) -> None:
        """Test rotate with negative dt decreases rotation."""
        player = Player(100.0, 100.0)
        player.rotation = 0
        player.rotate(-1.0)

        # rotation should decrease by 300 * -1.0 = -300
        assert player.rotation == pytest.approx(-300.0, abs=0.01)

    def test_rotate_zero_dt_no_change(self) -> None:
        """Test rotate with zero dt makes no change."""
        player = Player(100.0, 100.0)
        player.rotation = 45
        player.rotate(0.0)

        assert player.rotation == pytest.approx(45.0, abs=0.01)

    def test_rotate_small_dt(self) -> None:
        """Test rotate with small dt value (typical frame time)."""
        player = Player(100.0, 100.0)
        player.rotation = 0
        # Typical 60fps frame time is ~0.0167 seconds
        player.rotate(0.0167)

        # 300 * 0.0167 = 5.01 degrees
        assert player.rotation == pytest.approx(5.01, abs=0.01)

    def test_rotate_accumulation(self) -> None:
        """Test multiple rotate calls accumulate correctly."""
        player = Player(100.0, 100.0)
        player.rotation = 0

        player.rotate(0.1)  # +30 degrees
        player.rotate(0.1)  # +30 degrees
        player.rotate(0.1)  # +30 degrees

        assert player.rotation == pytest.approx(90.0, abs=0.01)

    def test_rotate_from_non_zero_initial(self) -> None:
        """Test rotate from non-zero starting rotation."""
        player = Player(100.0, 100.0)
        player.rotation = 45
        player.rotate(0.5)  # +150 degrees

        assert player.rotation == pytest.approx(195.0, abs=0.01)

    def test_rotate_beyond_360(self) -> None:
        """Test rotation can exceed 360 degrees."""
        player = Player(100.0, 100.0)
        player.rotation = 350
        player.rotate(1.0)  # +300 degrees

        # Should be 650, not wrapped
        assert player.rotation == pytest.approx(650.0, abs=0.01)

    def test_rotate_negative_rotation(self) -> None:
        """Test rotation can go negative."""
        player = Player(100.0, 100.0)
        player.rotation = 10
        player.rotate(-1.0)  # -300 degrees

        assert player.rotation == pytest.approx(-290.0, abs=0.01)

    def test_rotate_large_dt(self) -> None:
        """Test rotate with large dt value."""
        player = Player(100.0, 100.0)
        player.rotation = 0
        player.rotate(10.0)

        assert player.rotation == pytest.approx(3000.0, abs=0.01)

    def test_rotate_returns_none(self) -> None:
        """Test rotate returns None."""
        player = Player(100.0, 100.0)
        result = player.rotate(1.0)

        assert result is None

    def test_rotate_uses_player_turn_speed(self) -> None:
        """Test rotate uses PLAYER_TURN_SPEED constant."""
        player = Player(100.0, 100.0)
        player.rotation = 0
        expected_speed = PlayerDimensions().PLAYER_TURN_SPEED
        player.rotate(1.0)

        assert player.rotation == pytest.approx(float(expected_speed), abs=0.01)

    def test_rotate_with_validation_error_non_float(self) -> None:
        """Test rotate raises ValidationError for non-float dt."""
        player = Player(100.0, 100.0)

        with pytest.raises(ValidationError):
            player.rotate("not a float")  # type: ignore[arg-type]


class TestPlayerUpdate:
    """Tests for Player update method with keyboard input."""

    def test_update_a_key_rotates_left(self, mocker: MockerFixture) -> None:
        """Test pressing 'a' key rotates player counter-clockwise."""
        # Create a proper mock ScancodeWrapper that behaves like a dict
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: key == pygame.K_a
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 0
        player.update(0.1)

        # Should rotate by PLAYER_TURN_SPEED * dt = 300 * 0.1 = 30 degrees
        assert player.rotation == pytest.approx(30.0, abs=0.01)

    def test_update_d_key_rotates_right(self, mocker: MockerFixture) -> None:
        """Test pressing 'd' key rotates player clockwise."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: key == pygame.K_d
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 0
        player.update(0.1)

        # Should rotate by PLAYER_TURN_SPEED * -dt = 300 * -0.1 = -30 degrees
        assert player.rotation == pytest.approx(-30.0, abs=0.01)

    def test_update_both_keys_cancel_out(self, mocker: MockerFixture) -> None:
        """Test pressing both 'a' and 'd' keys applies both rotations."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: key in (pygame.K_a, pygame.K_d)
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 0
        player.update(0.1)

        # Both rotations applied: +30 and -30 = 0
        assert player.rotation == pytest.approx(0.0, abs=0.01)

    def test_update_no_keys_no_rotation(self, mocker: MockerFixture) -> None:
        """Test no keys pressed results in no rotation."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: False
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 45
        player.update(0.1)

        # Rotation should remain unchanged
        assert player.rotation == pytest.approx(45.0, abs=0.01)

    def test_update_other_keys_ignored(self, mocker: MockerFixture) -> None:
        """Test other keys don't affect rotation."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: key in (pygame.K_w, pygame.K_s, pygame.K_SPACE)
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 100.0
        player.update(0.1)

        # Rotation should remain unchanged
        assert player.rotation == pytest.approx(100.0, abs=0.01)

    def test_update_zero_dt(self, mocker: MockerFixture) -> None:
        """Test update with zero dt causes no rotation even with keys pressed."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: key == pygame.K_a
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 50
        player.update(0.0)

        # No time passed, so no rotation
        assert player.rotation == pytest.approx(50.0, abs=0.01)

    def test_update_large_dt(self, mocker: MockerFixture) -> None:
        """Test update with large dt value."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: key == pygame.K_a
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 0
        player.update(5.0)

        # 300 * 5.0 = 1500 degrees
        assert player.rotation == pytest.approx(1500.0, abs=0.01)

    def test_update_negative_dt(self, mocker: MockerFixture) -> None:
        """Test update with negative dt (time reversal scenario)."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: key == pygame.K_a
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 0
        player.update(-0.1)

        # 300 * -0.1 = -30 degrees (reverses rotation direction)
        assert player.rotation == pytest.approx(-30.0, abs=0.01)

    def test_update_returns_none(self, mocker: MockerFixture) -> None:
        """Test update returns None."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: False
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        result = player.update(0.1)

        assert result is None

    def test_update_calls_get_pressed(self, mocker: MockerFixture) -> None:
        """Test update calls pygame.key.get_pressed."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: False
        mock_get_pressed = mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.update(0.1)

        mock_get_pressed.assert_called_once()

    def test_update_multiple_frames_accumulate(self, mocker: MockerFixture) -> None:
        """Test multiple update calls accumulate rotation correctly."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: key == pygame.K_a
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)
        player.rotation = 0

        # Simulate 3 frames at 60fps (~0.0167s each)
        player.update(0.0167)
        player.update(0.0167)
        player.update(0.0167)

        # 300 * 0.0167 * 3 = ~15.03 degrees
        assert player.rotation == pytest.approx(15.03, abs=0.1)

    def test_update_alternating_keys(self, mocker: MockerFixture) -> None:
        """Test alternating between a and d keys."""
        player = Player(100.0, 100.0)
        player.rotation = 0

        # Press 'a'
        mock_keys_a = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys_a.__getitem__ = lambda self, key: key == pygame.K_a
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys_a)
        player.update(0.1)  # +30 degrees

        # Press 'd'
        mock_keys_d = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys_d.__getitem__ = lambda self, key: key == pygame.K_d
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys_d)
        player.update(0.1)  # -30 degrees

        # Should be back to 0
        assert player.rotation == pytest.approx(0.0, abs=0.01)

    def test_update_with_validation_error_non_float(self, mocker: MockerFixture) -> None:
        """Test update raises ValidationError for non-float dt."""
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__ = lambda self, key: False
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        player = Player(100.0, 100.0)

        with pytest.raises(ValidationError):
            player.update("not a float")  # type: ignore[arg-type]
