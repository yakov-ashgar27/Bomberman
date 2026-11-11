"""Shared test helpers: tiny hand-made levels and a fast-forward function."""
import random

from bomberman.game import Game

# Open arena: player top-left, one balloon bottom-right, exit hidden under the brick at (5,1).
OPEN_LEVEL = """
#########
#P...X..#
#.#.#.#.#
#.......#
#.#.#.#.#
#......E#
#########
"""


def make_game(*levels: str, seed: int = 0) -> Game:
    game = Game(list(levels) or [OPEN_LEVEL], rng=random.Random(seed))
    game.start_new_game()
    return game


def freeze_enemies(game: Game) -> None:
    """Stop enemies moving so a test controls everything."""
    for enemy in game.enemies:
        enemy.speed = 1e-9
        enemy.cooldown = 1e9


def run(game: Game, seconds: float, actions=frozenset(), step: float = 1 / 60) -> None:
    t = 0.0
    while t < seconds - 1e-9:
        game.update(step, set(actions))
        t += step
