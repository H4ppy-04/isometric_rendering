import pygame
import pytest

import main


@pytest.fixture
def game(monkeypatch):
    dummy_sprite = pygame.Surface((8, 8))
    monkeypatch.setattr(main, "load_sprite", lambda *a, **k: dummy_sprite.copy())
    monkeypatch.setattr(main, "load_map_grid", lambda *a, **k: [[0, 1], [1, 0]])
    return main.Game()


def test_starts_running_with_a_fresh_score_and_no_effects_yet(game):
    assert game.running is True
    assert game.score == 0
    assert game.particles == []
    assert game.sparks == []


def test_splash_screen_is_active_on_startup(game):
    assert game.splash.active is True


def test_arrow_keys_set_player_direction(game):
    game._handle_keydown(pygame.K_UP)
    assert game.player.direction.y == -1

    game._handle_keydown(pygame.K_DOWN)
    assert game.player.direction.y == 1

    game._handle_keydown(pygame.K_LEFT)
    assert game.player.direction.x == -1

    game._handle_keydown(pygame.K_RIGHT)
    assert game.player.direction.x == 1


def test_releasing_a_vertical_key_zeroes_vertical_direction(game):
    game.player.direction.y = -1

    game._handle_keyup(pygame.K_UP)

    assert game.player.direction.y == 0


def test_releasing_a_horizontal_key_zeroes_horizontal_direction(game):
    game.player.direction.x = 1

    game._handle_keyup(pygame.K_RIGHT)

    assert game.player.direction.x == 0


def test_escape_key_stops_the_game_loop(game):
    game._handle_keydown(pygame.K_ESCAPE)

    assert game.running is False


def test_space_key_triggers_a_screen_shake(game):
    game.screen_shake.timer = 0

    game._handle_keydown(pygame.K_SPACE)

    assert game.screen_shake.timer == 5


def test_any_keydown_dismisses_the_splash_screen(game):
    assert game.splash.active is True

    game._handle_keydown(pygame.K_a)

    assert game.splash.active is False


def test_make_spark_produces_a_spark_with_speed_in_the_configured_range():
    spark = main.Game._make_spark([1.0, 2.0])

    assert isinstance(spark, main.Spark)
    lo, hi = main.SPARK_SPEED_RANGE
    assert lo <= spark.speed <= hi
    assert spark.location == [1.0, 2.0]


def test_reset_zeroes_out_scroll_shake_and_world_bob_state(game):
    game.bg_scroll = 42.0
    game.render_offset = [3, 3]
    game.world_bob_phase = 1.5
    game.world_offset_y = 7

    game.reset()

    assert game.bg_scroll == 0.0
    assert game.render_offset == [0, 0]
    assert game.world_bob_phase == 0.0
    assert game.world_offset_y == 0


def test_reset_replaces_the_dialogue_with_a_fresh_one(game):
    game.dialogue.visible_char_count = 5

    game.reset()

    assert game.dialogue.visible_char_count == 0


def test_update_is_skipped_while_the_splash_screen_is_showing(game):
    game.splash.active = True

    game._update()

    assert game.particles == []


def test_update_spawns_a_trailing_particle_once_the_splash_is_dismissed(game):
    game.splash.active = False

    game._update()

    assert len(game.particles) == 1


def test_update_removes_particles_once_they_die(game):
    game.splash.active = False
    dead_particle = main.Particle((0, 0))
    dead_particle.radius = 0  # already dead
    game.particles = [dead_particle]

    game._update()

    # The dead particle should be gone; only the newly spawned one remains.
    assert dead_particle not in game.particles


def test_update_adds_a_spark_while_the_mouse_is_held_down(game):
    game.splash.active = False
    game.mouse_spark_active = True
    game.mouse_pos = (10, 10)

    game._update()

    assert len(game.sparks) == 1


def test_update_does_not_add_a_spark_when_the_mouse_is_not_held(game):
    game.splash.active = False
    game.mouse_spark_active = False

    game._update()

    assert game.sparks == []


def test_quit_event_stops_the_game_loop(game, monkeypatch):
    monkeypatch.setattr(
        pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)]
    )

    game._handle_events()

    assert game.running is False


def test_clicking_the_reset_button_calls_reset(game, monkeypatch):
    # Note: the click handler checks the *last known* mouse position
    # (updated on MOUSEMOTION), not the click event's own coordinates.
    game.splash.active = False
    game.mouse_pos = game.reset_button.rect.center
    calls = []
    monkeypatch.setattr(game, "reset", lambda: calls.append(True))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=game.mouse_pos, button=1)
    monkeypatch.setattr(pygame.event, "get", lambda: [event])

    game._handle_events()

    assert calls == [True]


def test_clicking_elsewhere_does_not_call_reset(game, monkeypatch):
    game.splash.active = False
    far_away = (game.reset_button.rect.centerx + 500, game.reset_button.rect.centery + 500)
    game.mouse_pos = far_away
    calls = []
    monkeypatch.setattr(game, "reset", lambda: calls.append(True))
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=far_away, button=1)
    monkeypatch.setattr(pygame.event, "get", lambda: [event])

    game._handle_events()

    assert calls == []


def test_draw_does_not_raise_before_the_splash_is_dismissed(game):
    game._draw()


def test_draw_does_not_raise_during_normal_gameplay(game):
    game.splash.active = False
    game._update()

    game._draw()
