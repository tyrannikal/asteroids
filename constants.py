"""Game constants and configuration with Pydantic validation."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

# pylint: disable=invalid-name  # These are default literals for Pydantic fields
screen_width_literal = 1280
screen_height_literal = 720

player_radius_literal = 20
line_width_literal = 2

fps_literal = 60
max_seconds_literal = 16
sprite_sample_limit_literal = 10  # Maximum number of sprites to log per group


class PlayerDimensions(BaseModel):
    """Player visual dimensions with validated constraints."""

    PLAYER_RADIUS: int = Field(
        gt=0,
        default=player_radius_literal,
        validate_default=True,
    )
    LINE_WIDTH: int = Field(
        gt=0,
        default=line_width_literal,
        validate_default=True,
    )
    model_config = ConfigDict(frozen=True)

    @field_validator("PLAYER_RADIUS", "LINE_WIDTH", mode="before")
    @classmethod
    def convert_to_int(cls, v: float) -> int:
        return int(v)


class GameArea(BaseModel):
    """Game area screen dimensions with validated constraints."""

    SCREEN_WIDTH: int = Field(
        gt=0,
        default=screen_width_literal,
        validate_default=True,
    )
    SCREEN_HEIGHT: int = Field(
        gt=0,
        default=screen_height_literal,
        validate_default=True,
    )
    model_config = ConfigDict(frozen=True)

    @field_validator("SCREEN_WIDTH", "SCREEN_HEIGHT", mode="before")
    @classmethod
    def convert_to_int(cls, v: float) -> int:
        return int(v)


class LoggingConstants(BaseModel):
    """Logging configuration with validated constraints."""

    FPS: int = Field(
        gt=0,
        default=fps_literal,
        validate_default=True,
    )
    MAX_SECONDS: int = Field(
        gt=0,
        default=max_seconds_literal,
        validate_default=True,
    )
    SPRITE_SAMPLE_LIMIT: int = Field(
        gt=0,
        default=sprite_sample_limit_literal,
        validate_default=True,
    )
    model_config = ConfigDict(frozen=True)

    @field_validator("FPS", "MAX_SECONDS", "SPRITE_SAMPLE_LIMIT", mode="before")
    @classmethod
    def convert_to_int(cls, v: float) -> int:
        return int(v)


# Module-level singleton instances (immutable, validated constants)
PLAYER_DIMS = PlayerDimensions()
GAME_AREA = GameArea()
LOG_CONFIG = LoggingConstants()
