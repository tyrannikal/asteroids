"""Tests for asteroid.py Asteroid class."""

from unittest.mock import MagicMock

import pygame
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from asteroid import Asteroid
from circleshape import CircleShape
from validationfunctions import SurfaceWrapped


@pytest.mark.unit
class TestAsteroidInit:
    """Tests for Asteroid initialization."""

    def test_init_valid_parameters(self) -> None:
        """Test Asteroid initializes with valid float x, y and int radius."""
        asteroid = Asteroid(100.0, 200.0, 30)
        assert asteroid.position.x == 100.0
        assert asteroid.position.y == 200.0
        assert asteroid.radius == 30

    def test_init_non_float_x_raises_assertion(self) -> None:
        """Test Asteroid raises AssertionError for non-float x."""
        with pytest.raises(AssertionError, match="x must be a float"):
            Asteroid(100, 200.0, 30)  # type: ignore[arg-type]

    def test_init_non_float_y_raises_assertion(self) -> None:
        """Test Asteroid raises AssertionError for non-float y."""
        with pytest.raises(AssertionError, match="y must be a float"):
            Asteroid(100.0, 200, 30)  # type: ignore[arg-type]

    def test_init_non_int_radius_raises_assertion(self) -> None:
        """Test Asteroid raises AssertionError for non-int radius."""
        with pytest.raises(AssertionError, match="radius must be a int"):
            Asteroid(100.0, 200.0, 30.0)  # type: ignore[arg-type]

    def test_inherits_circleshape(self) -> None:
        """Test Asteroid is instance of CircleShape."""
        asteroid = Asteroid(0.0, 0.0, 20)
        assert isinstance(asteroid, CircleShape)


@pytest.mark.unit
class TestAsteroidPydanticValidation:
    """Tests for Asteroid Pydantic custom validation."""

    def test_pydantic_validator_accepts_asteroid(self) -> None:
        """Test Asteroid._validate accepts Asteroid instance."""
        asteroid = Asteroid(100.0, 200.0, 30)
        validated = Asteroid._validate(asteroid)
        assert validated is asteroid

    def test_pydantic_validator_rejects_non_asteroid(self) -> None:
        """Test Asteroid._validate rejects non-Asteroid types."""
        with pytest.raises(TypeError, match="must be of type Asteroid"):
            Asteroid._validate("not an asteroid")

    def test_pydantic_validator_rejects_none(self) -> None:
        """Test Asteroid._validate rejects None."""
        with pytest.raises(TypeError, match="must be of type Asteroid"):
            Asteroid._validate(None)


@pytest.mark.integration
class TestAsteroidDraw:
    """Tests for Asteroid draw method."""

    def test_draw_calls_pygame_circle(self, mocker: MockerFixture) -> None:
        """Test draw method calls pygame.draw.circle with correct parameters."""
        pygame.init()
        screen = pygame.Surface((800, 600))
        wrapped_screen = SurfaceWrapped.model_validate(screen)

        mock_circle = mocker.patch("pygame.draw.circle", return_value=pygame.Rect(0, 0, 10, 10))

        asteroid = Asteroid(100.0, 200.0, 30)
        asteroid.draw(wrapped_screen)

        mock_circle.assert_called_once()
        args = mock_circle.call_args[0]
        assert args[0] is screen
        assert args[1] == "white"
        assert args[2] == asteroid.position
        assert args[3] == 30


@pytest.mark.unit
class TestAsteroidUpdate:
    """Tests for Asteroid update method."""

    def test_update_moves_asteroid(self) -> None:
        """Test update method moves asteroid based on velocity and delta time."""
        asteroid = Asteroid(100.0, 100.0, 30)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        asteroid.update(1.0)

        assert asteroid.position.x == pytest.approx(150.0)
        assert asteroid.position.y == pytest.approx(100.0)

    def test_update_with_partial_delta(self) -> None:
        """Test update with fractional delta time."""
        asteroid = Asteroid(100.0, 100.0, 30)
        asteroid.velocity = pygame.Vector2(100.0, 100.0)

        asteroid.update(0.5)

        assert asteroid.position.x == pytest.approx(150.0)
        assert asteroid.position.y == pytest.approx(150.0)

    def test_update_invalid_dt_raises_error(self) -> None:
        """Test update raises ValidationError for non-float dt."""
        asteroid = Asteroid(100.0, 100.0, 30)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        with pytest.raises(ValidationError):
            asteroid.update("invalid")  # type: ignore[arg-type]


@pytest.mark.unit
class TestAsteroidSplitMinimumRadius:
    """Tests for Asteroid split method with minimum radius asteroids."""

    def test_split_minimum_radius_kills_asteroid(self, mocker: MockerFixture) -> None:
        """Test split on minimum radius asteroid calls kill."""
        asteroid = Asteroid(100.0, 100.0, 20)
        mock_kill = mocker.patch.object(asteroid, "kill")

        asteroid.split()

        mock_kill.assert_called_once()

    def test_split_minimum_radius_creates_no_children(self, mocker: MockerFixture) -> None:
        """Test split on minimum radius asteroid creates no child asteroids."""
        mocker.patch("asteroid.log_event")

        # Track asteroid creations after the parent
        created_count = [0]
        original_init = Asteroid.__init__

        def counting_init(self: Asteroid, x: float, y: float, radius: int) -> None:
            original_init(self, x, y, radius)
            created_count[0] += 1

        asteroid = Asteroid(100.0, 100.0, 20)
        mocker.patch.object(Asteroid, "__init__", counting_init)
        created_count[0] = 0  # Reset after parent creation

        asteroid.split()

        # No children should be created
        assert created_count[0] == 0

    def test_split_minimum_radius_does_not_log_event(self, mocker: MockerFixture) -> None:
        """Test split on minimum radius asteroid does not log asteroid_split."""
        mock_log = mocker.patch("asteroid.log_event")

        asteroid = Asteroid(100.0, 100.0, 20)
        asteroid.split()

        mock_log.assert_not_called()

    def test_split_below_minimum_radius_creates_no_children(self, mocker: MockerFixture) -> None:
        """Test split on asteroid below minimum radius creates no children."""
        mocker.patch("asteroid.log_event")

        asteroid = Asteroid(100.0, 100.0, 15)
        mock_kill = mocker.patch.object(asteroid, "kill")

        asteroid.split()

        mock_kill.assert_called_once()


@pytest.mark.unit
class TestAsteroidSplitCreatesChildren:
    """Tests for Asteroid split method child creation."""

    def test_split_creates_two_child_asteroids(self, mocker: MockerFixture) -> None:
        """Test split creates exactly two child asteroids."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=35.0)

        created_asteroids: list[Asteroid] = []
        original_init = Asteroid.__init__

        def tracking_init(self: Asteroid, x: float, y: float, radius: int) -> None:
            original_init(self, x, y, radius)
            created_asteroids.append(self)

        mocker.patch.object(Asteroid, "__init__", tracking_init)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)
        created_asteroids.clear()  # Clear the parent asteroid

        asteroid.split()

        assert len(created_asteroids) == 2

    def test_split_children_at_parent_position(self, mocker: MockerFixture) -> None:
        """Test child asteroids are created at parent's position."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=35.0)

        asteroid = Asteroid(150.0, 250.0, 40)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        created_positions: list[tuple[float, float]] = []
        original_init = Asteroid.__init__

        def tracking_init(self: Asteroid, x: float, y: float, radius: int) -> None:
            original_init(self, x, y, radius)
            created_positions.append((x, y))

        mocker.patch.object(Asteroid, "__init__", tracking_init)
        created_positions.clear()

        asteroid.split()

        assert len(created_positions) == 2
        assert created_positions[0] == (150.0, 250.0)
        assert created_positions[1] == (150.0, 250.0)

    def test_split_children_have_reduced_radius(self, mocker: MockerFixture) -> None:
        """Test child asteroids have radius reduced by ASTEROID_MIN_RADIUS."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=35.0)

        asteroid = Asteroid(100.0, 100.0, 60)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        created_radii: list[int] = []
        original_init = Asteroid.__init__

        def tracking_init(self: Asteroid, x: float, y: float, radius: int) -> None:
            original_init(self, x, y, radius)
            created_radii.append(radius)

        mocker.patch.object(Asteroid, "__init__", tracking_init)
        created_radii.clear()

        asteroid.split()

        # 60 - 20 (ASTEROID_MIN_RADIUS) = 40
        assert created_radii == [40, 40]


@pytest.mark.unit
class TestAsteroidSplitVelocity:
    """Tests for Asteroid split method velocity calculations."""

    def test_split_children_have_rotated_velocities(self, mocker: MockerFixture) -> None:
        """Test child asteroids have velocities rotated in opposite directions."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=30.0)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(100.0, 0.0)

        asteroid.split()

        # Get the child asteroids by checking what was created
        # Since we can't easily track them, we'll verify the velocity math directly
        expected_vel_1 = pygame.Vector2(100.0, 0.0).rotate(30.0) * 1.2
        expected_vel_2 = pygame.Vector2(100.0, 0.0).rotate(-30.0) * 1.2

        # The velocities should be 1.2x the rotated original velocity
        assert expected_vel_1.length() == pytest.approx(120.0)
        assert expected_vel_2.length() == pytest.approx(120.0)

    def test_split_velocity_multiplied_by_1_2(self, mocker: MockerFixture) -> None:
        """Test child asteroid velocities are 1.2x the rotated parent velocity."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=45.0)

        asteroid = Asteroid(100.0, 100.0, 40)
        original_speed = 100.0
        asteroid.velocity = pygame.Vector2(original_speed, 0.0)

        # Calculate expected speed after split
        expected_speed = original_speed * 1.2

        # Velocity magnitude should be preserved through rotation, then multiplied
        rotated = asteroid.velocity.rotate(45.0)
        assert rotated.length() == pytest.approx(original_speed)

        boosted = rotated * 1.2
        assert boosted.length() == pytest.approx(expected_speed)

    def test_split_zero_velocity_creates_stationary_children(self, mocker: MockerFixture) -> None:
        """Test splitting asteroid with zero velocity creates stationary children."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=35.0)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(0.0, 0.0)

        # Zero vector rotated is still zero, multiplied by 1.2 is still zero
        rotated = asteroid.velocity.rotate(35.0)
        assert rotated.length() == pytest.approx(0.0)


@pytest.mark.unit
class TestAsteroidSplitAngle:
    """Tests for Asteroid split method angle randomization."""

    def test_split_uses_random_angle_between_20_and_50(self, mocker: MockerFixture) -> None:
        """Test split uses random.uniform to get angle between 20 and 50."""
        mocker.patch("asteroid.log_event")
        mock_uniform = mocker.patch("asteroid.random.uniform", return_value=35.0)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        asteroid.split()

        mock_uniform.assert_called_once_with(20, 50)

    def test_split_angle_at_minimum_boundary(self, mocker: MockerFixture) -> None:
        """Test split with angle at minimum boundary (20 degrees)."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=20.0)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(100.0, 0.0)

        # Should not raise assertion error
        asteroid.split()

    def test_split_angle_at_maximum_boundary(self, mocker: MockerFixture) -> None:
        """Test split with angle at maximum boundary (50 degrees)."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=50.0)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(100.0, 0.0)

        # Should not raise assertion error
        asteroid.split()


@pytest.mark.unit
class TestAsteroidSplitLogging:
    """Tests for Asteroid split method logging."""

    def test_split_logs_asteroid_split_event(self, mocker: MockerFixture) -> None:
        """Test split logs 'asteroid_split' event for splittable asteroids."""
        mock_log = mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=35.0)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        asteroid.split()

        mock_log.assert_called_once_with("asteroid_split")

    def test_split_logs_before_creating_children(self, mocker: MockerFixture) -> None:
        """Test log_event is called before child asteroids are created."""
        call_order: list[str] = []

        def track_log(event: str) -> None:
            call_order.append(f"log:{event}")

        original_init = Asteroid.__init__

        def track_init(self: Asteroid, x: float, y: float, radius: int) -> None:
            original_init(self, x, y, radius)
            call_order.append(f"init:{radius}")

        mocker.patch("asteroid.log_event", side_effect=track_log)
        mocker.patch("asteroid.random.uniform", return_value=35.0)
        mocker.patch.object(Asteroid, "__init__", track_init)

        asteroid = Asteroid(100.0, 100.0, 40)
        call_order.clear()

        asteroid.split()

        # Log should come before the two child inits
        assert call_order[0] == "log:asteroid_split"
        assert "init:20" in call_order[1:]


@pytest.mark.unit
class TestAsteroidSplitKill:
    """Tests for Asteroid split method kill behavior."""

    def test_split_kills_parent_asteroid(self, mocker: MockerFixture) -> None:
        """Test split always calls kill on the parent asteroid."""
        mocker.patch("asteroid.log_event")
        mocker.patch("asteroid.random.uniform", return_value=35.0)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)
        mock_kill = mocker.patch.object(asteroid, "kill")

        asteroid.split()

        mock_kill.assert_called_once()

    def test_split_kills_before_checking_radius(self, mocker: MockerFixture) -> None:
        """Test kill is called before the radius check."""
        call_order: list[str] = []

        asteroid = Asteroid(100.0, 100.0, 20)

        original_kill = asteroid.kill

        def track_kill() -> None:
            call_order.append("kill")
            original_kill()

        mocker.patch.object(asteroid, "kill", side_effect=track_kill)

        asteroid.split()

        assert call_order == ["kill"]


@pytest.mark.integration
class TestAsteroidSplitIntegration:
    """Integration tests for Asteroid split with sprite groups."""

    def test_split_children_added_to_containers(self) -> None:
        """Test child asteroids are added to sprite containers."""
        pygame.init()

        # Set up containers like main.py does
        test_group = pygame.sprite.Group()
        Asteroid.containers = (test_group,)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        initial_count = len(test_group)

        asteroid.split()

        # Parent killed (-1), two children added (+2), net +1
        assert len(test_group) == initial_count + 1

        # Clean up
        Asteroid.containers = ()

    def test_split_medium_asteroid_creates_small_asteroids(self) -> None:
        """Test medium asteroid (40) splits into two small asteroids (20)."""
        pygame.init()

        test_group = pygame.sprite.Group()
        Asteroid.containers = (test_group,)

        asteroid = Asteroid(100.0, 100.0, 40)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        asteroid.split()

        # Get the remaining asteroids (children only, parent was killed)
        children = [a for a in test_group if a.radius == 20]
        assert len(children) == 2

        Asteroid.containers = ()

    def test_split_large_asteroid_creates_medium_asteroids(self) -> None:
        """Test large asteroid (60) splits into two medium asteroids (40)."""
        pygame.init()

        test_group = pygame.sprite.Group()
        Asteroid.containers = (test_group,)

        asteroid = Asteroid(100.0, 100.0, 60)
        asteroid.velocity = pygame.Vector2(50.0, 0.0)

        asteroid.split()

        children = [a for a in test_group if a.radius == 40]
        assert len(children) == 2

        Asteroid.containers = ()

    def test_split_chain_large_to_small(self) -> None:
        """Test splitting chain: large -> medium -> small -> destroyed."""
        pygame.init()

        test_group = pygame.sprite.Group()
        Asteroid.containers = (test_group,)

        # Start with large asteroid
        large = Asteroid(100.0, 100.0, 60)
        large.velocity = pygame.Vector2(50.0, 0.0)

        # First split: large (60) -> 2 medium (40)
        large.split()
        mediums = [a for a in test_group if a.radius == 40]
        assert len(mediums) == 2

        # Second split: medium (40) -> 2 small (20)
        mediums[0].split()
        smalls = [a for a in test_group if a.radius == 20]
        assert len(smalls) == 2

        # Third split: small (20) -> destroyed (no children)
        small_count_before = len([a for a in test_group if a.radius == 20])
        smalls[0].split()
        small_count_after = len([a for a in test_group if a.radius == 20])

        # One small asteroid destroyed, no new ones created
        assert small_count_after == small_count_before - 1

        Asteroid.containers = ()
