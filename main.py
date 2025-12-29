import pygame
from typing import Any, Callable
from constants import SCREEN_WIDTH, SCREEN_HEIGHT 
from logger import log_state
from player import Player

from pydantic_core import CoreSchema, core_schema
from pydantic import BaseModel, ConfigDict, Field, field_validator, GetCoreSchemaHandler, model_validator, validate_call, ValidationError


class SurfaceWrapped(BaseModel):
    object: pygame.surface.Surface

    model_config = ConfigDict(arbitrary_types_allowed=True, 
                              extra="forbid", 
                              frozen=True, 
                              validate_assignment=True, 
                              )
    
    @model_validator(mode="before")
    def accept_raw_surface(cls, data):
        if isinstance(data, pygame.surface.Surface):
            return {"object": data}
        if isinstance(data, dict):
            return data
        raise TypeError(
            "SurfaceWrapped must receive a type pygame.Surface or dict key")


    @field_validator("object")
    def ensure_instance(cls, value):
        if not isinstance(value, pygame.surface.Surface):
            raise ValueError("must be pygame.surface.Surface")
        return value


class RectWrapped(BaseModel):
    object: pygame.rect.Rect

    model_config = ConfigDict(arbitrary_types_allowed=True, 
                              extra="forbid", 
                              frozen=True, 
                              validate_assignment=True, 
                              )

    @model_validator(mode="before")
    def accept_raw_rect(cls, data):
        if isinstance(data, pygame.rect.Rect):
            return {"object": data}
        if isinstance(data, dict):
            return data
        raise TypeError(
            "RectWrapped must receive a type pygame.Surface or dict key")


    @field_validator("object")
    def ensure_instance(cls, value):
        if not isinstance(value, pygame.rect.Rect):
            raise ValueError("must be pygame.rect.Rect")
        return value


class GameArea(BaseModel):
    width: int = Field(validate_default=True, default=SCREEN_WIDTH, gt=0, frozen=True)
    height: int = Field(validate_default=True, default=SCREEN_HEIGHT, gt=0, frozen=True)

    @property
    def GetWidth(self) -> int:
        return self.width

    @property
    def GetHeight(self) -> int:
        return self.height

    class ConfigDict:
        validate_assignment = True


game_area = GameArea() 


@validate_call(validate_return=True)
def PrintWelcomeMessage() -> None:
    assert pygame.__version__ == "2.6.1", "pygame version must be exactly 2.6.1"
    print(f"Starting Asteroids with pygame version: {pygame.__version__}")
    print(f"Screen width: {game_area.GetWidth}")
    print(f"Screen height: {game_area.GetHeight}")
    return None


@validate_call(validate_return=True)
def StartGame() -> None:
    game_modules: tuple = pygame.init()
    assert type(game_modules) == tuple, "pygame.init() must return type tuple"
    assert len(game_modules) == 2, "pygame.init() must return a tuple of length 2"
    assert game_modules[0] > 0, "pygame.init() must have at least one module succeed"
    assert game_modules[1] == 0, "pygame.init() must not have any modules fail"
    return None


@validate_call(validate_return=True)
def NewPlayerCenter() -> Player:
    player: Player = Player(game_area.GetWidth / 2, game_area.GetHeight / 2)
    return player

@validate_call(validate_return=True)
def FillBackground(screen: SurfaceWrapped, color: str) -> RectWrapped:
    assert color in pygame.colordict.THECOLORS, "background color must be listed in pygame.colordict.THECOLORS"
    unwrapped_screen: pygame.surface.Surface = screen.object

    background: pygame.rect.Rect = unwrapped_screen.fill(color)
    assert type(background) == pygame.rect.Rect

    background_size: tuple = pygame.Surface.get_size(unwrapped_screen)
    assert type(background_size) == tuple, "get_size must return type tuple"
    assert len(background_size) == 2, "get_size must return a tuple of length 2"
    assert background_size[0] == game_area.GetWidth, "screen background width must equal game_area width"
    assert background_size[1] == game_area.GetHeight, "screen background height must equal game_area height"

    return RectWrapped(object=background)


def main():
    welcome_message_return: None = PrintWelcomeMessage()
    assert welcome_message_return == None, "PrintWelcomeMessage must return type None"

    new_game: None = StartGame()
    assert new_game == None, "StartGame must return type None"

    clock: pygame.time.Clock = pygame.time.Clock()
    assert type(clock) == pygame.time.Clock, "pygame.time.Clock must return type Clock"
    dt: int = 0

    new_screen: pygame.surface.Surface = pygame.display.set_mode((game_area.GetWidth, game_area.GetHeight))
    assert type(new_screen) == pygame.surface.Surface, "pygame.display.set_mode must return type Surface"

    new_player: Player = NewPlayerCenter()
    assert type(new_player) == Player, "NewPlayerCenter() must return type Player"

    while(True):
        log_current_state: None = log_state()
        assert log_current_state == None, "log_state() must return type None"

        event_list: list = pygame.event.get()
        assert type(event_list) == list, "pygame.event.get() must return type list"
        for event in range(0, len(event_list)):
            if event_list[event].type == pygame.QUIT:
                return None

        background: RectWrapped = FillBackground(new_screen, "black")
        assert type(background) == RectWrapped, "FillBackground must return type RectWrapped"
        assert type(background.object) == pygame.rect.Rect, "FillBackground.object must be type pygame.rect.Rect"

        draw_player: None = new_player.draw(new_screen)
        assert draw_player == None, "player.draw must return type None"

        refresh_screen: None = pygame.display.flip()
        assert refresh_screen == None, "pygame.display.flip must return type None"

        tick: int = clock.tick(60)
        assert type(tick) == int, "clock.tick must return type int"
        assert tick >= 0, "clock.tick must return an integer >= 0"
        dt = tick / 1000


if __name__ == "__main__":
    main()

