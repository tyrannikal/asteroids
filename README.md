# Asteroids

A classic **Asteroids** arcade game built with Python and Pygame.

## Description

Navigate your spaceship through an asteroid field, blasting rocks into smaller pieces while avoiding collisions.

### Features

- **Smooth ship controls** — Rotate, thrust forward/backward, and shoot
- **Asteroid splitting** — Large asteroids break into smaller, faster pieces when hit
- **Collision detection** — Game ends if your ship touches an asteroid
- **60 FPS gameplay** — Consistent frame rate for smooth visuals

## Motivation

This project is a fun laser-blaster playground for implementing the **Tiger Style** coding methodology. It's also an opportunity to hone my skills with Python tooling, including:

- **pydantic** — Runtime validation and type enforcement
- **ruff** — Fast linting and formatting
- **pyright** — Static type checking
- **pylint** — Code analysis and error detection
- **bandit** — Security vulnerability scanning
- **vulture** — Dead code detection
- **radon** — Code complexity analysis
- **mkdocs** — Documentation generation
- **pre-commit** — Git hooks for automated checks

## Quick Start

**Requirements:** Python 3.13+

```bash
git clone https://github.com/tyrannikal/asteroids.git
cd asteroids
pip install .
python main.py
```

## Usage

| Key | Action |
|-----|--------|
| `W` | Thrust forward |
| `S` | Thrust backward |
| `A` | Rotate left |
| `D` | Rotate right |
| `Space` | Shoot |

## Contributing

### Setup

Clone the repository and install in editable mode:

```bash
git clone https://github.com/tyrannikal/asteroids.git
cd asteroids
pip install -e ".[test]"
```

### Running tests

```bash
pytest
```

### Submit a pull request

If you'd like to contribute, please fork the repository and open a pull request to the `main` branch.
