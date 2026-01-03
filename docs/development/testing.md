# Testing

The Asteroids project maintains comprehensive test coverage with pytest.

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_player.py

# Run tests matching a pattern
pytest -k "test_player"
```

## Test Organization

Tests are organized in the `tests/` directory with the following structure:

- `conftest.py` - Shared fixtures and pytest configuration
- `test_*.py` - Test modules matching source modules

## Test Markers

Tests are marked with custom markers:

- `@pytest.mark.unit` - Unit tests that don't require pygame initialization
- `@pytest.mark.integration` - Integration tests requiring pygame.init()

Run specific markers:

```bash
pytest -m unit
pytest -m integration
```

## Code Coverage

The project enforces 90%+ code coverage. Current coverage: **96.56%**

Coverage reports are generated in:
- Terminal output (during test run)
- `htmlcov/` directory (open `htmlcov/index.html` in browser)

## Testing Philosophy

### Don't Mock What You Don't Own

The test suite follows the principle of not mocking external libraries (like pygame). Instead:

- Use real pygame objects when possible
- Mock only I/O boundaries (file operations, time, etc.)
- Validate actual behavior, not implementation details

### Test What Matters

- Focus on testing behavior and invariants
- Don't test tautologies or framework guarantees
- Validate type constraints and assertions fire correctly

## Key Fixtures

### `clean_logger_state`

Resets logger module state between tests to ensure isolation.

```python
def test_logging(clean_logger_state):
    # Logger state is clean
    log_state()
```

### `mock_pygame_init`

Provides a mocked pygame initialization for tests that need it.

```python
def test_game_init(mock_pygame_init):
    # pygame.init() is mocked
    start_game()
```

## Pre-commit Integration

Tests run automatically on every commit via pre-commit hooks:

```bash
# Run pre-commit manually
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install
```

The pytest hook ensures all tests pass and coverage remains above 90% before allowing commits.
