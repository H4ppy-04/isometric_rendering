import pygame

from ui.counter import Counter


def test_starts_at_zero():
    counter = Counter(0, 0)

    assert counter.counter == 0


def test_rect_is_centered_on_given_coordinates():
    counter = Counter(50, 75)

    assert counter.rect.center == (50, 75)


def test_increment_increases_counter_by_one():
    counter = Counter(0, 0)

    counter.increment()
    assert counter.counter == 1

    counter.increment()
    assert counter.counter == 2


def test_decrement_decreases_counter_by_one():
    counter = Counter(0, 0)
    counter.increment()
    counter.increment()

    counter.decrement()

    assert counter.counter == 1


def test_decrement_can_go_negative():
    counter = Counter(0, 0)

    counter.decrement()

    assert counter.counter == -1


def test_reset_returns_counter_to_zero():
    counter = Counter(0, 0)
    counter.increment()
    counter.increment()
    counter.increment()

    counter.reset()

    assert counter.counter == 0


def test_render_resizes_image_to_match_new_text():
    counter = Counter(0, 0)
    small_size = counter.image.get_size()

    for _ in range(15):
        counter.increment()

    assert counter.image.get_size() != small_size
    assert counter.image.get_size() == counter.font_32_pt.size(str(counter.counter))


def test_draw_blits_its_own_image_at_its_own_rect(recording_surface):
    counter = Counter(0, 0)
    surface = recording_surface((100, 100))

    counter.draw(surface)

    assert surface.blit_calls == [(counter.image, counter.rect)]
