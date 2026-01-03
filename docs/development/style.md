# Code Style

The Asteroids project follows strict code quality standards with multiple linting and analysis tools.

## Tiger Style Compliance

This project follows "Tiger Style" development principles:

### Assertions Always Enabled

Python must never run with optimization flags (`-O` or `-OO`):

```python
if sys.flags.optimize != 0:
    raise RuntimeError("Assertions are REQUIRED for Tiger Style compliance")
```

### Validate Everything

Every assumption about runtime state is validated with assertions:

```python
game_modules: tuple[int, int] = pygame.init()
assert isinstance(game_modules, tuple), "pygame.init() must return type tuple"
success_count, failure_count = game_modules
assert success_count > 0, "pygame.init() must have at least one module succeed"
assert failure_count == 0, "pygame.init() must not have any modules fail"
```

## Code Quality Tools

All tools run automatically via pre-commit hooks:

### Ruff

Fast Python linter and formatter:

```bash
# Format code
ruff format .

# Lint with auto-fix
ruff check --fix .
```

Configuration in `pyproject.toml`:
- Line length: 100
- Target: Python 3.13
- All rules enabled except docstring requirements

### Mypy

Static type checker in strict mode:

```bash
mypy .
```

Requirements:
- All functions must have type hints
- No `Any` types from untyped imports
- No implicit optionals

### Pyright

Additional strict type checking:

```bash
pyright
```

Provides additional type safety checks beyond mypy.

### Pylint

Code quality and complexity analysis:

```bash
pylint *.py
```

Limits:
- Max arguments: 5
- Max local variables: 15
- Max returns: 3
- Max branches: 12

### Bandit

Security vulnerability scanner:

```bash
bandit -r . -ll
```

Checks for common security issues in Python code.

### Vulture

Dead code detection:

```bash
vulture . --min-confidence 80
```

Identifies unused code (with whitelist for pytest fixtures).

### Radon

Cyclomatic complexity checker:

```bash
radon cc . -a -nb --min A
```

Enforces Grade A complexity (low complexity).

## Type Hints

All functions must have complete type hints:

```python
def new_player_center() -> Player:
    player: Player = Player(GameArea().SCREEN_WIDTH / 2, GameArea().SCREEN_HEIGHT / 2)
    return player
```

Use `# type: ignore[specific-error]` only when absolutely necessary.

## Documentation Standards

### Docstrings Only Where They Add Value

- Module docstrings describe file purpose
- Class docstrings describe abstractions
- Function docstrings only for complex/non-obvious logic
- Don't document self-evident code

Example of when to use docstrings:

```python
# YES - Complex, non-obvious behavior
def log_state() -> None:
    """Log current game state by introspecting caller's local variables."""
    # ... introspection magic ...

# NO - Self-evident from name and types
def new_player_center() -> Player:
    player: Player = Player(GameArea().SCREEN_WIDTH / 2, GameArea().SCREEN_HEIGHT / 2)
    return player
```

### Comments

Keep only functional comments:

- `# type: ignore[...]` - Type checker pragmas
- `# noqa: ...` - Linter suppressions
- `# pylint: disable=...` - Pylint suppressions

Remove explanatory comments that just restate the code.

## Pre-commit Hooks

Install hooks to enforce quality on every commit:

```bash
pre-commit install
```

Hook sequence:
1. ruff-format - Format code
2. ruff-lint - Lint and auto-fix
3. mypy - Type check
4. pyright - Additional type checking
5. pylint - Code quality check
6. bandit - Security scan
7. vulture - Dead code detection
8. pytest - Run tests with coverage
9. radon - Complexity check

All hooks must pass before commit is allowed.

## Pydantic Validation

Use Pydantic for runtime validation:

```python
class PlayerDimensions(BaseModel):
    PLAYER_RADIUS: int = Field(gt=0, default=player_radius_literal)
    LINE_WIDTH: int = Field(gt=0, default=line_width_literal)
    model_config = ConfigDict(frozen=True)
```

Validators should raise `TypeError` or `ValueError` (Pydantic wraps them in `ValidationError`).
