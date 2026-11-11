"""Bombs, explosions and chain reactions (FR-04, FR-05, FR-06)."""
from bomberman import config
from bomberman.entities import Bomb, PowerUpType
from bomberman.game import Action, GameState
from bomberman.grid import Tile
from tests.helpers import freeze_enemies, make_game, run


def test_place_bomb_respects_limit():
    game = make_game()
    freeze_enemies(game)
    assert game.place_bomb()
    assert not game.place_bomb()                     # already a bomb here
    game.update(0.01, {Action.RIGHT})
    assert not game.place_bomb()                     # max_bombs = 1
    game.player.max_bombs = 2
    assert game.place_bomb()
    assert len(game.bombs) == 2


def test_bomb_explodes_after_fuse():
    game = make_game()
    freeze_enemies(game)
    game.bombs.append(Bomb(3, 3, 1))
    run(game, config.BOMB_FUSE - 0.1)
    assert len(game.bombs) == 1 and not game.flames
    run(game, 0.2)
    assert not game.bombs
    assert set(game.flames) == {(3, 3), (2, 3), (4, 3), (3, 2), (3, 4)}


def test_flames_stop_at_walls():
    game = make_game()
    freeze_enemies(game)
    game.bombs.append(Bomb(1, 3, 3))
    game.detonate(list(game.bombs))
    assert (0, 3) not in game.flames                 # border wall
    assert (4, 3) in game.flames                     # range 3 to the right
    assert (5, 3) not in game.flames


def test_flame_destroys_only_first_brick_in_line():
    game = make_game()
    freeze_enemies(game)
    game.grid.set(2, 3, Tile.BRICK)
    game.grid.set(3, 3, Tile.BRICK)
    game.bombs.append(Bomb(1, 3, 5))
    game.detonate(list(game.bombs))
    assert game.grid.get(2, 3) is Tile.EMPTY
    assert game.grid.get(3, 3) is Tile.BRICK
    assert game.score == config.SCORE_BRICK


def test_chain_reaction():
    game = make_game()
    freeze_enemies(game)
    first = Bomb(1, 3, 2, timer=0.01)
    second = Bomb(3, 3, 2, timer=99)                 # would not explode on its own
    game.bombs += [first, second]
    game.update(0.02)
    assert not game.bombs
    assert (5, 3) in game.flames                     # reached only by the second bomb


def test_flames_disappear_after_duration():
    game = make_game()
    freeze_enemies(game)
    game.bombs.append(Bomb(3, 3, 1))
    game.detonate(list(game.bombs))
    run(game, config.EXPLOSION_DURATION + 0.05)
    assert not game.flames


def test_destroying_brick_reveals_powerup_and_exit():
    game = make_game()
    freeze_enemies(game)
    game.grid.set(2, 3, Tile.BRICK)
    game.hidden_powerups[(2, 3)] = PowerUpType.BOMB_UP
    game.bombs += [Bomb(1, 3, 1), Bomb(4, 1, 1)]     # second bomb hits the exit brick
    game.detonate(list(game.bombs))
    assert game.powerups == {(2, 3): PowerUpType.BOMB_UP}
    assert game.exit_revealed


def test_player_in_flame_dies():
    game = make_game()
    freeze_enemies(game)
    game.place_bomb()
    run(game, config.BOMB_FUSE + 0.05)
    assert not game.player.alive
    assert game.state is GameState.PLAYER_DIED
    assert game.player.lives == config.PLAYER_START_LIVES - 1


def test_player_escaping_blast_survives():
    game = make_game()
    freeze_enemies(game)
    game.update(0.01, {Action.BOMB})
    run(game, 0.6, {Action.DOWN})                    # (1,1) -> (1,3): out of range 1...
    run(game, 0.4, {Action.RIGHT})                   # ...and around the corner to (2,3)
    run(game, config.BOMB_FUSE)
    assert game.player.alive
    assert game.state is GameState.PLAYING
