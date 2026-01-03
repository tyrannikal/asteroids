# Asteroids Game

A Tiger Style compliant Asteroids game implementation using pygame with strict Pydantic validation.

## Overview

This project implements a classic Asteroids-style game with a focus on:

- **Tiger Style Compliance**: Extensive assertions that validate runtime invariants
- **Type Safety**: Strict type checking with mypy and pyright
- **Validation**: Pydantic models for runtime validation of pygame objects
- **Code Quality**: Comprehensive linting with ruff, pylint, bandit, vulture, and radon
- **Testing**: 96%+ code coverage with pytest

## Key Features

- Player ship with triangle rendering and rotation
- Strict validation of all pygame types (Surface, Rect, etc.)
- Game state and event logging for debugging
- Immutable configuration with Pydantic models
- Pre-commit hooks ensuring code quality

## Quick Start

### Installation

```bash
# Install game dependencies
pip install -e .

# Install test dependencies
pip install -e ".[test]"

# Install documentation dependencies
pip install -e ".[docs]"
```

### Running the Game

```bash
python main.py
```

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
mkdocs build
```

### Serving Documentation Locally

```bash
mkdocs serve
```

## Project Structure

```
asteroids/
├── main.py                  # Game entry point and main loop
├── player.py                # Player ship class
├── circleshape.py          # Base class for circular game objects
├── constants.py            # Validated game constants
├── logger.py               # Game state and event logging
├── validationfunctions.py  # Pydantic wrappers for pygame types
├── tests/                  # Comprehensive test suite
└── docs/                   # Documentation source files
```

## Development Philosophy

This project follows "Tiger Style" development:

- Assertions are never disabled (Python must not run with -O flag)
- Every assumption is validated at runtime
- Type hints are comprehensive and checked strictly
- Code coverage must remain above 90%
- All quality tools must pass before commit

Documentation follows the principle of "docstrings only where they add value" - simple, self-evident code doesn't need docstrings, but complex logic and abstractions are well-documented.

## Next Steps

- Browse the [API Reference](api/main.md) for detailed code documentation
- Read about [Testing](development/testing.md) practices
- Learn about [Code Style](development/style.md) requirements
