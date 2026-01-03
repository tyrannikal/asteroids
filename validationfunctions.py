"""Pydantic validation wrappers for pygame types."""
# pylint: disable=c-extension-no-member,no-self-argument
# Pygame types are C extensions, validators use cls not self

from typing import Any

import pygame
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
)


class SurfaceWrapped(BaseModel):
    """Pydantic wrapper for pygame.Surface with strict validation."""

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
    """Pydantic wrapper for pygame.Rect with strict validation."""

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
