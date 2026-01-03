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
