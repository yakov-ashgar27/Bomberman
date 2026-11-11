"""Level files: plain-text maps, one character per tile.

    #  indestructible wall        .  empty floor
    B  brick                      P  player start
    E  balloon enemy              O  oneal enemy (chases the player)
    X  brick hiding the exit door
    1  brick hiding BOMB_UP       2  brick hiding FIRE_UP     3  brick hiding SPEED_UP

Lines starting with ';' are comments. The map must be rectangular, fully
enclosed by walls, and contain exactly one P, exactly one X and at least one
enemy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .entities import PowerUpType
from .grid import Grid, Tile


class LevelFormatError(ValueError):
    """Raised when a level file breaks the format rules above."""


ENEMY_CHARS = {"E": "balloon", "O": "oneal"}
POWERUP_CHARS = {"1": PowerUpType.BOMB_UP, "2": PowerUpType.FIRE_UP, "3": PowerUpType.SPEED_UP}
VALID_CHARS = set("#.BPX") | set(ENEMY_CHARS) | set(POWERUP_CHARS)


@dataclass
class LevelData:
    name: str
    grid: Grid
    player_start: tuple[int, int]
    exit_pos: tuple[int, int]
    enemies: list[tuple[str, tuple[int, int]]] = field(default_factory=list)
    powerups: dict[tuple[int, int], PowerUpType] = field(default_factory=dict)


def parse_level(text: str, name: str = "level") -> LevelData:
    rows = [line.rstrip("\r\n") for line in text.splitlines()]
    rows = [r for r in rows if r.strip() and not r.lstrip().startswith(";")]
    if not rows:
        raise LevelFormatError("level is empty")

    width = len(rows[0])
    if any(len(r) != width for r in rows):
        raise LevelFormatError("level rows must all have the same length")
    height = len(rows)
    if width < 3 or height < 3:
        raise LevelFormatError("level must be at least 3x3")

    grid = Grid(width, height)
    player_start = None
    exit_pos = None
    enemies: list[tuple[str, tuple[int, int]]] = []
    powerups: dict[tuple[int, int], PowerUpType] = {}

    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch not in VALID_CHARS:
                raise LevelFormatError(f"unknown character {ch!r} at ({x}, {y})")
            on_border = x in (0, width - 1) or y in (0, height - 1)
            if on_border and ch != "#":
                raise LevelFormatError(f"border tile ({x}, {y}) must be a wall")

            if ch == "#":
                grid.set(x, y, Tile.WALL)
            elif ch == "B":
                grid.set(x, y, Tile.BRICK)
            elif ch == "P":
                if player_start is not None:
                    raise LevelFormatError("level has more than one player start")
                player_start = (x, y)
            elif ch == "X":
                if exit_pos is not None:
                    raise LevelFormatError("level has more than one exit")
                exit_pos = (x, y)
                grid.set(x, y, Tile.BRICK)
            elif ch in ENEMY_CHARS:
                enemies.append((ENEMY_CHARS[ch], (x, y)))
            elif ch in POWERUP_CHARS:
                powerups[(x, y)] = POWERUP_CHARS[ch]
                grid.set(x, y, Tile.BRICK)

    if player_start is None:
        raise LevelFormatError("level has no player start (P)")
    if exit_pos is None:
        raise LevelFormatError("level has no exit (X)")
    if not enemies:
        raise LevelFormatError("level has no enemies")

    return LevelData(name, grid, player_start, exit_pos, enemies, powerups)


def load_level_file(path: str | Path) -> LevelData:
    path = Path(path)
    return parse_level(path.read_text(encoding="utf-8"), name=path.stem)


def load_level_texts(directory: str | Path) -> list[str]:
    """Read every level*.txt in a folder, in name order."""
    files = sorted(Path(directory).glob("level*.txt"))
    if not files:
        raise FileNotFoundError(f"no level files found in {directory}")
    return [f.read_text(encoding="utf-8") for f in files]
