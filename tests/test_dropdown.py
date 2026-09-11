import pygame

from ui.dropdown import DropdownMenu


def test_starts_collapsed_on_the_first_value():
    dropdown = DropdownMenu(0, 0)

    assert dropdown.dropped_down is False
    assert dropdown.index == 0
    assert dropdown.values[dropdown.index] == "Foo"


def test_rect_is_centered_on_given_coordinates():
    dropdown = DropdownMenu(100, 100)

    assert dropdown.rect.center == (100, 100)


def test_collapsed_draw_renders_a_single_row():
    dropdown = DropdownMenu(0, 0)
    surface = pygame.Surface((300, 300))

    dropdown.draw(surface)

    assert dropdown.image.get_size() == dropdown.text_size


def test_expanded_draw_renders_one_row_per_value():
    dropdown = DropdownMenu(0, 0)
    dropdown.dropped_down = True
    surface = pygame.Surface((300, 300))

    dropdown.draw(surface)

    expected_height = dropdown.text_size[1] * len(dropdown.values)
    assert dropdown.image.get_width() == dropdown.text_size[0]
    assert dropdown.image.get_height() == expected_height


def test_draw_keeps_rect_size_in_sync_with_image():
    dropdown = DropdownMenu(0, 0)
    surface = pygame.Surface((300, 300))

    dropdown.dropped_down = True
    dropdown.draw(surface)
    assert dropdown.rect.size == dropdown.image.get_size()

    dropdown.dropped_down = False
    dropdown.draw(surface)
    assert dropdown.rect.size == dropdown.image.get_size()


def test_collapsing_after_expanding_shrinks_image_back_down():
    dropdown = DropdownMenu(0, 0)
    surface = pygame.Surface((300, 300))

    dropdown.dropped_down = True
    dropdown.draw(surface)
    expanded_height = dropdown.image.get_height()

    dropdown.dropped_down = False
    dropdown.draw(surface)

    assert dropdown.image.get_height() < expanded_height
    assert dropdown.image.get_height() == dropdown.text_size[1]


def test_draw_outlines_its_rect(monkeypatch):
    dropdown = DropdownMenu(0, 0)
    surface = pygame.Surface((300, 300))
    calls = []
    monkeypatch.setattr(
        pygame.draw, "rect", lambda surf, color, rect, width: calls.append((color, width))
    )

    dropdown.draw(surface)

    assert calls == [((255, 0, 0), 1)]
