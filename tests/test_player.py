import pytest

import main


def test_default_position_and_speed():
    player = main.Player()

    assert tuple(player.pos) == (250, 250)
    assert player.speed == 0.8


def test_custom_position_and_speed():
    player = main.Player(pos=(10, 20), speed=2.0)

    assert tuple(player.pos) == (10, 20)
    assert player.speed == 2.0


def test_update_does_not_move_when_direction_is_zero():
    player = main.Player(pos=(0, 0))

    player.update()

    assert tuple(player.pos) == (0, 0)


def test_update_moves_by_speed_along_a_cardinal_direction():
    player = main.Player(pos=(0, 0), speed=3.0)
    player.direction.x = 1

    player.update()

    assert player.pos.x == pytest.approx(3.0)
    assert player.pos.y == pytest.approx(0.0)


def test_update_normalizes_diagonal_movement_so_speed_is_consistent():
    player = main.Player(pos=(0, 0), speed=2.0)
    player.direction.x = 1
    player.direction.y = 1

    player.update()

    # A normalized diagonal direction times speed should have magnitude
    # equal to speed, not speed * sqrt(2).
    assert player.pos.length() == pytest.approx(2.0)


def test_repeated_updates_accumulate_position():
    player = main.Player(pos=(0, 0), speed=1.0)
    player.direction.x = 1

    player.update()
    player.update()
    player.update()

    assert player.pos.x == pytest.approx(3.0)
