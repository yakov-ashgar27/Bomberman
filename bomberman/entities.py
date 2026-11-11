"""Things that live on the grid: the player, enemies, bombs and power-ups."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from . import config


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self) -> int:
        return self.value[0]

    @property
    def dy(self) -> int:
        return self.value[1]

    @property
    def opposite(self) -> "Direction":
        return {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }[self]


class PowerUpType(Enum):
    BOMB_UP = "bomb_up"    # +1 bomb at a time
    FIRE_UP = "fire_up"    # +1 explosion range
    SPEED_UP = "speed_up"  # faster movement


class Mover:
    """Tile-based movement with a cooldown. The logical position jumps one
    tile at a time; render_pos() interpolates so movement looks smooth."""

    def __init__(self, x: int, y: int, speed: float):
        self.x = x
        self.y = y
        self.prev_x = x
        self.prev_y = y
        self.speed = speed
        self.cooldown = 0.0
        self.facing = Direction.DOWN

    @property
    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)

    def can_move(self) -> bool:
        return self.cooldown <= 0.0

    def move(self, direction: Direction) -> None:
        self.prev_x, self.prev_y = self.x, self.y
        self.x += direction.dx
        self.y += direction.dy
        self.facing = direction
        self.cooldown = 1.0 / self.speed

    def tick(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)

    def place_at(self, x: int, y: int) -> None:
        self.x = self.prev_x = x
        self.y = self.prev_y = y
        self.cooldown = 0.0
        self.facing = Direction.DOWN

    def render_pos(self) -> tuple[float, float]:
        if self.cooldown <= 0.0:
            return (float(self.x), float(self.y))
        t = min(1.0, max(0.0, 1.0 - self.cooldown * self.speed))
        return (
            self.prev_x + (self.x - self.prev_x) * t,
            self.prev_y + (self.y - self.prev_y) * t,
        )


class Player(Mover):
    def __init__(self, x: int = 0, y: int = 0):
        super().__init__(x, y, config.PLAYER_BASE_SPEED)
        self.lives = config.PLAYER_START_LIVES
        self.max_bombs = config.PLAYER_START_BOMBS
        self.fire_range = config.PLAYER_START_FIRE
        self.alive = True

    def apply_powerup(self, kind: PowerUpType) -> None:
        if kind is PowerUpType.BOMB_UP:
            self.max_bombs = min(config.PLAYER_MAX_BOMBS, self.max_bombs + 1)
        elif kind is PowerUpType.FIRE_UP:
            self.fire_range = min(config.PLAYER_MAX_FIRE, self.fire_range + 1)
        elif kind is PowerUpType.SPEED_UP:
            self.speed = min(config.PLAYER_MAX_SPEED, self.speed + config.PLAYER_SPEED_STEP)


class Enemy(Mover):
    def __init__(self, kind: str, x: int, y: int):
        if kind not in config.ENEMY_STATS:
            raise ValueError(f"unknown enemy kind: {kind}")
        stats = config.ENEMY_STATS[kind]
        super().__init__(x, y, stats["speed"])
        self.kind = kind
        self.points = stats["points"]
        self.chase_range = stats["chase_range"]
        self.alive = True
        self.direction: Direction | None = None


@dataclass(eq=False)  # identity equality: two bombs are never "the same"
class Bomb:
    x: int
    y: int
    fire_range: int
    timer: float = config.BOMB_FUSE

    @property
    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)
