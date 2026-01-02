"""Tests for validationfunctions.py Pydantic wrappers."""

from unittest.mock import MagicMock

import pygame
import pytest
from pydantic import ValidationError

from validationfunctions import RectWrapped, SurfaceWrapped


class TestSurfaceWrapped:
    """Tests for SurfaceWrapped Pydantic model."""

    def test_wrap_valid_surface(self, mock_surface: MagicMock) -> None:
        """Test SurfaceWrapped accepts pygame.Surface."""
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        assert wrapped.object is mock_surface

    def test_reject_non_surface_string(self) -> None:
        """Test SurfaceWrapped rejects string input."""
        with pytest.raises(ValidationError) as exc_info:
            SurfaceWrapped.model_validate("not a surface")
        assert "must receive a type pygame.Surface" in str(exc_info.value)

    def test_reject_non_surface_int(self) -> None:
        """Test SurfaceWrapped rejects integer input."""
        with pytest.raises(ValidationError) as exc_info:
            SurfaceWrapped.model_validate(42)
        assert "must receive a type pygame.Surface" in str(exc_info.value)

    def test_reject_non_surface_none(self) -> None:
        """Test SurfaceWrapped rejects None input."""
        with pytest.raises(ValidationError) as exc_info:
            SurfaceWrapped.model_validate(None)
        assert "must receive a type pygame.Surface" in str(exc_info.value)

    def test_reject_rect_instead_of_surface(self, mock_rect: pygame.rect.Rect) -> None:
        """Test SurfaceWrapped rejects pygame.Rect."""
        with pytest.raises(ValidationError) as exc_info:
            SurfaceWrapped.model_validate(mock_rect)
        assert "must receive a type pygame.Surface" in str(exc_info.value)

    def test_model_validator_preprocessing(self, mock_surface: MagicMock) -> None:
        """Test model_validator converts raw Surface to dict."""
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        assert isinstance(wrapped.object, pygame.surface.Surface)

    def test_immutability(self, mock_surface: MagicMock) -> None:
        """Test SurfaceWrapped is frozen (cannot reassign object)."""
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        new_surface = MagicMock(spec=pygame.surface.Surface)
        with pytest.raises(ValidationError):
            wrapped.object = new_surface  # type: ignore[misc]

    def test_extra_fields_forbidden(self, mock_surface: MagicMock) -> None:
        """Test SurfaceWrapped forbids extra fields."""
        with pytest.raises(ValidationError) as exc_info:
            SurfaceWrapped(object=mock_surface, extra_field="value")  # type: ignore[call-arg]
        assert "extra" in str(exc_info.value).lower()

    def test_dict_with_object_key(self, mock_surface: MagicMock) -> None:
        """Test SurfaceWrapped rejects dict input (model_validator checks raw Surface)."""
        # The model_validator expects raw Surface, not dict
        with pytest.raises(ValidationError):
            SurfaceWrapped.model_validate({"object": mock_surface})

    def test_access_object_attribute(self, mock_surface: MagicMock) -> None:
        """Test accessing wrapped Surface object."""
        mock_surface.get_size.return_value = (1280, 720)
        wrapped = SurfaceWrapped.model_validate(mock_surface)
        assert wrapped.object.get_size() == (1280, 720)


class TestRectWrapped:
    """Tests for RectWrapped Pydantic model."""

    def test_wrap_valid_rect(self, mock_rect: pygame.rect.Rect) -> None:
        """Test RectWrapped accepts pygame.Rect."""
        wrapped = RectWrapped.model_validate(mock_rect)
        assert wrapped.object is mock_rect

    def test_reject_non_rect_string(self) -> None:
        """Test RectWrapped rejects string input."""
        with pytest.raises(ValidationError) as exc_info:
            RectWrapped.model_validate("not a rect")
        assert "must receive a type pygame.Surface" in str(exc_info.value)

    def test_reject_non_rect_int(self) -> None:
        """Test RectWrapped rejects integer input."""
        with pytest.raises(ValidationError) as exc_info:
            RectWrapped.model_validate(123)
        assert "must receive a type pygame.Surface" in str(exc_info.value)

    def test_reject_non_rect_none(self) -> None:
        """Test RectWrapped rejects None input."""
        with pytest.raises(ValidationError) as exc_info:
            RectWrapped.model_validate(None)
        assert "must receive a type pygame.Surface" in str(exc_info.value)

    def test_reject_surface_instead_of_rect(self, mock_surface: MagicMock) -> None:
        """Test RectWrapped rejects pygame.Surface."""
        with pytest.raises(ValidationError) as exc_info:
            RectWrapped.model_validate(mock_surface)
        assert "must receive a type pygame.Surface" in str(exc_info.value)

    def test_model_validator_preprocessing(self, mock_rect: pygame.rect.Rect) -> None:
        """Test model_validator converts raw Rect to dict."""
        wrapped = RectWrapped.model_validate(mock_rect)
        assert isinstance(wrapped.object, pygame.rect.Rect)

    def test_immutability(self, mock_rect: pygame.rect.Rect) -> None:
        """Test RectWrapped is frozen."""
        wrapped = RectWrapped.model_validate(mock_rect)
        new_rect = pygame.rect.Rect(10, 10, 100, 100)
        with pytest.raises(ValidationError):
            wrapped.object = new_rect  # type: ignore[misc]

    def test_extra_fields_forbidden(self, mock_rect: pygame.rect.Rect) -> None:
        """Test RectWrapped forbids extra fields."""
        with pytest.raises(ValidationError) as exc_info:
            RectWrapped(object=mock_rect, extra_field="value")  # type: ignore[call-arg]
        assert "extra" in str(exc_info.value).lower()

    def test_dict_with_object_key(self, mock_rect: pygame.rect.Rect) -> None:
        """Test RectWrapped rejects dict input (model_validator checks raw Rect)."""
        # The model_validator expects raw Rect, not dict
        with pytest.raises(ValidationError):
            RectWrapped.model_validate({"object": mock_rect})

    def test_access_object_attribute(self, mock_rect: pygame.rect.Rect) -> None:
        """Test accessing wrapped Rect object properties."""
        wrapped = RectWrapped.model_validate(mock_rect)
        assert wrapped.object.width == 1280
        assert wrapped.object.height == 720

    def test_rect_with_different_dimensions(self) -> None:
        """Test RectWrapped with different Rect dimensions."""
        rect = pygame.rect.Rect(50, 100, 200, 300)
        wrapped = RectWrapped.model_validate(rect)
        assert wrapped.object.x == 50
        assert wrapped.object.y == 100
        assert wrapped.object.width == 200
        assert wrapped.object.height == 300
