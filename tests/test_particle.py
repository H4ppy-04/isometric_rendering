import pygame
import pytest

import main


def test_spawns_at_the_given_position():
    particle = main.Particle((5, 7))

    assert particle.pos == [5, 7]


def test_radius_is_within_the_configured_range():
    particle = main.Particle((0, 0))

    lo, hi = main.PARTICLE_RADIUS_RANGE
    assert lo <= particle.radius <= hi


def test_alive_is_true_for_a_freshly_spawned_particle():
    particle = main.Particle((0, 0))

    assert particle.alive is True


def test_alive_is_false_once_radius_drops_to_zero_or_below():
    particle = main.Particle((0, 0))
    particle.radius = 0

    assert particle.alive is False


def test_update_moves_position_by_current_velocity():
    particle = main.Particle((0, 0))
    particle.velocity = [1.0, 2.0]

    particle.update()

    assert particle.pos == [1.0, 2.0]


def test_update_applies_gravity_to_vertical_velocity():
    particle = main.Particle((0, 0))
    particle.velocity = [0.0, 0.0]

    particle.update()

    assert particle.velocity[1] == pytest.approx(main.PARTICLE_GRAVITY)


def test_update_shrinks_the_radius_over_time():
    particle = main.Particle((0, 0))
    starting_radius = particle.radius

    particle.update()

    assert particle.radius == pytest.approx(starting_radius - main.PARTICLE_SHRINK_RATE)


def test_particle_eventually_dies_after_enough_updates():
    particle = main.Particle((0, 0))
    particle.radius = main.PARTICLE_SHRINK_RATE * 2

    particle.update()
    assert particle.alive is True

    particle.update()
    particle.update()
    assert particle.alive is False


def test_draw_does_not_raise(recording_surface):
    particle = main.Particle((50, 50))
    surface = recording_surface((100, 100))

    particle.draw(surface)

    # The particle itself plus its additive glow surface should both be
    # blit onto the target surface.
    assert len(surface.blit_calls) == 1
