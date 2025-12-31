import pygame

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

class SurfaceWrapped(BaseModel):
    object: pygame.surface.Surface

    model_config = ConfigDict(arbitrary_types_allowed=True, 
                              extra="forbid", 
                              frozen=True, 
                              validate_assignment=True, 
                              )
    
    @model_validator(mode="before")
    def accept_raw_surface(cls, data):
        if not isinstance(data, pygame.surface.Surface):
            raise ValidationError("SurfaceWrapped must receive a type pygame.Surface or dict key")
        return {"object": data}

    @field_validator("object")
    def ensure_instance(cls, value):
        if not isinstance(value, pygame.surface.Surface):
            raise ValidationError("must be pygame.surface.Surface")
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
        if not isinstance(data, pygame.rect.Rect):
            raise ValidationError("RectWrapped must receive a type pygame.Surface or dict key")
        return {"object": data}


    @field_validator("object")
    def ensure_instance(cls, value):
        if not isinstance(value, pygame.rect.Rect):
            raise ValidationError("must be pygame.rect.Rect")
        return value

