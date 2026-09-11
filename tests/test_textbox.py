import pygame

from ui.textbox import TextBox


def test_starts_inactive_and_empty():
    box = TextBox()

    assert box.active is False
    assert box.value == ""


def test_append_does_nothing_while_inactive():
    box = TextBox()

    box.append("a")

    assert box.value == ""


def test_append_adds_characters_while_active():
    box = TextBox()
    box.active = True

    box.append("h")
    box.append("i")

    assert box.value == "hi"


def test_delete_removes_last_character_while_active():
    box = TextBox()
    box.active = True
    box.append("abc")

    box.delete()

    assert box.value == "ab"


def test_delete_on_empty_value_is_a_noop():
    box = TextBox()
    box.active = True

    box.delete()

    assert box.value == ""


def test_delete_does_nothing_while_inactive():
    box = TextBox()
    box.active = True
    box.append("a")
    box.active = False

    box.delete()

    assert box.value == "a"


def test_wipe_clears_value_while_active():
    box = TextBox()
    box.active = True
    box.append("hello")

    box.wipe()

    assert box.value == ""


def test_wipe_does_nothing_while_inactive():
    box = TextBox()
    box.active = True
    box.append("hello")
    box.active = False

    box.wipe()

    assert box.value == "hello"


def test_render_resizes_image_and_rect_to_fit_value():
    box = TextBox()
    box.active = True

    box.append("a longer string of text")

    assert box.image.get_size() == box.font.size(box.value)
    assert box.rect.size == box.image.get_size()


def test_draw_outline_is_green_when_active(monkeypatch):
    box = TextBox()
    box.active = True
    surface = pygame.Surface((300, 300))
    calls = []
    monkeypatch.setattr(
        pygame.draw, "rect", lambda surf, color, rect, width: calls.append(color)
    )

    box.draw(surface)

    assert calls == [(0, 200, 0)]


def test_draw_outline_is_red_when_inactive(monkeypatch):
    box = TextBox()
    box.active = False
    surface = pygame.Surface((300, 300))
    calls = []
    monkeypatch.setattr(
        pygame.draw, "rect", lambda surf, color, rect, width: calls.append(color)
    )

    box.draw(surface)

    assert calls == [(200, 0, 0)]


def test_draw_outline_rect_is_inset_around_the_textbox_rect(monkeypatch):
    box = TextBox()
    surface = pygame.Surface((300, 300))
    captured = {}
    monkeypatch.setattr(
        pygame.draw,
        "rect",
        lambda surf, color, rect, width: captured.update(rect=rect),
    )

    box.draw(surface)

    outline = captured["rect"]
    assert outline.x == box.rect.x - 2
    assert outline.y == box.rect.y - 2
    assert outline.w == box.rect.w + 4
    assert outline.h == box.rect.h + 4
