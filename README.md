# Bomberman — Software Engineering Course Project

A complete Bomberman clone in Python + Pygame: 3 levels, two enemy types (one
uses BFS path-finding), power-ups, chain-reaction explosions, a level timer,
lives, pause, and a persistent high-score table.

## Documentation

| Document | Link |
|----------|------|
| Software Requirements Specification (Hebrew) | [docs/SRS.md](docs/SRS.md) · [live doc](https://claude.ai/artifact/YUsrtuZm8a6WFD5jfL7bHA) |
| Work plan & team roles (Hebrew) | [docs/WORK_PLAN.md](docs/WORK_PLAN.md) |
| Presentation, 12 slides (Hebrew) | [live deck](https://claude.ai/artifact/8EieE4a2x1gf9HTao65He2) |

![Architecture](docs/images/architecture.png)

## Install & run

**Windows, easiest:** double-click `PLAY_BOMBERMAN.bat`. It finds Python, installs pygame the first time, and starts the game.

Or from a terminal:

```bash
python -m pip install -r requirements.txt     # Python 3.10+
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| Arrows / WASD | Move |
| Space | Drop bomb |
| P / Esc | Pause / resume |
| Q (while paused) | Back to menu |
| Enter | Confirm |

## Rules

* Destroy bricks with bombs. Some hide power-ups: **B** (+1 bomb), **F** (+1 range), **S** (speed).
* One brick hides the exit door. It opens (turns green) once every enemy is dead.
* Enemies, flames (including your own) and the timer running out each cost one life.
* Scoring: brick 10 · power-up 50 · balloon 100 · oneal 200 · level 500 + 5 per second left.

## Run the tests

```bash
python -m pip install pytest
python -m pytest -v
```

59 automated tests cover the game logic (~95% of the logic code). The logic
(`game.py`, `ai.py`, `level.py`, …) never imports pygame, which is why it can
be tested without opening a window.

## Project structure

```
main.py                 entry point
bomberman/
  config.py             every tunable constant (speeds, timers, scores)
  grid.py               Tile enum + Grid (the map)
  entities.py           Direction, Mover, Player, Enemy, Bomb, PowerUpType
  level.py              text level-file parser + validation
  ai.py                 enemy behaviour (wander, BFS chase)
  game.py               Game model + state machine (no pygame)
  highscores.py         JSON high-score table
  renderer.py           all drawing (pygame primitives only)
  app.py                window, main loop, input, screen switching
levels/level1..3.txt    the levels (editable by hand)
tools/generate_levels.py  regenerates the levels from fixed seeds
tests/                  pytest unit + integration tests
```

## Editing levels

Level files are text: `#` wall, `.` floor, `B` brick, `P` player start,
`E` balloon, `O` oneal, `X` brick hiding the exit, `1`/`2`/`3` bricks hiding
bomb/fire/speed power-ups. The border must be walls. Add `level4.txt` and the
game picks it up automatically.
