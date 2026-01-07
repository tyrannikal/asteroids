# Vulture whitelist - pytest fixtures and Pydantic internals appear unused
# but are actually used via dependency injection or framework mechanisms

# Pytest fixture names (used as function parameters in tests via DI)
clean_logger_state
mock_pygame_init
mock_pygame_display
mock_vector2
assert_vector2_equal
create_mock_sprite_group

# Pydantic internals (used by the Pydantic framework)
model_config
convert_to_int
accept_raw_surface
accept_raw_rect
ensure_instance
__module__
