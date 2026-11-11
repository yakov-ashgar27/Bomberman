"""Lives, timer, pause, level completion and victory (FR-09 .. FR-12)."""
import pytest

from bomberman import config
from bomberman.game import Action, Game, GameState
from tests.helpers import OPEN_LEVEL, freeze_enemies, make_game, run


def clear_level(game):
    """Kill all enemies and reveal the exit, as if the player had done it."""
    game.enemies.clear()
    game.grid.destroy_brick(*game.exit_pos)
    game.exit_revealed = True


def test_new_game_starts_playing():
    game = Game([OPEN_LEVEL])
    assert game.state is GameState.MENU
    game.start_new_game()
    assert game.state is GameState.PLAYING
    assert game.player.lives == config.PLAYER_START_LIVES
    assert game.score == 0 and game.level_number == 1


def test_game_requires_levels():
    with pytest.raises(ValueError):
        Game([])


def test_death_restarts_level_and_keeps_score():
    game = make_game()
    game.score = 300
    game.player.max_bombs = 3
    game._kill_player()
    run(game, config.DEATH_DELAY + 0.1)
    assert game.state is GameState.PLAYING
    assert game.player.alive and game.player.pos == (1, 1)
    assert game.score == 300
    assert game.player.max_bombs == 3           # power-ups survive a death
    assert game.grid.get(5, 1).name == "BRICK"  # level was reset


def test_game_over_after_last_life():
    game = make_game()
    for _ in range(config.PLAYER_START_LIVES):
        game._kill_player()
        run(game, config.DEATH_DELAY + 0.1)
    assert game.state is GameState.GAME_OVER
    assert game.player.lives == 0


def test_timer_counts_down_and_kills_at_zero():
    game = make_game()
    freeze_enemies(game)
    run(game, 1.0)
    assert game.time_left == pytest.approx(config.LEVEL_TIME - 1.0, abs=0.05)
    game.time_left = 0.01
    game.update(0.02)
    assert game.state is GameState.PLAYER_DIED


def test_pause_freezes_everything():
    game = make_game()
    game.place_bomb()
    game.toggle_pause()
    assert game.state is GameState.PAUSED
    time_before = game.time_left
    run(game, 5.0, {Action.RIGHT})
    assert game.time_left == time_before
    assert game.bombs and game.player.pos == (1, 1)
    game.toggle_pause()
    assert game.state is GameState.PLAYING


def test_exit_closed_while_enemies_alive():
    game = make_game()
    freeze_enemies(game)
    game.grid.destroy_brick(*game.exit_pos)
    game.exit_revealed = True
    game.player.place_at(4, 1)
    game.update(0.01, {Action.RIGHT})
    assert game.player.pos == game.exit_pos
    assert game.state is GameState.PLAYING
    assert not game.exit_open


def test_reaching_open_exit_completes_level_with_bonus():
    game = make_game(OPEN_LEVEL, OPEN_LEVEL)
    clear_level(game)
    game.player.place_at(4, 1)
    game.update(0.01, {Action.RIGHT})
    assert game.state is GameState.LEVEL_COMPLETE
    expected = config.SCORE_LEVEL_COMPLETE + int(game.time_left) * config.SCORE_TIME_BONUS_PER_SECOND
    assert game.score == expected
    run(game, config.LEVEL_COMPLETE_DELAY + 0.1)
    assert game.state is GameState.PLAYING and game.level_number == 2
    assert game.time_left == pytest.approx(config.LEVEL_TIME, abs=0.1)


def test_finishing_last_level_is_victory():
    game = make_game()
    clear_level(game)
    game.player.place_at(4, 1)
    game.update(0.01, {Action.RIGHT})
    run(game, config.LEVEL_COMPLETE_DELAY + 0.1)
    assert game.state is GameState.VICTORY


def test_full_playthrough_with_shipped_levels():
    """Smoke test: the real levels load and survive a minute of random input."""
    import random
    from bomberman.level import load_level_texts
    game = Game(load_level_texts("levels"), rng=random.Random(7))
    game.start_new_game()
    rng = random.Random(7)
    for _ in range(60 * 60):
        actions = {rng.choice(list(Action))}
        game.update(1 / 60, actions)
        if game.state is GameState.GAME_OVER:
            break
    assert game.state in (GameState.PLAYING, GameState.PLAYER_DIED, GameState.GAME_OVER)
