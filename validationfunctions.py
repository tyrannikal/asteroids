# pylint: disable=c-extension-no-member,no-self-argument

from typing import Any

import pygame
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)


class SurfaceWrapped(BaseModel):
    object: pygame.surface.Surface

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    @model_validator(mode="before")
    def accept_raw_surface(cls, data: Any) -> dict[str, Any]:  # noqa: N805, ANN401
        if not isinstance(data, pygame.surface.Surface):
            msg = "SurfaceWrapped must receive a type pygame.Surface or dict key"
            raise TypeError(msg)
        return {"object": data}

    @field_validator("object")
    def ensure_instance(cls, value: Any) -> pygame.surface.Surface:  # noqa: N805, ANN401
        if not isinstance(value, pygame.surface.Surface):
            msg = "must be pygame.surface.Surface"
            raise TypeError(msg)
        return value


class RectWrapped(BaseModel):
    object: pygame.rect.Rect

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    @model_validator(mode="before")
    def accept_raw_rect(cls, data: Any) -> dict[str, Any]:  # noqa: N805, ANN401
        if not isinstance(data, pygame.rect.Rect):
            msg = "RectWrapped must receive a type pygame.Surface or dict key"
            raise TypeError(msg)
        return {"object": data}

    @field_validator("object")
    def ensure_instance(cls, value: Any) -> pygame.rect.Rect:  # noqa: N805, ANN401
        if not isinstance(value, pygame.rect.Rect):
            msg = "must be pygame.rect.Rect"
            raise TypeError(msg)
        return value


class Vector2Wrapped(BaseModel):
    object: pygame.Vector2

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
    )

    @model_validator(mode="before")
    def accept_raw_vector2(cls, data: Any) -> dict[str, Any]:  # noqa: N805, ANN401
        if not isinstance(data, pygame.Vector2):
            msg = "Vector2Wrapped must receive a type pygame.Vector2 or dict key"
            raise TypeError(msg)
        return {"object": data}

    @field_validator("object")
    def ensure_instance(cls, value: Any) -> pygame.Vector2:  # noqa: N805, ANN401
        if not isinstance(value, pygame.Vector2):
            msg = "must be pygame.Vector2"
            raise TypeError(msg)
        return value
