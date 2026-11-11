"""Player movement and power-ups (FR-03, FR-08)."""
from bomberman import config
from bomberman.entities import Direction, Player, PowerUpType
from bomberman.game import Action
from tests.helpers import freeze_enemies, make_game, run


def test_player_moves_one_tile():
    game = make_game()
    freeze_enemies(game)
    game.update(0.01, {Action.RIGHT})
    assert game.player.pos == (2, 1)
    assert game.player.facing is Direction.RIGHT


def test_movement_speed_respects_cooldown():
    game = make_game()
    freeze_enemies(game)
    game.update(0.01, {Action.RIGHT})
    game.update(0.01, {Action.RIGHT})          # still cooling down
    assert game.player.pos == (2, 1)
    run(game, 1.0 / config.PLAYER_BASE_SPEED, {Action.RIGHT})
    assert game.player.pos == (3, 1)


def test_walls_block_movement():
    game = make_game()
    freeze_enemies(game)
    game.update(0.01, {Action.UP})             # border wall
    game.update(0.01, {Action.LEFT})
    assert game.player.pos == (1, 1)


def test_bricks_block_movement():
    game = make_game()
    freeze_enemies(game)
    run(game, 1.0, {Action.RIGHT})             # walks into the exit brick at (5,1)
    assert game.player.pos == (4, 1)


def test_bombs_block_movement_but_player_can_leave_own_bomb():
    game = make_game()
    freeze_enemies(game)
    game.update(0.01, {Action.BOMB})
    game.update(0.01, {Action.RIGHT})          # leaves the bomb tile
    assert game.player.pos == (2, 1)
    run(game, 0.3, {Action.LEFT})              # cannot walk back onto the bomb
    assert game.player.pos == (2, 1)


def test_direction_priority_when_several_keys_held():
    game = make_game()
    freeze_enemies(game)
    game.update(0.01, {Action.DOWN, Action.RIGHT})
    assert game.player.pos == (1, 2)


def test_render_position_interpolates():
    p = Player(1, 1)
    p.move(Direction.RIGHT)
    p.tick(0.5 / p.speed)
    x, y = p.render_pos()
    assert 1.4 < x < 1.6 and y == 1


def test_powerups_increase_stats_with_caps():
    p = Player()
    p.apply_powerup(PowerUpType.BOMB_UP)
    p.apply_powerup(PowerUpType.FIRE_UP)
    p.apply_powerup(PowerUpType.SPEED_UP)
    assert (p.max_bombs, p.fire_range) == (2, 2)
    assert p.speed == config.PLAYER_BASE_SPEED + config.PLAYER_SPEED_STEP
    for _ in range(20):
        p.apply_powerup(PowerUpType.BOMB_UP)
        p.apply_powerup(PowerUpType.FIRE_UP)
        p.apply_powerup(PowerUpType.SPEED_UP)
    assert p.max_bombs == config.PLAYER_MAX_BOMBS
    assert p.fire_range == config.PLAYER_MAX_FIRE
    assert p.speed == config.PLAYER_MAX_SPEED


def test_walking_over_powerup_collects_it():
    game = make_game()
    freeze_enemies(game)
    game.powerups[(2, 1)] = PowerUpType.FIRE_UP
    game.update(0.01, {Action.RIGHT})
    assert game.player.fire_range == 2
    assert (2, 1) not in game.powerups
    assert game.score == config.SCORE_POWERUP
    assert "powerup" in game.events
