"""Game state and event logging for debugging and analysis."""

import inspect
import json
import math
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from constants import LOG_CONFIG

__all__ = ["log_event", "log_state"]


# pylint: disable=invalid-name  # Module-level state variables intentionally private
_frame_count = 0
_state_log_initialized = False
_event_log_initialized = False
_start_time = datetime.now(UTC)


def log_state() -> None:  # noqa: C901, PLR0912  # pylint: disable=too-many-return-statements,too-many-branches
    """Log current game state by introspecting caller's local variables."""
    global _frame_count, _state_log_initialized  # noqa: PLW0603  # pylint: disable=global-statement

    # Stop logging after `LOG_CONFIG.MAX_SECONDS` seconds
    if _frame_count > LOG_CONFIG.FPS * LOG_CONFIG.MAX_SECONDS:
        return

    # Take a snapshot approx. once per second
    _frame_count += 1
    if _frame_count % LOG_CONFIG.FPS != 0:
        return

    now = datetime.now(UTC)

    frame = inspect.currentframe()
    if frame is None:
        return

    frame_back = frame.f_back
    if frame_back is None:
        return

    local_vars = frame_back.f_locals.copy()

    screen_size = []
    game_state = {}

    for key, value in local_vars.items():
        if "pygame" in str(type(value)) and hasattr(  # pyright: ignore[reportUnknownArgumentType]
            value,
            "get_size",
        ):
            screen_size = value.get_size()

        if hasattr(value, "__class__") and "Group" in value.__class__.__name__:
            sprites_data = []

            for i, sprite in enumerate(value):
                if i >= LOG_CONFIG.SPRITE_SAMPLE_LIMIT:
                    break

                sprite_info = {"type": sprite.__class__.__name__}

                if hasattr(sprite, "position"):
                    sprite_info["pos"] = [
                        round(sprite.position.x, 2),
                        round(sprite.position.y, 2),
                    ]

                if hasattr(sprite, "velocity"):
                    sprite_info["vel"] = [
                        round(sprite.velocity.x, 2),
                        round(sprite.velocity.y, 2),
                    ]

                if hasattr(sprite, "radius"):
                    sprite_info["rad"] = sprite.radius

                if hasattr(sprite, "rotation"):
                    sprite_info["rot"] = round(sprite.rotation, 2)

                sprites_data.append(sprite_info)  # pyright: ignore[reportUnknownMemberType]

            game_state[key] = {"count": len(value), "sprites": sprites_data}

        if len(game_state) == 0 and hasattr(  # pyright: ignore[reportUnknownArgumentType]
            value,
            "position",
        ):
            sprite_info = {"type": value.__class__.__name__}

            sprite_info["pos"] = [
                round(value.position.x, 2),
                round(value.position.y, 2),
            ]

            if hasattr(value, "velocity"):
                sprite_info["vel"] = [
                    round(value.velocity.x, 2),
                    round(value.velocity.y, 2),
                ]

            if hasattr(value, "radius"):
                sprite_info["rad"] = value.radius

            if hasattr(value, "rotation"):
                sprite_info["rot"] = round(value.rotation, 2)

            game_state[key] = sprite_info

    entry = {  # pyright: ignore[reportUnknownVariableType]
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _frame_count,
        "screen_size": screen_size,
        **game_state,
    }

    # New log file on each run
    mode = "w" if not _state_log_initialized else "a"
    with Path("game_state.jsonl").open(mode, encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    _state_log_initialized = True


def log_event(event_type: str, **details: Any) -> None:  # noqa: ANN401
    global _event_log_initialized  # noqa: PLW0603  # pylint: disable=global-statement

    now = datetime.now(UTC)

    event = {
        "timestamp": now.strftime("%H:%M:%S.%f")[:-3],
        "elapsed_s": math.floor((now - _start_time).total_seconds()),
        "frame": _frame_count,
        "type": event_type,
        **details,
    }

    mode = "w" if not _event_log_initialized else "a"
    with Path("game_events.jsonl").open(mode, encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    _event_log_initialized = True
