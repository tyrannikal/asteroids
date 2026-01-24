from pydantic import BaseModel, ConfigDict, Field, field_validator

# pylint: disable=invalid-name
screen_width_literal = 1280
screen_height_literal = 720

player_radius_literal = 20
player_turn_speed_literal = 300
player_speed_literal = 200
player_shoot_speed_literal = 500
player_shot_radius_literal = 5
player_shoot_cooldown_seconds_literal = 0.3

asteroid_min_radius_literal = 20
asteroid_kinds_literal = 3
asteroid_spawn_rate_seconds_literal = 0.8
asteroid_max_radius_literal = asteroid_min_radius_literal * asteroid_kinds_literal

line_width_literal = 2
fps_literal = 60
max_seconds_literal = 16
sprite_sample_limit_literal = 10


class PlayerStats(BaseModel):
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
    PLAYER_TURN_SPEED: int = Field(
        gt=0,
        default=player_turn_speed_literal,
        validate_default=True,
    )
    PLAYER_SPEED: int = Field(
        gt=0,
        default=player_speed_literal,
        validate_default=True,
    )
    PLAYER_SHOOT_SPEED: int = Field(
        gt=0,
        default=player_shoot_speed_literal,
        validate_default=True,
    )
    PLAYER_SHOT_RADIUS: int = Field(
        gt=0,
        default=player_shot_radius_literal,
        validate_default=True,
    )
    PLAYER_SHOOT_COOLDOWN_SECONDS: float = Field(
        gt=0,
        default=player_shoot_cooldown_seconds_literal,
        validate_default=True,
    )
    model_config = ConfigDict(frozen=True)

    @field_validator(
        "PLAYER_RADIUS",
        "LINE_WIDTH",
        "PLAYER_TURN_SPEED",
        "PLAYER_SPEED",
        "PLAYER_SHOOT_SPEED",
        "PLAYER_SHOT_RADIUS",
        mode="before",
    )
    @classmethod
    def convert_to_int(cls, v: float) -> int:
        return int(v)

    @field_validator("PLAYER_SHOOT_COOLDOWN_SECONDS", mode="before")
    @classmethod
    def convert_to_float(cls, v: int) -> float:
        return float(v)


class AsteroidStats(BaseModel):
    ASTEROID_MIN_RADIUS: int = Field(
        gt=0,
        default=asteroid_min_radius_literal,
        validate_default=True,
    )
    ASTEROID_KINDS: int = Field(
        gt=0,
        default=asteroid_kinds_literal,
        validate_default=True,
    )
    ASTEROID_SPAWN_RATE_SECONDS: float = Field(
        gt=0,
        default=asteroid_spawn_rate_seconds_literal,
        validate_default=True,
    )
    ASTEROID_MAX_RADIUS: int = Field(
        gt=0,
        default=asteroid_max_radius_literal,
        validate_default=True,
    )
    model_config = ConfigDict(frozen=True)

    @field_validator(
        "ASTEROID_MIN_RADIUS",
        "ASTEROID_KINDS",
        "ASTEROID_MAX_RADIUS",
        mode="before",
    )
    @classmethod
    def convert_to_int(cls, v: float) -> int:
        return int(v)

    @field_validator("ASTEROID_SPAWN_RATE_SECONDS", mode="before")
    @classmethod
    def convert_to_float(cls, v: int) -> float:
        return float(v)


class GameArea(BaseModel):
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


PLAYER_STATS = PlayerStats()
ASTEROID_STATS = AsteroidStats()
GAME_AREA = GameArea()
LOG_CONFIG = LoggingConstants()
