"""Tests for logger.py file I/O and introspection."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import mock_open

import freezegun
import pygame
from pytest_mock import MockerFixture

import pytest

import logger
from constants import LoggingConstants


@pytest.mark.unit
class TestLogStateFrameCounting:
    """Tests for log_state frame counting logic."""

    def test_frame_count_increments(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test _frame_count increments on each log_state() call."""
        mocker.patch("inspect.currentframe", return_value=None)  # Skip actual logging

        initial_count = logger._frame_count  # type: ignore[attr-defined]
        logger.log_state()
        assert logger._frame_count == initial_count + 1  # type: ignore[attr-defined]

    def test_logs_only_on_fps_interval(
        self,
        clean_logger_state: Any,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test log_state() only writes every FPS frames."""
        mocker.patch("inspect.currentframe", return_value=None)

        # Call log_state FPS-1 times, should not write
        fps = LoggingConstants().FPS
        for _ in range(fps - 1):
            logger.log_state()

        # Frame count should be FPS-1, but no file written
        assert logger._frame_count == fps - 1  # type: ignore[attr-defined]

    def test_stops_after_max_seconds(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() stops after MAX_SECONDS * FPS frames."""
        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {}
        mocker.patch("inspect.currentframe", return_value=mock_frame)
        mock_open_func = mocker.patch("pathlib.Path.open", mock_open())

        max_frames = LoggingConstants().FPS * LoggingConstants().MAX_SECONDS

        # Set frame count to max + 1
        logger._frame_count = max_frames + 1  # type: ignore[attr-defined]

        logger.log_state()

        # Should return early, no file operations
        mock_open_func.assert_not_called()


@pytest.mark.unit
class TestLogStateFileIO:
    """Tests for log_state file I/O operations."""

    def test_creates_game_state_jsonl(
        self,
        clean_logger_state: Any,
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test log_state() creates game_state.jsonl file."""
        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        # Change to tmp directory
        mocker.patch("pathlib.Path", return_value=tmp_path / "game_state.jsonl")

        # Call log_state at FPS interval
        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

    def test_first_write_uses_mode_w(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test first log_state() opens file in 'w' mode."""
        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_open_func = mocker.patch("pathlib.Path.open", mock_open())

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        # Verify file opened in 'w' mode
        mock_open_func.assert_called_once()
        assert mock_open_func.call_args[0][0] == "w"

    def test_subsequent_writes_use_mode_a(
        self,
        clean_logger_state: Any,
        mocker: MockerFixture,
    ) -> None:
        """Test subsequent log_state() opens file in 'a' mode."""
        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_open_func = mocker.patch("pathlib.Path.open", mock_open())

        # First call
        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        # Second call
        logger._frame_count = LoggingConstants().FPS * 2 - 1  # type: ignore[attr-defined]
        logger.log_state()

        # Second call should use 'a' mode
        assert mock_open_func.call_count == 2
        assert mock_open_func.call_args[0][0] == "a"


@pytest.mark.unit
class TestLogStateIntrospection:
    """Tests for log_state introspection of caller locals."""

    def test_captures_screen_size(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() captures screen size from Surface.get_size()."""
        mock_surface = mocker.MagicMock(spec=["get_size"])
        mock_surface.get_size.return_value = (1280, 720)
        # Make pygame detection work
        mock_surface.__class__.__module__ = "pygame.surface"

        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {"screen": mock_surface}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        # Verify JSON written contains screen_size
        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        assert data["screen_size"] == [1280, 720]

    def test_captures_sprite_position(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() captures sprite position attribute."""
        mock_sprite = mocker.MagicMock(spec=["position", "__class__"])
        mock_sprite.position = pygame.Vector2(100.5, 200.75)
        mock_sprite.__class__.__name__ = "MockSprite"

        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {"player": mock_sprite}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        assert "player" in data
        assert data["player"]["pos"] == [100.5, 200.75]

    def test_captures_sprite_velocity(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() captures sprite velocity attribute."""
        mock_sprite = mocker.MagicMock(spec=["position", "velocity", "__class__"])
        mock_sprite.position = pygame.Vector2(0, 0)
        mock_sprite.velocity = pygame.Vector2(5.123, 10.456)
        mock_sprite.__class__.__name__ = "Sprite"

        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {"obj": mock_sprite}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        assert data["obj"]["vel"] == [5.12, 10.46]  # Rounded to 2 decimals

    def test_captures_sprite_radius(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() captures sprite radius attribute."""
        mock_sprite = mocker.MagicMock(spec=["position", "radius", "__class__"])
        mock_sprite.position = pygame.Vector2(0, 0)
        mock_sprite.radius = 20
        mock_sprite.__class__.__name__ = "Circle"

        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {"circle": mock_sprite}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        assert data["circle"]["rad"] == 20

    def test_captures_sprite_rotation(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() captures sprite rotation attribute."""
        mock_sprite = mocker.MagicMock(spec=["position", "rotation", "__class__"])
        mock_sprite.position = pygame.Vector2(0, 0)
        mock_sprite.rotation = 45.678
        mock_sprite.__class__.__name__ = "Player"

        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {"player": mock_sprite}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        assert data["player"]["rot"] == 45.68  # Rounded to 2 decimals

    def test_handles_sprite_groups(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() detects and logs pygame.sprite.Group."""
        mock_sprite1 = mocker.MagicMock(spec=["position", "__class__"])
        mock_sprite1.position = pygame.Vector2(10, 20)
        mock_sprite1.__class__.__name__ = "Asteroid"

        mock_sprite2 = mocker.MagicMock(spec=["position", "__class__"])
        mock_sprite2.position = pygame.Vector2(30, 40)
        mock_sprite2.__class__.__name__ = "Asteroid"

        mock_group = mocker.MagicMock(spec=["__class__", "__iter__", "__len__"])
        mock_group.__class__.__name__ = "Group"
        mock_group.__iter__.return_value = iter([mock_sprite1, mock_sprite2])
        mock_group.__len__.return_value = 2

        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {"asteroids": mock_group}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        assert "asteroids" in data
        assert data["asteroids"]["count"] == 2
        assert len(data["asteroids"]["sprites"]) == 2

    def test_sprite_sample_limit(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() respects SPRITE_SAMPLE_LIMIT."""
        # Create more sprites than the limit
        limit = LoggingConstants().SPRITE_SAMPLE_LIMIT
        sprites = []
        for i in range(limit + 5):
            mock_sprite = mocker.MagicMock(spec=["position", "__class__"])
            mock_sprite.position = pygame.Vector2(i, i)
            mock_sprite.__class__.__name__ = "Sprite"
            sprites.append(mock_sprite)

        mock_group = mocker.MagicMock(spec=["__class__", "__iter__", "__len__"])
        mock_group.__class__.__name__ = "Group"
        mock_group.__iter__.return_value = iter(sprites)
        mock_group.__len__.return_value = len(sprites)

        mock_frame = mocker.MagicMock()
        mock_frame.f_back.f_locals = {"sprites": mock_group}
        mocker.patch("inspect.currentframe", return_value=mock_frame)

        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        # Should only log SPRITE_SAMPLE_LIMIT sprites
        assert len(data["sprites"]["sprites"]) == limit

    def test_handles_no_frame(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() handles inspect.currentframe() returning None."""
        mocker.patch("inspect.currentframe", return_value=None)
        mock_open_func = mocker.patch("pathlib.Path.open", mock_open())

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        # Should return early, no file operations
        mock_open_func.assert_not_called()

    def test_handles_no_frame_back(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_state() handles frame.f_back returning None."""
        mock_frame = mocker.MagicMock()
        mock_frame.f_back = None
        mocker.patch("inspect.currentframe", return_value=mock_frame)
        mock_open_func = mocker.patch("pathlib.Path.open", mock_open())

        logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
        logger.log_state()

        # Should return early, no file operations
        mock_open_func.assert_not_called()


@pytest.mark.unit
class TestLogStateTimestamps:
    """Tests for log_state timestamp handling."""

    def test_timestamp_format(
        self,
        clean_logger_state: Any,
        mocker: MockerFixture,
    ) -> None:
        """Test timestamp format is HH:MM:SS.mmm."""
        # Freeze time
        frozen_time = datetime(2024, 1, 1, 12, 30, 45, 123000, tzinfo=UTC)

        with freezegun.freeze_time(frozen_time):
            mock_frame = mocker.MagicMock()
            mock_frame.f_back.f_locals = {}
            mocker.patch("inspect.currentframe", return_value=mock_frame)

            mock_file = mocker.mock_open()
            mocker.patch("pathlib.Path.open", mock_file)

            # Reset start time to frozen time
            logger._start_time = frozen_time  # type: ignore[attr-defined]
            logger._frame_count = LoggingConstants().FPS - 1  # type: ignore[attr-defined]
            logger.log_state()

            written_data = mock_file().write.call_args[0][0]
            data = json.loads(written_data.strip())
            assert data["timestamp"] == "12:30:45.123"


@pytest.mark.unit
class TestLogEvent:
    """Tests for log_event function."""

    def test_creates_game_events_jsonl(
        self,
        clean_logger_state: Any,
        mocker: MockerFixture,
    ) -> None:
        """Test log_event() creates game_events.jsonl file."""
        mock_file = mocker.mock_open()
        mock_path = mocker.patch("logger.Path")
        mock_path.return_value.open = mock_file

        logger.log_event("test_event")

        # Verify Path was called with correct filename
        mock_path.assert_called_with("game_events.jsonl")
        mock_file.assert_called_once()

    def test_first_write_uses_mode_w(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test first log_event() opens file in 'w' mode."""
        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger.log_event("event1")

        assert mock_file.call_args[0][0] == "w"

    def test_subsequent_writes_use_mode_a(
        self,
        clean_logger_state: Any,
        mocker: MockerFixture,
    ) -> None:
        """Test subsequent log_event() opens file in 'a' mode."""
        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger.log_event("event1")
        logger.log_event("event2")

        # Second call should use 'a' mode
        assert mock_file.call_args[0][0] == "a"

    def test_includes_event_type(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_event() includes event_type in output."""
        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger.log_event("collision")

        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        assert data["type"] == "collision"

    def test_includes_custom_details(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test log_event() includes **details kwargs."""
        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger.log_event("score", points=100, player="Alice")

        written_data = mock_file().write.call_args[0][0]
        data = json.loads(written_data.strip())
        assert data["type"] == "score"
        assert data["points"] == 100
        assert data["player"] == "Alice"

    def test_jsonl_format(self, clean_logger_state: Any, mocker: MockerFixture) -> None:
        """Test output is valid JSONL."""
        mock_file = mocker.mock_open()
        mocker.patch("pathlib.Path.open", mock_file)

        logger.log_event("test")

        written_data = mock_file().write.call_args[0][0]
        # Should end with newline
        assert written_data.endswith("\n")
        # Should be valid JSON
        data = json.loads(written_data.strip())
        assert isinstance(data, dict)
