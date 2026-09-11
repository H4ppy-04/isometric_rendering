import pygame
import pytest

import main


def test_load_map_grid_parses_digit_rows_into_ints(tmp_path, monkeypatch):
    maps_dir = tmp_path / "data" / "maps"
    maps_dir.mkdir(parents=True)
    (maps_dir / "test_map.txt").write_text("120\n201")
    monkeypatch.chdir(tmp_path)

    grid = main.load_map_grid("test_map.txt")

    assert grid == [[1, 2, 0], [2, 0, 1]]


def test_load_map_grid_raises_on_non_digit_characters(tmp_path, monkeypatch):
    maps_dir = tmp_path / "data" / "maps"
    maps_dir.mkdir(parents=True)
    (maps_dir / "bad_map.txt").write_text("1x0")
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError):
        main.load_map_grid("bad_map.txt")


def test_make_glow_surface_is_sized_to_double_the_radius():
    surface = main.make_glow_surface(10, (20, 20, 20))

    assert surface.get_size() == (20, 20)


def test_make_glow_surface_clamps_radius_to_at_least_one():
    # radius < 1 (including 0 or negative) should still produce a usable,
    # non-empty surface rather than crashing on pygame.Surface((0, 0)).
    surface = main.make_glow_surface(0, (20, 20, 20))

    assert surface.get_size() == (2, 2)


def test_make_glow_surface_sets_black_as_the_colorkey():
    surface = main.make_glow_surface(5, (20, 20, 20))

    assert surface.get_colorkey()[:3] == main.BLACK


def test_build_background_surface_matches_configured_dimensions():
    surface = main.build_background_surface()

    assert surface.get_size() == (main.SCREEN_WIDTH, main.BACKGROUND_SURFACE_HEIGHT)


def test_build_world_surface_matches_configured_size_and_colorkey():
    grass = pygame.Surface((8, 8))
    teleporter = pygame.Surface((8, 8))
    grid = [[0, 1], [2, 0]]

    surface = main.build_world_surface(grid, grass, teleporter)

    assert surface.get_size() == (main.WORLD_SURFACE_SIZE, main.WORLD_SURFACE_SIZE)
    assert surface.get_colorkey()[:3] == main.BLACK


def test_build_world_surface_places_grass_and_teleporter_tiles_by_type():
    grass = pygame.Surface((8, 8))
    grass.fill((10, 20, 30))
    teleporter = pygame.Surface((8, 8))
    teleporter.fill((40, 50, 60))

    # x=0,y=0 -> tile 0 (nothing); x=1,y=0 -> tile 1 (grass);
    # x=0,y=1 -> tile 2 (teleporter); x=1,y=1 -> tile 0 (nothing).
    surface = main.build_world_surface([[0, 1], [2, 0]], grass, teleporter)

    grass_tile_pos = (150 + 1 * 10 - 0 * 10, 100 + 1 * 5 + 0 * 5)
    teleporter_tile_pos = (150 + 0 * 10 - 1 * 10, 100 + 0 * 5 + 1 * 5)

    assert surface.get_at(grass_tile_pos)[:3] == (10, 20, 30)
    assert surface.get_at(teleporter_tile_pos)[:3] == (40, 50, 60)


def test_build_world_surface_leaves_unknown_tile_values_untouched():
    grass = pygame.Surface((8, 8))
    grass.fill((10, 20, 30))
    teleporter = pygame.Surface((8, 8))
    teleporter.fill((40, 50, 60))

    # Tile value 9 doesn't match either branch, so nothing should be drawn
    # at its position and the surface should keep its default black fill.
    surface = main.build_world_surface([[9]], grass, teleporter)

    tile_pos = (150, 100)
    assert surface.get_at(tile_pos)[:3] == main.BLACK
