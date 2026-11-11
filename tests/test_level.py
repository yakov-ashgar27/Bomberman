"""Level loading and grid (requirements FR-01, FR-02)."""
import pytest

from bomberman.entities import PowerUpType
from bomberman.grid import Grid, Tile
from bomberman.level import LevelFormatError, load_level_texts, parse_level, load_level_file
from tests.helpers import OPEN_LEVEL


def test_parse_valid_level():
    data = parse_level(OPEN_LEVEL)
    assert (data.grid.width, data.grid.height) == (9, 7)
    assert data.player_start == (1, 1)
    assert data.exit_pos == (5, 1)
    assert data.grid.get(5, 1) is Tile.BRICK          # exit is hidden under a brick
    assert data.enemies == [("balloon", (7, 5))]


def test_hidden_powerups_are_bricks():
    text = OPEN_LEVEL.replace("#.......#", "#.1.2.3.#", 1)
    data = parse_level(text)
    assert data.powerups == {(2, 3): PowerUpType.BOMB_UP, (4, 3): PowerUpType.FIRE_UP,
                             (6, 3): PowerUpType.SPEED_UP}
    assert all(data.grid.get(*pos) is Tile.BRICK for pos in data.powerups)


def test_comments_are_ignored():
    assert parse_level("; my level\n" + OPEN_LEVEL).player_start == (1, 1)


@pytest.mark.parametrize("bad, message", [
    ("", "empty"),
    (OPEN_LEVEL.replace("#P...X..#", "#P...X.#"), "same length"),
    (OPEN_LEVEL.replace("P", "."), "player start"),
    (OPEN_LEVEL.replace("X", "."), "exit"),
    (OPEN_LEVEL.replace("E", "."), "enemies"),
    (OPEN_LEVEL.replace("#P", ".P"), "border"),
    (OPEN_LEVEL.replace("#.......#", "#...?...#"), "unknown character"),
    (OPEN_LEVEL.replace("#.......#", "#...P...#"), "more than one player"),
])
def test_invalid_levels_are_rejected(bad, message):
    with pytest.raises(LevelFormatError, match=message):
        parse_level(bad)


def test_shipped_levels_are_valid():
    for text in load_level_texts("levels"):
        data = parse_level(text)
        assert data.grid.get(*data.player_start) is Tile.EMPTY
        assert len(data.enemies) >= 1


def test_shipped_level_file_loads():
    assert load_level_file("levels/level1.txt").name == "level1"


def test_grid_out_of_bounds_is_wall():
    g = Grid(3, 3)
    assert g.get(-1, 0) is Tile.WALL and g.is_solid(5, 5)
    with pytest.raises(IndexError):
        g.set(3, 0, Tile.WALL)


def test_grid_destroy_brick_only_affects_bricks():
    g = Grid(3, 3)
    g.set(1, 1, Tile.BRICK)
    g.set(2, 2, Tile.WALL)
    assert g.destroy_brick(1, 1) and g.get(1, 1) is Tile.EMPTY
    assert not g.destroy_brick(2, 2) and g.get(2, 2) is Tile.WALL


def test_grid_copy_is_independent():
    g = Grid(3, 3)
    clone = g.copy()
    clone.set(0, 0, Tile.WALL)
    assert g.get(0, 0) is Tile.EMPTY
