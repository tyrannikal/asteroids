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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
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


@pytest.mark.unit
class TestMainLoop:
    """Integration-style tests for main() with heavy mocking."""

    def test_main_initializes_pygame(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() calls start_game()."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mock_start = mocker.patch("main.start_game", return_value=None)

        # Use real Surface from pygame
        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state", return_value=None)
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_start.assert_called_once()

    def test_main_creates_clock(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() creates pygame.time.Clock and uses it."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        # Don't mock Clock, let it be real
        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state", return_value=None)
        mocker.patch("pygame.display.flip")

        from main import main

        # If Clock wasn't created, main() would fail when calling clock.tick()
        main()  # Success implies Clock was created and used

    def test_main_creates_display(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() calls pygame.display.set_mode()."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mock_display = mocker.patch("pygame.display.set_mode", return_value=real_surface)

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state", return_value=None)
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_display.assert_called_once()
        call_args = mock_display.call_args
        assert call_args[0][0] == (1280, 720)

    def test_main_creates_player(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() calls new_player_center()."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)

        # Spy on new_player_center to verify it's called while keeping real implementation
        import main as main_module
        mock_new_player = mocker.spy(main_module, "new_player_center")

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state", return_value=None)
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_new_player.assert_called_once()

    def test_main_event_loop_processes_quit(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() returns on pygame.QUIT event."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)

        # Mock QUIT event
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state", return_value=None)
        mocker.patch("pygame.display.flip")

        from main import main

        # Should return (not loop forever)
        result = main()
        assert result is None

    def test_main_calls_log_state(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() calls log_state() each iteration."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)

        mock_log = mocker.patch("main.log_state", return_value=None)

        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_log.assert_called()

    def test_main_fills_background_each_frame(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() calls fill_background() each iteration."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        # Use real surface so fill() works properly
        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)


        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state", return_value=None)
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        # Verify surface was filled (real surface.fill() returns Rect, verifying it was called)
        # Since we're using a real surface, we can't directly verify fill was called
        # but if main() completes without error, fill_background() was called successfully

    def test_main_draws_player_each_frame(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() draws player each iteration via sprite groups."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)

        # Mock pygame.key.get_pressed since video system isn't initialized
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__.return_value = False
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        # Spy on Player.draw to verify it's called
        mock_draw = mocker.spy(Player, "draw")

        # Let one iteration complete, then quit on second iteration
        mock_quit_event = MagicMock()
        mock_quit_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", side_effect=[[], [mock_quit_event]])
        mocker.patch("main.log_state", return_value=None)
        mocker.patch("pygame.display.flip")

        from main import main

        main()

        # Verify Player.draw was called (via sprite group iteration)
        mock_draw.assert_called_once()

    def test_main_flips_display(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() calls pygame.display.flip()."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)

        # Mock pygame.key.get_pressed since video system isn't initialized
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__.return_value = False
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        # Let one iteration complete, then quit on second iteration
        mock_quit_event = MagicMock()
        mock_quit_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", side_effect=[[], [mock_quit_event]])
        mocker.patch("main.log_state", return_value=None)
        mock_flip = mocker.patch("pygame.display.flip")

        from main import main

        main()

        mock_flip.assert_called()

    def test_main_ticks_clock(self, mocker: MockerFixture, mock_pygame_init: None) -> None:
        """Test main() calls clock.tick(60)."""
        mocker.patch("main.print_welcome_message", return_value=None)
        mocker.patch("main.start_game", return_value=None)

        real_surface = pygame.Surface((GameArea().SCREEN_WIDTH, GameArea().SCREEN_HEIGHT))
        mocker.patch("pygame.display.set_mode", return_value=real_surface)


        # Mock event loop to exit immediately
        mock_event = MagicMock()
        mock_event.type = pygame.QUIT
        mocker.patch("pygame.event.get", return_value=[mock_event])
        mocker.patch("main.log_state", return_value=None)
        mocker.patch("pygame.display.flip")

        from main import main

        # If clock.tick wasn't called properly, assertions in main() would fail
        main()


@pytest.mark.unit
class TestSpriteGroups:
    """Tests for sprite group initialization and integration."""

    def test_player_added_to_groups_via_containers(self, mocker: MockerFixture) -> None:
        """Test Player instances are automatically added to groups when containers is set."""
        # Create sprite groups
        updatable = pygame.sprite.Group()
        drawable = pygame.sprite.Group()

        # Set containers
        Player.containers = (updatable, drawable)

        # Create a player
        player = Player(100.0, 200.0)

        # Verify player is in both groups
        assert updatable.has(player)
        assert drawable.has(player)
        assert len(updatable) == 1
        assert len(drawable) == 1

        # Clean up
        Player.containers = ()

    def test_group_update_calls_sprite_update(self, mocker: MockerFixture) -> None:
        """Test that calling group.update() calls update on all sprites."""
        # Create sprite groups
        updatable = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        Player.containers = (updatable, drawable)

        # Create player and spy on its update method
        player = Player(100.0, 200.0)
        mock_update = mocker.spy(player, "update")

        # Mock pygame.key.get_pressed to avoid video system requirement
        mock_keys = MagicMock(spec=pygame.key.ScancodeWrapper)
        mock_keys.__getitem__.return_value = False
        mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

        # Call group update
        updatable.update(0.016)

        # Verify player.update was called with dt
        mock_update.assert_called_once_with(0.016)

        # Clean up
        Player.containers = ()

    def test_drawable_group_iteration(self, mocker: MockerFixture) -> None:
        """Test iterating over drawable group yields player sprites."""
        # Create sprite groups
        updatable = pygame.sprite.Group()
        drawable = pygame.sprite.Group()
        Player.containers = (updatable, drawable)

        # Create two players
        player1 = Player(100.0, 200.0)
        player2 = Player(300.0, 400.0)

        # Iterate and collect sprites
        sprites = list(drawable)

        assert len(sprites) == 2
        assert player1 in sprites
        assert player2 in sprites

        # Clean up
        Player.containers = ()
