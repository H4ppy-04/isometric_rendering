import pygame

from ui.button import Button


def test_initial_state_uses_unfocused_color_and_given_text():
    button = Button("Start", 100, 50)

    assert button.text == "Start"
    assert button.hovering is False
    assert button.color == button.font_color


def test_rect_is_centered_on_given_coordinates():
    button = Button("Start", 100, 50)

    assert button.rect.center == (100, 50)


def test_image_surface_matches_font_metrics_for_text():
    button = Button("Start", 0, 0)

    assert button.image.get_size() == button.font_16_pt.size("Start")


def test_is_a_sprite_and_joins_groups_passed_in():
    group = pygame.sprite.Group()
    button = Button("Start", 0, 0, group)

    assert isinstance(button, pygame.sprite.Sprite)
    assert button in group


def test_update_switches_to_hover_color_when_hovering():
    button = Button("Start", 0, 0)

    button.hovering = True
    button.update()

    assert button.color == button.hover_color


def test_update_reverts_to_default_color_when_not_hovering():
    button = Button("Start", 0, 0)
    button.hovering = True
    button.update()

    button.hovering = False
    button.update()

    assert button.color == button.font_color


def test_draw_blits_its_own_image_at_its_own_rect(recording_surface):
    button = Button("Start", 0, 0)
    surface = recording_surface((200, 200))

    button.draw(surface)

    assert surface.blit_calls == [(button.image, button.rect)]
