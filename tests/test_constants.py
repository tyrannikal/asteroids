"""Tests for constants.py Pydantic models."""

import pytest
from pydantic import ValidationError

from constants import GameArea, LoggingConstants, PlayerStats


@pytest.mark.unit
class TestPlayerStats:
    """Tests for PlayerStats Pydantic model."""

    def test_default_values(self) -> None:
        """Test PlayerStats uses correct default values."""
        stats = PlayerStats()
        assert stats.PLAYER_RADIUS == 20
        assert stats.LINE_WIDTH == 2

    def test_custom_valid_values(self) -> None:
        """Test PlayerStats accepts valid custom values."""
        stats = PlayerStats(PLAYER_RADIUS=30, LINE_WIDTH=3)
        assert stats.PLAYER_RADIUS == 30
        assert stats.LINE_WIDTH == 3

    def test_negative_radius_raises_error(self) -> None:
        """Test negative PLAYER_RADIUS raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerStats(PLAYER_RADIUS=-5)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_radius_raises_error(self) -> None:
        """Test zero PLAYER_RADIUS raises ValidationError (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerStats(PLAYER_RADIUS=0)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_negative_line_width_raises_error(self) -> None:
        """Test negative LINE_WIDTH raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerStats(LINE_WIDTH=-1)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_line_width_raises_error(self) -> None:
        """Test zero LINE_WIDTH raises ValidationError (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            PlayerStats(LINE_WIDTH=0)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_immutability(self) -> None:
        """Test PlayerStats is frozen (cannot modify fields)."""
        stats = PlayerStats()
        with pytest.raises(ValidationError):
            stats.PLAYER_RADIUS = 50  # type: ignore[misc]

    def test_float_radius_converted_to_int(self) -> None:
        """Test float PLAYER_RADIUS is converted to int."""
        stats = PlayerStats(PLAYER_RADIUS=25.7)
        assert stats.PLAYER_RADIUS == 25
        assert isinstance(stats.PLAYER_RADIUS, int)

    def test_float_line_width_converted_to_int(self) -> None:
        """Test float LINE_WIDTH is converted to int."""
        stats = PlayerStats(LINE_WIDTH=3.9)
        assert stats.LINE_WIDTH == 3
        assert isinstance(stats.LINE_WIDTH, int)


@pytest.mark.unit
class TestGameArea:
    """Tests for GameArea Pydantic model."""

    def test_default_values(self) -> None:
        """Test GameArea uses correct default dimensions."""
        area = GameArea()
        assert area.SCREEN_WIDTH == 1280
        assert area.SCREEN_HEIGHT == 720

    def test_custom_valid_dimensions(self) -> None:
        """Test GameArea accepts valid custom dimensions."""
        area = GameArea(SCREEN_WIDTH=1920, SCREEN_HEIGHT=1080)
        assert area.SCREEN_WIDTH == 1920
        assert area.SCREEN_HEIGHT == 1080

    def test_negative_width_raises_error(self) -> None:
        """Test negative SCREEN_WIDTH raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GameArea(SCREEN_WIDTH=-100)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_width_raises_error(self) -> None:
        """Test zero SCREEN_WIDTH raises ValidationError (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            GameArea(SCREEN_WIDTH=0)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_negative_height_raises_error(self) -> None:
        """Test negative SCREEN_HEIGHT raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            GameArea(SCREEN_HEIGHT=-50)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_height_raises_error(self) -> None:
        """Test zero SCREEN_HEIGHT raises ValidationError (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            GameArea(SCREEN_HEIGHT=0)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_immutability(self) -> None:
        """Test GameArea is frozen."""
        area = GameArea()
        with pytest.raises(ValidationError):
            area.SCREEN_WIDTH = 1920  # type: ignore[misc]

    def test_float_width_converted_to_int(self) -> None:
        """Test float SCREEN_WIDTH is converted to int."""
        area = GameArea(SCREEN_WIDTH=1920.8)
        assert area.SCREEN_WIDTH == 1920
        assert isinstance(area.SCREEN_WIDTH, int)

    def test_float_height_converted_to_int(self) -> None:
        """Test float SCREEN_HEIGHT is converted to int."""
        area = GameArea(SCREEN_HEIGHT=1080.5)
        assert area.SCREEN_HEIGHT == 1080
        assert isinstance(area.SCREEN_HEIGHT, int)

    def test_very_large_dimensions(self) -> None:
        """Test GameArea accepts very large valid dimensions."""
        area = GameArea(SCREEN_WIDTH=10000, SCREEN_HEIGHT=10000)
        assert area.SCREEN_WIDTH == 10000
        assert area.SCREEN_HEIGHT == 10000


@pytest.mark.unit
class TestLoggingConstants:
    """Tests for LoggingConstants Pydantic model."""

    def test_default_values(self) -> None:
        """Test LoggingConstants uses correct defaults."""
        log_config = LoggingConstants()
        assert log_config.FPS == 60
        assert log_config.MAX_SECONDS == 16
        assert log_config.SPRITE_SAMPLE_LIMIT == 10

    def test_custom_valid_values(self) -> None:
        """Test LoggingConstants accepts valid values."""
        log_config = LoggingConstants(FPS=30, MAX_SECONDS=10, SPRITE_SAMPLE_LIMIT=5)
        assert log_config.FPS == 30
        assert log_config.MAX_SECONDS == 10
        assert log_config.SPRITE_SAMPLE_LIMIT == 5

    def test_negative_fps_raises_error(self) -> None:
        """Test negative FPS raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConstants(FPS=-10)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_fps_raises_error(self) -> None:
        """Test zero FPS raises ValidationError (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConstants(FPS=0)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_negative_max_seconds_raises_error(self) -> None:
        """Test negative MAX_SECONDS raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConstants(MAX_SECONDS=-5)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_max_seconds_raises_error(self) -> None:
        """Test zero MAX_SECONDS raises ValidationError (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConstants(MAX_SECONDS=0)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_negative_sprite_limit_raises_error(self) -> None:
        """Test negative SPRITE_SAMPLE_LIMIT raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConstants(SPRITE_SAMPLE_LIMIT=-1)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_zero_sprite_limit_raises_error(self) -> None:
        """Test zero SPRITE_SAMPLE_LIMIT raises ValidationError (gt=0)."""
        with pytest.raises(ValidationError) as exc_info:
            LoggingConstants(SPRITE_SAMPLE_LIMIT=0)
        assert "greater than 0" in str(exc_info.value).lower()

    def test_immutability(self) -> None:
        """Test LoggingConstants is frozen."""
        log_config = LoggingConstants()
        with pytest.raises(ValidationError):
            log_config.FPS = 30  # type: ignore[misc]

    def test_float_fps_converted_to_int(self) -> None:
        """Test float FPS is converted to int."""
        log_config = LoggingConstants(FPS=120.9)
        assert log_config.FPS == 120
        assert isinstance(log_config.FPS, int)

    def test_float_max_seconds_converted_to_int(self) -> None:
        """Test float MAX_SECONDS is converted to int."""
        log_config = LoggingConstants(MAX_SECONDS=30.5)
        assert log_config.MAX_SECONDS == 30
        assert isinstance(log_config.MAX_SECONDS, int)

    def test_float_sprite_limit_converted_to_int(self) -> None:
        """Test float SPRITE_SAMPLE_LIMIT is converted to int."""
        log_config = LoggingConstants(SPRITE_SAMPLE_LIMIT=15.7)
        assert log_config.SPRITE_SAMPLE_LIMIT == 15
        assert isinstance(log_config.SPRITE_SAMPLE_LIMIT, int)

    def test_very_high_fps(self) -> None:
        """Test LoggingConstants accepts very high valid FPS."""
        log_config = LoggingConstants(FPS=240)
        assert log_config.FPS == 240
