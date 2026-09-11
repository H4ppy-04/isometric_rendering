import main


def test_default_state_produces_no_offset():
    shake = main.ScreenShake()

    assert shake.update() == [0, 0]


def test_start_sets_timer_and_magnitude():
    shake = main.ScreenShake()

    shake.start(duration=10, magnitude=3)

    assert shake.timer == 10
    assert shake.magnitude == 3


def test_start_uses_default_magnitude_when_not_given():
    shake = main.ScreenShake()

    shake.start(duration=10)

    assert shake.magnitude == main.SCREEN_SHAKE_DEFAULT_MAGNITUDE


def test_update_counts_the_timer_down_by_one_per_call():
    shake = main.ScreenShake()
    shake.start(duration=3, magnitude=1)

    shake.update()
    assert shake.timer == 2

    shake.update()
    assert shake.timer == 1


def test_update_returns_offsets_within_magnitude_while_active(monkeypatch):
    shake = main.ScreenShake()
    shake.start(duration=5, magnitude=4)
    monkeypatch.setattr(main.random, "randint", lambda lo, hi: hi)

    offset = shake.update()

    assert offset == [4, 4]


def test_update_stops_producing_offsets_once_the_timer_runs_out():
    shake = main.ScreenShake()
    shake.start(duration=1, magnitude=5)

    first = shake.update()  # timer 1 -> 0, still produces an offset
    second = shake.update()  # timer already 0, no more shaking

    assert len(first) == 2
    assert second == [0, 0]
