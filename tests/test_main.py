"""Tests for main.py game initialization and main loop."""

from typing import Any
from unittest.mock import MagicMock

import pygame
import pytest
from pytest_mock import MockerFixture

from constants import GameArea
from main import fill_background, new_player_center, print_welcome_message, start_game
from player import Player
from validationfunctions import RectWrapped, SurfaceWrapped


class TestPrintWelcomeMessage:
    """Tests for print_welcome_message function."""

    def test_outputs_version(self, mocker: MockerFixture, capsys: Any) -> None:
        """Test print_welcome_message() outputs pygame version."""
        mocker.patch("pygame.version.ver", "2.6.1")

        print_welcome_message()

        captured = capsys.readouterr()
        assert "2.6.1" in captured.out
        assert "pygame version" in captured.out

    def test_outputs_screen_dimensions(self, capsys: Any) -> None:
        """Test print_welcome_message() outputs SCREEN_WIDTH/HEIGHT."""
        print_welcome_message()

        captured = capsys.readouterr()
        assert "1280" in captured.out
        assert "720" in captured.out
        assert "Screen width" in captured.out
        assert "Screen height" in captured.out

    def test_returns_none(self) -> None:
        """Test print_welcome_message() returns None."""
        result = print_welcome_message()
        assert result is None

    def test_asserts_pygame_version(self, mocker: MockerFixture) -> None:
        """Test print_welcome_message() asserts pygame version == 2.6.1."""
        mocker.patch("pygame.version.ver", "2.5.0")

        with pytest.raises(AssertionError, match="pygame version must be exactly 2.6.1"):
            print_welcome_message()


class TestStartGame:
    """Tests for start_game function."""

    def test_calls_pygame_init(self, mock_pygame_init: MagicMock) -> None:
        """Test start_game() calls pygame.init()."""
        start_game()
        mock_pygame_init.assert_called_once()

    def test_returns_none(self, mock_pygame_init: MagicMock) -> None:
        """Test start_game() returns None."""
        result = start_game()
        assert result is None

    def test_asserts_tuple_return(self, mocker: MockerFixture) -> None:
        """Test start_game() asserts pygame.init() returns tuple."""
        mocker.patch("pygame.init", return_value=[10, 0])  # List instead of tuple

        with pytest.raises(AssertionError, match="pygame.init.*must return type tuple"):
            start_game()

    def test_asserts_success_count_positive(self, mocker: MockerFixture) -> None:
        """Test start_game() asserts success_count > 0."""
        mocker.patch("pygame.init", return_value=(0, 0))

        with pytest.raises(AssertionError, match="must have at least one module succeed"):
            start_game()

    def test_asserts_failure_count_zero(self, mocker: MockerFixture) -> None:
        """Test start_game() asserts failure_count == 0."""
        mocker.patch("pygame.init", return_value=(10, 1))

        with pytest.raises(AssertionError, match="must not have any modules fail"):
            start_game()

    def test_successful_initialization(self, mocker: MockerFixture) -> None:
        """Test start_game() with valid initialization."""
        mocker.patch("pygame.init", return_value=(15, 0))

        # Should not raise any errors
        start_game()


class TestNewPlayerCenter:
    """Tests for new_player_center function."""

    def test_creates_player_at_center(self) -> None:
        """Test new_player_center() creates Player at screen center."""
        player = new_player_center()

        expected_x = GameArea().SCREEN_WIDTH / 2
        expected_y = GameArea().SCREEN_HEIGHT / 2

        assert player.position.x == expected_x
        assert player.position.y == expected_y

    def test_returns_player_instance(self) -> None:
        """Test new_player_center() returns Player type."""
        player = new_player_center()
        assert isinstance(player, Player)

    def test_uses_game_area_dimensions(self) -> None:
        """Test new_player_center() uses GameArea().SCREEN_WIDTH/HEIGHT."""
        player = new_player_center()

        # Default dimensions are 1280x720
        assert player.position.x == 640.0
        assert player.position.y == 360.0


class TestFillBackground:
    """Tests for fill_background function."""

    def test_fills_screen_with_color(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test fill_background() calls Surface.fill()."""
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
        mock_surface.get_size.return_value = (1280, 720)

        wrapped = SurfaceWrapped.model_validate(mock_surface)
        fill_background(wrapped, "black")

        mock_surface.fill.assert_called_once_with("black")

    def test_returns_rect_wrapped(self, mock_surface: MagicMock) -> None:
        """Test fill_background() returns RectWrapped."""
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
        mock_surface.get_size.return_value = (1280, 720)

        wrapped = SurfaceWrapped.model_validate(mock_surface)
        result = fill_background(wrapped, "black")

        assert isinstance(result, RectWrapped)

    def test_validates_color_in_thecolors(self, mock_surface: MagicMock) -> None:
        """Test fill_background() asserts color in pygame.colordict.THECOLORS."""
        wrapped = SurfaceWrapped.model_validate(mock_surface)

        with pytest.raises(
            AssertionError,
            match="background color must be listed in pygame.colordict.THECOLORS",
        ):
            fill_background(wrapped, "invalid_color_xyz_123")

    def test_invalid_color_raises_assertion(self, mock_surface: MagicMock) -> None:
        """Test fill_background() raises AssertionError for invalid color."""
        wrapped = SurfaceWrapped.model_validate(mock_surface)

        with pytest.raises(AssertionError):
            fill_background(wrapped, "notarealcolor")

    def test_validates_dimensions(self, mocker: MockerFixture, mock_surface: MagicMock) -> None:
        """Test fill_background() validates screen size matches GameArea."""
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
        mock_surface.get_size.return_value = (1280, 720)

        wrapped = SurfaceWrapped.model_validate(mock_surface)

        # Should not raise any errors
        result = fill_background(wrapped, "black")
        assert isinstance(result, RectWrapped)

    def test_wrong_width_raises_assertion(self, mock_surface: MagicMock) -> None:
        """Test fill_background() raises AssertionError for wrong width."""
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1920, 720)
        mock_surface.get_size.return_value = (1920, 720)

        wrapped = SurfaceWrapped.model_validate(mock_surface)

        with pytest.raises(
            AssertionError,
            match="screen background width must equal game_area width",
        ):
            fill_background(wrapped, "black")

    def test_wrong_height_raises_assertion(self, mock_surface: MagicMock) -> None:
        """Test fill_background() raises AssertionError for wrong height."""
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 1080)
        mock_surface.get_size.return_value = (1280, 1080)

        wrapped = SurfaceWrapped.model_validate(mock_surface)

        with pytest.raises(
            AssertionError,
            match="screen background height must equal game_area height",
        ):
            fill_background(wrapped, "black")

    def test_valid_colors(self, mock_surface: MagicMock) -> None:
        """Test fill_background() accepts various valid colors."""
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
        mock_surface.get_size.return_value = (1280, 720)

        wrapped = SurfaceWrapped.model_validate(mock_surface)

        # Test various valid colors
        for color in ["black", "white", "red", "blue", "green"]:
            result = fill_background(wrapped, color)
            assert isinstance(result, RectWrapped)


class TestMainLoop:
    """Integration-style tests for main() with heavy mocking."""

    def test_main_initializes_pygame(self, mocker: MockerFixture) -> None:
        """Test main() calls start_game()."""
        mocker.patch("main.print_welcome_message")
        mock_start = mocker.patch("main.start_game")
        mocker.patch("pygame.time.Clock")
        mocker.patch("pygame.display.set_mode", return_value=MagicMock(spec=pygame.surface.Surface))
        mocker.patch("main.new_player_center", return_value=MagicMock(spec=Player))

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_start.assert_called_once()

    def test_main_creates_clock(self, mocker: MockerFixture) -> None:
        """Test main() creates pygame.time.Clock."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mock_clock_class = mocker.patch("pygame.time.Clock")
        mocker.patch("pygame.display.set_mode", return_value=MagicMock(spec=pygame.surface.Surface))
        mocker.patch("main.new_player_center", return_value=MagicMock(spec=Player))

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_clock_class.assert_called_once()

    def test_main_creates_display(self, mocker: MockerFixture) -> None:
        """Test main() calls pygame.display.set_mode()."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mocker.patch("pygame.time.Clock")
        mock_display = mocker.patch(
            "pygame.display.set_mode",
            return_value=MagicMock(spec=pygame.surface.Surface),
        )
        mocker.patch("main.new_player_center", return_value=MagicMock(spec=Player))

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_display.assert_called_once()
        call_args = mock_display.call_args
        assert call_args[0][0] == (1280, 720)

    def test_main_creates_player(self, mocker: MockerFixture) -> None:
        """Test main() calls new_player_center()."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mocker.patch("pygame.time.Clock")
        mocker.patch("pygame.display.set_mode", return_value=MagicMock(spec=pygame.surface.Surface))
        mock_player = mocker.patch("main.new_player_center", return_value=MagicMock(spec=Player))

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_player.assert_called_once()

    def test_main_event_loop_processes_quit(self, mocker: MockerFixture) -> None:
        """Test main() returns on pygame.QUIT event."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mocker.patch("pygame.time.Clock")
        mocker.patch("pygame.display.set_mode", return_value=MagicMock(spec=pygame.surface.Surface))
        mocker.patch("main.new_player_center", return_value=MagicMock(spec=Player))

        # Mock QUIT event
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mocker.patch("pygame.display.flip")

        from main import main

        # Should return (not loop forever)
        result = main()
        assert result is None

    def test_main_calls_log_state(self, mocker: MockerFixture) -> None:
        """Test main() calls log_state() each iteration."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mocker.patch("pygame.time.Clock")
        mocker.patch("pygame.display.set_mode", return_value=MagicMock(spec=pygame.surface.Surface))
        mocker.patch("main.new_player_center", return_value=MagicMock(spec=Player))

        mock_log = mocker.patch("main.log_state")

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_log.assert_called()

    def test_main_fills_background_each_frame(self, mocker: MockerFixture) -> None:
        """Test main() calls fill_background() each iteration."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mocker.patch("pygame.time.Clock")
        mock_surface = MagicMock(spec=pygame.surface.Surface)
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
        mock_surface.get_size.return_value = (1280, 720)
        mocker.patch("pygame.display.set_mode", return_value=mock_surface)

        mock_player = MagicMock(spec=Player)
        mock_player.draw.return_value = None
        mocker.patch("main.new_player_center", return_value=mock_player)

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        # Verify surface.fill was called
        mock_surface.fill.assert_called_with("black")

    def test_main_draws_player_each_frame(self, mocker: MockerFixture) -> None:
        """Test main() calls player.draw() each iteration."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mocker.patch("pygame.time.Clock")
        mock_surface = MagicMock(spec=pygame.surface.Surface)
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
        mock_surface.get_size.return_value = (1280, 720)
        mocker.patch("pygame.display.set_mode", return_value=mock_surface)

        mock_player = MagicMock(spec=Player)
        mock_player.draw.return_value = None
        mocker.patch("main.new_player_center", return_value=mock_player)

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        # Verify player.draw was called
        mock_player.draw.assert_called_once()

    def test_main_flips_display(self, mocker: MockerFixture) -> None:
        """Test main() calls pygame.display.flip()."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mock_clock = MagicMock()
        mock_clock.tick.return_value = 16
        mocker.patch("pygame.time.Clock", return_value=mock_clock)
        mock_surface = MagicMock(spec=pygame.surface.Surface)
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
        mock_surface.get_size.return_value = (1280, 720)
        mocker.patch("pygame.display.set_mode", return_value=mock_surface)

        mock_player = MagicMock(spec=Player)
        mock_player.draw.return_value = None
        mocker.patch("main.new_player_center", return_value=mock_player)

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mock_flip = mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_flip.assert_called()

    def test_main_ticks_clock(self, mocker: MockerFixture) -> None:
        """Test main() calls clock.tick(60)."""
        mocker.patch("main.print_welcome_message")
        mocker.patch("main.start_game")
        mock_clock = MagicMock()
        mock_clock.tick.return_value = 16
        mocker.patch("pygame.time.Clock", return_value=mock_clock)
        mock_surface = MagicMock(spec=pygame.surface.Surface)
        mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
        mock_surface.get_size.return_value = (1280, 720)
        mocker.patch("pygame.display.set_mode", return_value=mock_surface)

        mock_player = MagicMock(spec=Player)
        mock_player.draw.return_value = None
        mocker.patch("main.new_player_center", return_value=mock_player)

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state")
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_clock.tick.assert_called_with(60)
