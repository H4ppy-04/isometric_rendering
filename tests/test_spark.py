import math

import pygame
import pytest

import main


def make_spark(**overrides):
    defaults = dict(location=[0.0, 0.0], angle=0.0, speed=1.0, color=(255, 255, 255))
    defaults.update(overrides)
    return main.Spark(**defaults)


def test_calculate_movement_along_positive_x_axis():
    spark = make_spark(angle=0.0, speed=2.0)

    dx, dy = spark.calculate_movement(dt=1.0)

    assert dx == pytest.approx(2.0)
    assert dy == pytest.approx(0.0, abs=1e-9)


def test_calculate_movement_along_positive_y_axis():
    spark = make_spark(angle=math.pi / 2, speed=2.0)

    dx, dy = spark.calculate_movement(dt=1.0)

    assert dx == pytest.approx(0.0, abs=1e-9)
    assert dy == pytest.approx(2.0)


def test_calculate_movement_scales_with_dt():
    spark = make_spark(angle=0.0, speed=2.0)

    dx, _ = spark.calculate_movement(dt=0.5)

    assert dx == pytest.approx(1.0)


def test_move_updates_location_according_to_angle_and_speed():
    spark = make_spark(location=[10.0, 10.0], angle=0.0, speed=5.0)

    spark.move(dt=1.0)

    assert spark.location[0] == pytest.approx(15.0)
    assert spark.location[1] == pytest.approx(10.0, abs=1e-9)


def test_move_reduces_speed_by_the_deceleration_constant():
    spark = make_spark(speed=1.0)

    spark.move(dt=1.0)

    assert spark.speed == pytest.approx(1.0 - main.SPEED_DECELERATION)


def test_move_kills_the_spark_once_speed_reaches_zero():
    spark = make_spark(speed=main.SPEED_DECELERATION)

    spark.move(dt=1.0)

    assert spark.speed == 0
    assert spark.alive is False


def test_move_clamps_speed_at_zero_rather_than_going_negative():
    spark = make_spark(speed=main.SPEED_DECELERATION / 2)

    spark.move(dt=1.0)

    assert spark.speed == 0


def test_move_keeps_spark_alive_while_speed_remains_positive():
    spark = make_spark(speed=10.0)

    spark.move(dt=1.0)

    assert spark.alive is True


def test_point_towards_does_nothing_when_already_at_target_angle():
    spark = make_spark(angle=math.pi / 4)

    spark.point_towards(target_angle=math.pi / 4, rotation_rate=0.1)

    assert spark.angle == pytest.approx(math.pi / 4)


def test_point_towards_snaps_to_target_when_within_rotation_rate():
    spark = make_spark(angle=0.0)

    spark.point_towards(target_angle=0.05, rotation_rate=0.1)

    assert spark.angle == pytest.approx(0.05)


def test_point_towards_steps_by_rotation_rate_when_target_is_far():
    spark = make_spark(angle=0.0)

    spark.point_towards(target_angle=math.pi / 2, rotation_rate=0.1)

    assert spark.angle == pytest.approx(0.1)


def test_point_towards_rotates_the_shortest_way_around():
    # From angle 0, rotating to -pi/2 is shorter going clockwise (negative)
    # than counter-clockwise, so the step should be negative even though
    # the target angle itself is negative-but-"far" in raw terms.
    spark = make_spark(angle=0.0)

    spark.point_towards(target_angle=-math.pi / 2, rotation_rate=0.1)

    assert spark.angle == pytest.approx(-0.1)


def test_velocity_adjust_points_angle_towards_resulting_movement_vector():
    spark = make_spark(angle=0.0, speed=1.0)

    spark.velocity_adjust(friction=1.0, force=0.0, terminal_velocity=100.0, dt=1.0)

    # With no friction/force change, the movement vector is unchanged, so
    # the angle should remain (numerically) the same.
    assert spark.angle == pytest.approx(0.0, abs=1e-9)


def test_velocity_adjust_bends_angle_downward_when_force_is_applied():
    spark = make_spark(angle=0.0, speed=1.0)

    spark.velocity_adjust(friction=1.0, force=5.0, terminal_velocity=100.0, dt=1.0)

    assert spark.angle > 0


def test_velocity_adjust_caps_the_vertical_component_at_terminal_velocity():
    spark = make_spark(angle=0.0, speed=1.0)

    spark.velocity_adjust(friction=1.0, force=1000.0, terminal_velocity=2.0, dt=1.0)

    # angle = atan2(min(force*dt, terminal_velocity), horizontal_component)
    assert spark.angle == pytest.approx(math.atan2(2.0, 1.0))


def test_draw_skips_rendering_when_not_alive(monkeypatch):
    spark = make_spark()
    spark.alive = False
    surface = pygame.Surface((50, 50))
    calls = []
    monkeypatch.setattr(pygame.draw, "polygon", lambda *a, **k: calls.append(a))

    spark.draw(surface)

    assert calls == []


def test_draw_renders_a_polygon_in_the_sparks_color_when_alive(monkeypatch):
    spark = make_spark(color=(255, 255, 255))
    surface = pygame.Surface((50, 50))
    calls = []
    monkeypatch.setattr(
        pygame.draw, "polygon", lambda surf, color, points: calls.append(color)
    )

    spark.draw(surface)

    assert calls == [(255, 255, 255)]
