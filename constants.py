from pydantic import BaseModel, ConfigDict, Field


screen_width_literal = 1280
screen_height_literal = 720
player_radius_literal = 20
line_width_literal = 2


class PlayerDimensions(BaseModel):
    PLAYER_RADIUS: int = Field(gt=0, default=player_radius_literal, validate_default=True)
    LINE_WIDTH: int = Field(gt=0, default=line_width_literal, validate_default=True)
    model_config = ConfigDict(frozen=True)


class GameArea(BaseModel):
    SCREEN_WIDTH: int = Field(gt=0, default=screen_width_literal, validate_default=True)
    SCREEN_HEIGHT: int = Field(gt=0, default=screen_height_literal, validate_default=True)
    model_config = ConfigDict(frozen=True)
