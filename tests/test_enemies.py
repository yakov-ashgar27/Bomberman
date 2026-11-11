"""Enemy AI and contact (FR-07)."""
import random

from bomberman import config
from bomberman.ai import choose_direction, find_path_step, manhattan
from bomberman.entities import Bomb, Direction, Enemy
from bomberman.game import Action, GameState
from bomberman.grid import Tile
from tests.helpers import freeze_enemies, make_game, run


def test_bfs_finds_shortest_first_step():
    game = make_game()
    # from (1,3) to (3,3): straight right along the open row
    assert find_path_step(game, (1, 3), (3, 3)) is Direction.RIGHT
    # around a pillar: (3,1) -> (3,3) must go down through (3,2)
    assert find_path_step(game, (3, 1), (3, 3)) is Direction.DOWN


def test_bfs_returns_none_when_unreachable():
    game = make_game()
    for pos in [(1, 2), (2, 1)]:
        game.grid.set(*pos, Tile.BRICK)
    assert find_path_step(game, (5, 5), (1, 1)) is None


def test_bfs_avoids_bombs():
    game = make_game()
    game.bombs.append(Bomb(2, 3, 1))
    step = find_path_step(game, (1, 3), (3, 3))
    assert step is not Direction.RIGHT


def test_wandering_enemy_never_walks_into_walls():
    game = make_game(seed=42)
    enemy = Enemy("balloon", 1, 1)
    rng = random.Random(1)
    for _ in range(200):
        d = choose_direction(enemy, game, rng)
        assert d is not None
        assert game.is_walkable(enemy.x + d.dx, enemy.y + d.dy)
        enemy.move(d)


def test_trapped_enemy_stays_still():
    game = make_game()
    enemy = Enemy("balloon", 1, 3)
    game.grid.set(1, 2, Tile.BRICK)
    game.grid.set(1, 4, Tile.BRICK)
    game.grid.set(2, 3, Tile.BRICK)
    assert choose_direction(enemy, game, random.Random(0)) is None


def test_oneal_chases_player_in_range():
    game = make_game()
    oneal = Enemy("oneal", 4, 1)
    game.player.place_at(1, 1)
    assert manhattan(oneal.pos, game.player.pos) <= oneal.chase_range
    assert choose_direction(oneal, game, random.Random(0)) is Direction.LEFT


def test_enemy_in_flame_dies_and_scores():
    game = make_game()
    freeze_enemies(game)
    enemy = game.enemies[0]
    game.bombs.append(Bomb(enemy.x - 1, enemy.y, 1, timer=0.01))
    game.update(0.02)
    assert game.enemies_remaining == 0
    assert game.score == config.ENEMY_STATS["balloon"]["points"]
    assert "enemy_killed" in game.events


def test_enemy_contact_kills_player():
    game = make_game()
    freeze_enemies(game)
    game.enemies[0].place_at(2, 1)
    game.enemies[0].cooldown = 1e9
    game.update(0.01)
    assert game.state is GameState.PLAYING      # adjacent is not touching
    run(game, 0.3, {Action.RIGHT})               # walk into the enemy
    assert game.state is GameState.PLAYER_DIED


def test_enemies_move_over_time():
    game = make_game(seed=3)
    start = game.enemies[0].pos
    game.player.place_at(1, 5)        # keep the player out of the way
    run(game, 2.0)
    assert game.enemies[0].pos != start
