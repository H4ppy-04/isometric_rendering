"""
Shared pytest fixtures.

Two problems have to be solved before any of this pygame code can run in
CI/headless environments:

1. There's no real display. We force SDL's "dummy" video/audio drivers so
   pygame.display.set_mode() and friends work without a windowing system.
2. Every widget loads a font from a relative, repo-specific path
   (e.g. "assets/fonts/Tengoku.ttf" or just "Tengoku.ttf") that won't exist
   wherever tests run. We patch pygame.font.Font so any path resolves to
   pygame's bundled default font instead of touching the filesystem. This
   keeps tests focused on behavior (positions, state, sizes) rather than on
   font-rendering fidelity, and means tests don't break if asset paths move.
"""
import os

import pygame
import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


@pytest.fixture(scope="session", autouse=True)
def _pygame_session():
    pygame.init()
    # A display surface is required for things like pygame.display.get_surface()
    # (used by IntroSplasher.draw) and for convert()/convert_alpha() to work.
    pygame.display.set_mode((900, 900))
    yield
    pygame.quit()


@pytest.fixture(autouse=True)
def _patch_font(monkeypatch):
    real_font_cls = pygame.font.Font

    def fake_font(file=None, size=16, **kwargs):
        return real_font_cls(None, size)

    monkeypatch.setattr(pygame.font, "Font", fake_font)
    yield


class RecordingSurface(pygame.Surface):
    """
    A pygame.Surface that records every blit() call it receives.

    pygame.Surface is a C extension type, so its methods can't be patched
    with monkeypatch.setattr on an instance or the class directly (its
    attributes are read-only). Subclassing and overriding blit() is the
    supported way to observe blit calls while still behaving like a real
    surface for anything else (get_at, get_size, etc.).
    """

    def __init__(self, size):
        super().__init__(size)
        self.blit_calls = []

    def blit(self, source, dest, *args, **kwargs):
        self.blit_calls.append((source, dest))
        return super().blit(source, dest, *args, **kwargs)


@pytest.fixture
def recording_surface():
    return RecordingSurface
