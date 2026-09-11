import pygame
import pytest

import main


@pytest.fixture
def font():
    return pygame.font.Font(None, 16)


def test_starts_with_nothing_revealed_and_full_alpha(font):
    dialogue = main.IntroDialogue(font, text="Hi")

    assert dialogue.visible_char_count == 0
    assert dialogue.alpha == 255.0
    assert dialogue.is_fading_out is False


def test_bar_height_eases_towards_the_open_height_over_time(font):
    dialogue = main.IntroDialogue(font, text="Hi")

    for _ in range(5):
        dialogue.update(dt=16)

    assert 0 < dialogue.bar_height < main.DIALOGUE_BAR_OPEN_HEIGHT


def test_bar_height_converges_on_the_open_height_while_held_open(font):
    dialogue = main.IntroDialogue(font, text="Hi")

    # Stay comfortably inside the hold window (INTRO_HOLD_FRAMES) so the
    # bars haven't started easing closed again yet.
    for _ in range(100):
        dialogue.update(dt=16)

    assert dialogue.bar_height == pytest.approx(main.DIALOGUE_BAR_OPEN_HEIGHT, abs=0.5)
    assert dialogue.is_fading_out is False


def test_characters_reveal_one_at_a_time_as_time_passes(font):
    dialogue = main.IntroDialogue(font, text="Hi there")
    ms_per_char = 1000 / main.TEXT_REVEAL_SPEED

    dialogue.update(dt=ms_per_char)

    assert dialogue.visible_char_count == 1


def test_reveal_stops_once_the_full_text_is_shown(font):
    text = "Hi"
    dialogue = main.IntroDialogue(font, text=text)
    ms_per_char = 1000 / main.TEXT_REVEAL_SPEED

    for _ in range(len(text) + 5):
        dialogue.update(dt=ms_per_char)

    assert dialogue.visible_char_count == len(text)


def test_begins_fading_out_after_the_hold_period_elapses(font):
    dialogue = main.IntroDialogue(font, text="Hi")

    for _ in range(main.INTRO_HOLD_FRAMES + 1):
        dialogue.update(dt=16)

    assert dialogue.is_fading_out is True
    assert dialogue.target_bar_height == 0


def test_alpha_fades_to_zero_and_active_text_disappears(font):
    dialogue = main.IntroDialogue(font, text="Hi")

    for _ in range(main.INTRO_HOLD_FRAMES + 300):
        dialogue.update(dt=16)

    assert dialogue.alpha == 0.0


def test_draw_is_a_noop_before_any_characters_are_revealed(font, recording_surface):
    dialogue = main.IntroDialogue(font, text="Hi")
    surface = recording_surface((900, 900))

    dialogue.draw(surface)

    assert surface.blit_calls == []


def test_draw_renders_text_once_characters_are_revealed(font, recording_surface):
    dialogue = main.IntroDialogue(font, text="Hi")
    dialogue.update(dt=1000 / main.TEXT_REVEAL_SPEED)
    surface = recording_surface((900, 900))

    dialogue.draw(surface)

    # The settled portion of the text plus the newest "popping in"
    # character are each blit separately.
    assert len(surface.blit_calls) == 2
