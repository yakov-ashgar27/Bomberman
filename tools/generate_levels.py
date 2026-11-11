"""Generate the level files in ../levels with a fixed seed (reproducible).

Run:  python tools/generate_levels.py
Level files are plain text, so they can also be edited by hand afterwards.
"""
from __future__ import annotations

import random
from pathlib import Path

WIDTH, HEIGHT = 15, 13
OUT = Path(__file__).resolve().parent.parent / "levels"

# seed, brick density, enemies, hidden power-ups ("1" bomb, "2" fire, "3" speed)
LEVELS = [
    (101, 0.35, "EEE", "12"),
    (202, 0.42, "EEEOO", "123"),
    (303, 0.48, "EEOOOO", "1232"),
]
SAFE_ZONE = {(1, 1), (2, 1), (1, 2), (3, 1), (1, 3)}  # keep the start corner open


def build(seed: int, density: float, enemies: str, powerups: str) -> list[str]:
    rng = random.Random(seed)
    rows = [["." for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if x in (0, WIDTH - 1) or y in (0, HEIGHT - 1) or (x % 2 == 0 and y % 2 == 0):
                rows[y][x] = "#"
    open_tiles = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)
                  if rows[y][x] == "." and (x, y) not in SAFE_ZONE]
    for x, y in open_tiles:
        if rng.random() < density:
            rows[y][x] = "B"

    bricks = [(x, y) for (x, y) in open_tiles if rows[y][x] == "B"]
    rng.shuffle(bricks)
    far_bricks = [b for b in bricks if b[0] + b[1] >= 10]
    exit_x, exit_y = far_bricks.pop()
    rows[exit_y][exit_x] = "X"
    for ch in powerups:
        x, y = far_bricks.pop()
        rows[y][x] = ch

    free = [(x, y) for (x, y) in open_tiles if rows[y][x] == "." and x + y >= 8]
    rng.shuffle(free)
    for ch in enemies:
        x, y = free.pop()
        rows[y][x] = ch

    rows[1][1] = "P"
    return ["".join(r) for r in rows]


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for i, (seed, density, enemies, powerups) in enumerate(LEVELS, start=1):
        lines = build(seed, density, enemies, powerups)
        header = f"; Level {i} - generated with seed {seed}\n"
        (OUT / f"level{i}.txt").write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
        print(f"level{i}.txt")
        print("\n".join(lines))


if __name__ == "__main__":
    main()
