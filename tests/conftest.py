"""Shared pytest fixtures for asteroids tests."""

from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pygame
import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_pygame_init(mocker: MockerFixture) -> MagicMock:
    """Mock pygame.init() to avoid actual SDL initialization.

    Returns:
        MagicMock of pygame.init() that returns (10, 0) for success.
    """
    return mocker.patch("pygame.init", return_value=(10, 0))


@pytest.fixture
def mock_pygame_display(mocker: MockerFixture) -> tuple[MagicMock, MagicMock]:
    """Mock pygame.display.set_mode() returning a mock Surface.

    Returns:
        Tuple of (mock_display, mock_surface).
    """
    mock_surface = MagicMock(spec=pygame.surface.Surface)
    mock_surface.get_size.return_value = (1280, 720)
    mock_surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
    mock_display = mocker.patch("pygame.display.set_mode", return_value=mock_surface)
    return mock_display, mock_surface


@pytest.fixture
def mock_surface() -> MagicMock:
    """Create a mock pygame Surface with common methods.

    Returns:
        MagicMock configured to act like pygame.Surface.
    """
    surface = MagicMock(spec=pygame.surface.Surface)
    surface.fill.return_value = pygame.rect.Rect(0, 0, 1280, 720)
    surface.get_size.return_value = (1280, 720)
    return surface


@pytest.fixture
def mock_rect() -> pygame.rect.Rect:
    """Create a real pygame Rect for testing.

    Returns:
        pygame.Rect instance.
    """
    return pygame.rect.Rect(0, 0, 1280, 720)


@pytest.fixture
def mock_vector2() -> Callable[[float, float], pygame.Vector2]:
    """Create factory for pygame.Vector2 instances.

    Returns:
        Factory function that creates Vector2 instances.
    """

    def _make_vector(x: float = 0, y: float = 0) -> pygame.Vector2:
        return pygame.Vector2(x, y)

    return _make_vector


@pytest.fixture
def clean_logger_state() -> Any:
    """Reset logger module state between tests.

    Yields:
        None - just provides cleanup functionality.
    """
    import logger

    # Store original state
    original_frame_count = getattr(logger, "_frame_count", 0)
    original_state_init = getattr(logger, "_state_log_initialized", False)
    original_event_init = getattr(logger, "_event_log_initialized", False)

    # Reset to clean state
    logger._frame_count = 0  # type: ignore[attr-defined]
    logger._state_log_initialized = False  # type: ignore[attr-defined]
    logger._event_log_initialized = False  # type: ignore[attr-defined]

    yield

    # Restore original state
    logger._frame_count = original_frame_count  # type: ignore[attr-defined]
    logger._state_log_initialized = original_state_init  # type: ignore[attr-defined]
    logger._event_log_initialized = original_event_init  # type: ignore[attr-defined]


def assert_vector2_equal(
    actual: pygame.Vector2,
    expected: tuple[float, float],
    tolerance: float = 0.01,
) -> None:
    """Assert Vector2 approximately equals expected (x, y).

    Args:
        actual: The actual Vector2 to check.
        expected: Tuple of (x, y) expected values.
        tolerance: Absolute tolerance for floating point comparison.

    Raises:
        AssertionError: If values don't match within tolerance.
    """
    assert abs(actual.x - expected[0]) < tolerance, f"x: {actual.x} != {expected[0]}"
    assert abs(actual.y - expected[1]) < tolerance, f"y: {actual.y} != {expected[1]}"


def create_mock_sprite_group(mocker: MockerFixture, sprites: list[Any]) -> MagicMock:
    """Create mock pygame.sprite.Group with sprites.

    Args:
        mocker: pytest-mock fixture.
        sprites: List of sprite objects to include in the group.

    Returns:
        MagicMock configured to act like pygame.sprite.Group.
    """
    group = mocker.MagicMock(spec=pygame.sprite.Group)
    group.__iter__.return_value = iter(sprites)
    group.__len__.return_value = len(sprites)
    return group
