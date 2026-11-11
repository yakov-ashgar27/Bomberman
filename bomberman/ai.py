"""Enemy decision making.

* balloon: wanders - keeps going straight, sometimes turns, never stuck.
* oneal:   wanders, but when the player is within chase_range it follows the
           shortest path to the player (breadth-first search).
"""
from __future__ import annotations

import random
from collections import deque
from typing import TYPE_CHECKING

from . import config
from .entities import Direction, Enemy

if TYPE_CHECKING:
    from .game import Game


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def find_path_step(game: "Game", start: tuple[int, int], goal: tuple[int, int],
                   max_depth: int = 50) -> Direction | None:
    """First step of the shortest walkable path from start to goal, or None."""
    if start == goal:
        return None
    queue = deque([(start, None, 0)])
    visited = {start}
    while queue:
        (x, y), first_step, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for d in Direction:
            nxt = (x + d.dx, y + d.dy)
            if nxt in visited:
                continue
            if nxt != goal and not game.is_walkable(*nxt):
                continue
            step = first_step or d
            if nxt == goal:
                return step
            visited.add(nxt)
            queue.append((nxt, step, depth + 1))
    return None


def wander(enemy: Enemy, options: list[Direction], rng: random.Random) -> Direction:
    keep_going = enemy.direction in options and rng.random() >= config.ENEMY_TURN_CHANCE
    if keep_going:
        return enemy.direction
    # avoid turning straight back unless it is the only way out
    if len(options) > 1 and enemy.direction is not None:
        forward = [d for d in options if d is not enemy.direction.opposite]
        if forward:
            options = forward
    return rng.choice(options)


def choose_direction(enemy: Enemy, game: "Game", rng: random.Random) -> Direction | None:
    options = [d for d in Direction if game.is_walkable(enemy.x + d.dx, enemy.y + d.dy)]
    player = game.player

    if enemy.chase_range > 0 and player.alive and \
            manhattan(enemy.pos, player.pos) <= enemy.chase_range:
        step = find_path_step(game, enemy.pos, player.pos, max_depth=enemy.chase_range * 3)
        if step is not None:
            enemy.direction = step
            return step

    if not options:
        return None
    enemy.direction = wander(enemy, options, rng)
    return enemy.direction
