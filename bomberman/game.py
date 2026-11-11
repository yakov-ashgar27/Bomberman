"""Core game model. Pure Python - no pygame - so every rule can be unit-tested.

The UI layer calls  update(dt, actions)  once per frame and reads the public
attributes to draw the screen.
"""
from __future__ import annotations

import math
import random
from enum import Enum, auto

from . import ai, config
from .entities import Bomb, Direction, Enemy, Player, PowerUpType
from .grid import Grid, Tile
from .level import LevelData, parse_level


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    PLAYER_DIED = auto()
    LEVEL_COMPLETE = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class Action(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    BOMB = auto()


ACTION_TO_DIRECTION = {
    Action.UP: Direction.UP,
    Action.DOWN: Direction.DOWN,
    Action.LEFT: Direction.LEFT,
    Action.RIGHT: Direction.RIGHT,
}


class Game:
    def __init__(self, level_texts: list[str], rng: random.Random | None = None):
        if not level_texts:
            raise ValueError("at least one level is required")
        self.levels: list[LevelData] = [
            parse_level(text, name=f"level{i + 1}") for i, text in enumerate(level_texts)
        ]
        self.rng = rng or random.Random()
        self.state = GameState.MENU
        self.score = 0
        self.level_index = 0
        self.player = Player()
        self.events: list[str] = []  # things that happened this frame (for sound / UI)
        self._reset_level_objects()

    # ------------------------------------------------------------------ setup
    def _reset_level_objects(self) -> None:
        self.grid: Grid = self.levels[0].grid.copy()
        self.enemies: list[Enemy] = []
        self.bombs: list[Bomb] = []
        self.flames: dict[tuple[int, int], float] = {}
        self.powerups: dict[tuple[int, int], PowerUpType] = {}
        self.hidden_powerups: dict[tuple[int, int], PowerUpType] = {}
        self.exit_pos: tuple[int, int] = self.levels[0].exit_pos
        self.exit_revealed = False
        self.time_left = config.LEVEL_TIME
        self.state_timer = 0.0

    def start_new_game(self) -> None:
        self.score = 0
        self.level_index = 0
        self.player = Player()
        self._load_level(0)
        self.state = GameState.PLAYING

    def _load_level(self, index: int) -> None:
        data = self.levels[index]
        self.level_index = index
        self._reset_level_objects()
        self.grid = data.grid.copy()
        self.enemies = [Enemy(kind, x, y) for kind, (x, y) in data.enemies]
        self.hidden_powerups = dict(data.powerups)
        self.exit_pos = data.exit_pos
        self.player.place_at(*data.player_start)
        self.player.alive = True

    # -------------------------------------------------------------- queries
    @property
    def level_number(self) -> int:
        return self.level_index + 1

    @property
    def level_count(self) -> int:
        return len(self.levels)

    @property
    def enemies_remaining(self) -> int:
        return sum(1 for e in self.enemies if e.alive)

    @property
    def exit_open(self) -> bool:
        return self.exit_revealed and self.enemies_remaining == 0

    def bomb_at(self, x: int, y: int) -> Bomb | None:
        for bomb in self.bombs:
            if bomb.x == x and bomb.y == y:
                return bomb
        return None

    def is_walkable(self, x: int, y: int) -> bool:
        return not self.grid.is_solid(x, y) and self.bomb_at(x, y) is None

    # -------------------------------------------------------------- control
    def toggle_pause(self) -> None:
        if self.state is GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state is GameState.PAUSED:
            self.state = GameState.PLAYING

    def update(self, dt: float, actions: set[Action] | frozenset[Action] = frozenset()) -> None:
        self.events = []
        dt = min(dt, config.MAX_FRAME_DT)
        if self.state is GameState.PLAYING:
            self._update_playing(dt, actions)
        elif self.state is GameState.PLAYER_DIED:
            self._update_flames(dt)
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._after_death()
        elif self.state is GameState.LEVEL_COMPLETE:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._advance_level()

    # ------------------------------------------------------------ main step
    def _update_playing(self, dt: float, actions) -> None:
        self.time_left = max(0.0, self.time_left - dt)
        if self.time_left <= 0:
            self._kill_player()
            return
        self._update_player(dt, actions)
        self._update_bombs(dt)
        self._update_flames(dt)
        self._update_enemies(dt)
        self._check_collisions()
        if self.state is GameState.PLAYING:
            self._check_exit()

    def _update_player(self, dt: float, actions) -> None:
        p = self.player
        p.tick(dt)
        if Action.BOMB in actions:
            self.place_bomb()
        if not p.can_move():
            return
        for action in (Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT):
            if action in actions:
                direction = ACTION_TO_DIRECTION[action]
                p.facing = direction
                if self.is_walkable(p.x + direction.dx, p.y + direction.dy):
                    p.move(direction)
                    self._collect_powerup()
                break

    def _collect_powerup(self) -> None:
        kind = self.powerups.pop(self.player.pos, None)
        if kind is not None:
            self.player.apply_powerup(kind)
            self.score += config.SCORE_POWERUP
            self.events.append("powerup")

    def place_bomb(self) -> bool:
        p = self.player
        if not p.alive or self.bomb_at(p.x, p.y) is not None:
            return False
        if len(self.bombs) >= p.max_bombs:
            return False
        self.bombs.append(Bomb(p.x, p.y, p.fire_range))
        self.events.append("bomb_placed")
        return True

    # --------------------------------------------------------- explosions
    def _update_bombs(self, dt: float) -> None:
        for bomb in self.bombs:
            bomb.timer -= dt
        due = [b for b in self.bombs if b.timer <= 0]
        if due:
            self.detonate(due)

    def detonate(self, bombs: list[Bomb]) -> None:
        """Explode bombs, including any chain reaction they trigger."""
        queue = list(bombs)
        done: list[Bomb] = []
        flame_tiles: set[tuple[int, int]] = set()
        bricks: set[tuple[int, int]] = set()

        while queue:
            bomb = queue.pop()
            if bomb in done:
                continue
            done.append(bomb)
            flame_tiles.add(bomb.pos)
            for d in Direction:
                for i in range(1, bomb.fire_range + 1):
                    x, y = bomb.x + d.dx * i, bomb.y + d.dy * i
                    tile = self.grid.get(x, y)
                    if tile is Tile.WALL:
                        break
                    flame_tiles.add((x, y))
                    if tile is Tile.BRICK:
                        bricks.add((x, y))
                        break
                    other = self.bomb_at(x, y)
                    if other is not None and other not in done:
                        queue.append(other)  # chain reaction
                        break

        self.bombs = [b for b in self.bombs if b not in done]
        for tile in flame_tiles:
            self.flames[tile] = config.EXPLOSION_DURATION
        for pos in bricks:
            self.grid.destroy_brick(*pos)
            self.score += config.SCORE_BRICK
            if pos in self.hidden_powerups:
                self.powerups[pos] = self.hidden_powerups.pop(pos)
            if pos == self.exit_pos:
                self.exit_revealed = True
        self.events.append("explosion")

    def _update_flames(self, dt: float) -> None:
        for pos in list(self.flames):
            self.flames[pos] -= dt
            if self.flames[pos] <= 0:
                del self.flames[pos]

    # ------------------------------------------------------------ enemies
    def _update_enemies(self, dt: float) -> None:
        for enemy in self.enemies:
            if not enemy.alive:
                continue
            enemy.tick(dt)
            if enemy.can_move():
                direction = ai.choose_direction(enemy, self, self.rng)
                if direction is not None:
                    enemy.move(direction)

    def _touching(self, enemy: Enemy) -> bool:
        if enemy.pos == self.player.pos:
            return True
        ex, ey = enemy.render_pos()
        px, py = self.player.render_pos()
        return math.hypot(ex - px, ey - py) < config.CONTACT_DISTANCE

    @staticmethod
    def _occupied_tiles(mover) -> set[tuple[int, int]]:
        """Tiles a mover touches: while it walks between two tiles it is drawn
        across both, so a flame on either one must hit it."""
        tiles = {mover.pos}
        if not mover.can_move():
            tiles.add((mover.prev_x, mover.prev_y))
        return tiles

    def _check_collisions(self) -> None:
        for enemy in self.enemies:
            if enemy.alive and self._occupied_tiles(enemy) & self.flames.keys():
                enemy.alive = False
                self.score += enemy.points
                self.events.append("enemy_killed")
        self.enemies = [e for e in self.enemies if e.alive]

        if not self.player.alive:
            return
        if self.player.pos in self.flames or any(self._touching(e) for e in self.enemies):
            self._kill_player()

    # --------------------------------------------------------- level flow
    def _kill_player(self) -> None:
        if not self.player.alive:
            return
        self.player.alive = False
        self.player.lives -= 1
        self.state = GameState.PLAYER_DIED
        self.state_timer = config.DEATH_DELAY
        self.events.append("player_died")

    def _after_death(self) -> None:
        if self.player.lives > 0:
            self._load_level(self.level_index)
            self.state = GameState.PLAYING
        else:
            self.state = GameState.GAME_OVER
            self.events.append("game_over")

    def _check_exit(self) -> None:
        if self.exit_open and self.player.pos == self.exit_pos:
            self.score += config.SCORE_LEVEL_COMPLETE
            self.score += int(self.time_left) * config.SCORE_TIME_BONUS_PER_SECOND
            self.state = GameState.LEVEL_COMPLETE
            self.state_timer = config.LEVEL_COMPLETE_DELAY
            self.events.append("level_complete")

    def _advance_level(self) -> None:
        if self.level_index + 1 < len(self.levels):
            self._load_level(self.level_index + 1)
            self.state = GameState.PLAYING
        else:
            self.state = GameState.VICTORY
            self.events.append("victory")
