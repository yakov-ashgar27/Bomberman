"""The tile map: indestructible walls, destructible bricks and empty floor."""
from __future__ import annotations

from enum import Enum


class Tile(Enum):
    EMPTY = 0
    WALL = 1    # indestructible
    BRICK = 2   # destroyed by explosions


class Grid:
    def __init__(self, width: int, height: int, fill: Tile = Tile.EMPTY):
        if width <= 0 or height <= 0:
            raise ValueError("grid dimensions must be positive")
        self.width = width
        self.height = height
        self._tiles = [[fill for _ in range(width)] for _ in range(height)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x: int, y: int) -> Tile:
        if not self.in_bounds(x, y):
            return Tile.WALL  # outside the map behaves like a wall
        return self._tiles[y][x]

    def set(self, x: int, y: int, tile: Tile) -> None:
        if not self.in_bounds(x, y):
            raise IndexError(f"({x}, {y}) is outside the grid")
        self._tiles[y][x] = tile

    def is_solid(self, x: int, y: int) -> bool:
        return self.get(x, y) in (Tile.WALL, Tile.BRICK)

    def destroy_brick(self, x: int, y: int) -> bool:
        """Turn a brick into floor. Returns True if a brick was destroyed."""
        if self.get(x, y) is Tile.BRICK:
            self.set(x, y, Tile.EMPTY)
            return True
        return False

    def count(self, tile: Tile) -> int:
        return sum(row.count(tile) for row in self._tiles)

    def copy(self) -> "Grid":
        clone = Grid(self.width, self.height)
        clone._tiles = [row[:] for row in self._tiles]
        return clone
