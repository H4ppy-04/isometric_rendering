import pygame
import pytest

import main


@pytest.fixture
def splasher(monkeypatch):
    dummy_logo = pygame.Surface((20, 20), pygame.SRCALPHA)
    monkeypatch.setattr(main, "load_sprite", lambda *a, **k: dummy_logo.copy())
    return main.IntroSplasher()


def test_starts_active_and_invisible(splasher):
    assert splasher.active is True
    assert splasher.alpha == 0.0
    assert splasher.is_fading_in is True


def test_frames_elapsed_increments_on_every_update(splasher):
    splasher.update()
    splasher.update()

    assert splasher.frames_elapsed == 2


def test_fades_in_to_full_opacity(splasher):
    for _ in range(60):
        splasher.update()

    assert splasher.alpha == pytest.approx(255.0)


def test_stays_active_throughout_the_fade_in(splasher):
    for _ in range(60):
        splasher.update()

    assert splasher.active is True


def test_becomes_inactive_after_the_full_display_window_elapses(splasher):
    # Comfortably past the >300-frame threshold that deactivates the splash.
    for _ in range(400):
        splasher.update()

    assert splasher.active is False


def test_draw_fills_the_screen_black_before_placing_the_logo(splasher):
    display = pygame.display.get_surface()

    splasher.draw(display)

    # A corner far from the centered logo should be pure black.
    assert display.get_at((0, 0))[:3] == main.BLACK


def test_draw_does_not_raise_once_the_logo_has_faded_in(splasher):
    for _ in range(60):
        splasher.update()
    display = pygame.display.get_surface()

    splasher.draw(display)  # should complete without error
