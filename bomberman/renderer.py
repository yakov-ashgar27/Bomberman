"""All drawing. Uses only pygame primitives, so the game needs no image files."""
from __future__ import annotations

import math

import pygame

from . import config
from .entities import Direction, PowerUpType
from .game import Game, GameState
from .grid import Tile

TS = config.TILE_SIZE
TOP = config.HUD_HEIGHT

# palette
BG = (24, 26, 33)
FLOOR = (62, 120, 74)
FLOOR_ALT = (58, 112, 69)
WALL = (92, 96, 110)
WALL_LIGHT = (130, 135, 150)
WALL_DARK = (58, 61, 72)
BRICK = (176, 98, 52)
MORTAR = (120, 64, 34)
HUD_BG = (16, 17, 22)
WHITE = (240, 240, 240)
GREY = (150, 150, 160)
YELLOW = (255, 214, 64)
ORANGE = (255, 140, 30)
RED = (220, 50, 50)
BLUE = (60, 110, 230)

POWERUP_STYLE = {
    PowerUpType.BOMB_UP: ((50, 50, 60), "B"),
    PowerUpType.FIRE_UP: ((220, 80, 30), "F"),
    PowerUpType.SPEED_UP: ((40, 150, 220), "S"),
}
ENEMY_COLORS = {"balloon": (240, 120, 170), "oneal": (130, 90, 220)}


def tile_rect(x: float, y: float) -> pygame.Rect:
    return pygame.Rect(int(x * TS), int(y * TS) + TOP, TS, TS)


class Renderer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 26)
        self.font = pygame.font.Font(None, 36)
        self.font_big = pygame.font.Font(None, 72)
        self.clock = 0.0  # used for simple animations

    # ------------------------------------------------------------ helpers
    def _text(self, text, font, color, center=None, topleft=None):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center is not None:
            rect.center = center
        elif topleft is not None:
            rect.topleft = topleft
        self.screen.blit(surface, rect)
        return rect

    def _overlay(self, alpha: int = 170):
        shade = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, alpha))
        self.screen.blit(shade, (0, 0))

    # -------------------------------------------------------------- world
    def draw_game(self, game: Game, dt: float) -> None:
        self.clock += dt
        self.screen.fill(BG)
        self._draw_grid(game)
        self._draw_exit(game)
        self._draw_powerups(game)
        self._draw_bombs(game)
        self._draw_flames(game)
        for enemy in game.enemies:
            self._draw_enemy(enemy)
        self._draw_player(game)
        self._draw_hud(game)

        cx, cy = config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2
        if game.state is GameState.PAUSED:
            self._overlay()
            self._text("PAUSED", self.font_big, WHITE, center=(cx, cy - 30))
            self._text("P / Esc - resume     Q - quit to menu", self.font_small, GREY,
                       center=(cx, cy + 30))
        elif game.state is GameState.LEVEL_COMPLETE:
            self._overlay(140)
            self._text(f"LEVEL {game.level_number} COMPLETE!", self.font_big, YELLOW,
                       center=(cx, cy))
        elif game.state is GameState.GAME_OVER:
            self._overlay()
            self._text("GAME OVER", self.font_big, RED, center=(cx, cy - 30))
            self._text(f"Score: {game.score}", self.font, WHITE, center=(cx, cy + 25))
            self._text("Press Enter", self.font_small, GREY, center=(cx, cy + 65))
        elif game.state is GameState.VICTORY:
            self._overlay()
            self._text("YOU WIN!", self.font_big, YELLOW, center=(cx, cy - 30))
            self._text(f"Final score: {game.score}", self.font, WHITE, center=(cx, cy + 25))
            self._text("Press Enter", self.font_small, GREY, center=(cx, cy + 65))

    def _draw_grid(self, game: Game) -> None:
        for y in range(game.grid.height):
            for x in range(game.grid.width):
                rect = tile_rect(x, y)
                tile = game.grid.get(x, y)
                if tile is Tile.WALL:
                    pygame.draw.rect(self.screen, WALL, rect)
                    pygame.draw.line(self.screen, WALL_LIGHT, rect.topleft, rect.topright, 3)
                    pygame.draw.line(self.screen, WALL_LIGHT, rect.topleft, rect.bottomleft, 3)
                    pygame.draw.line(self.screen, WALL_DARK, rect.bottomleft, rect.bottomright, 3)
                    pygame.draw.line(self.screen, WALL_DARK, rect.topright, rect.bottomright, 3)
                else:
                    color = FLOOR if (x + y) % 2 == 0 else FLOOR_ALT
                    pygame.draw.rect(self.screen, color, rect)
                    if tile is Tile.BRICK:
                        self._draw_brick(rect)

    def _draw_brick(self, rect: pygame.Rect) -> None:
        pygame.draw.rect(self.screen, BRICK, rect.inflate(-2, -2))
        rows = 3
        h = rect.height / rows
        for r in range(1, rows):
            y = int(rect.top + r * h)
            pygame.draw.line(self.screen, MORTAR, (rect.left, y), (rect.right - 1, y), 2)
        for r in range(rows):
            offset = rect.width // 2 if r % 2 else rect.width // 4
            x = rect.left + offset
            top = int(rect.top + r * h)
            pygame.draw.line(self.screen, MORTAR, (x, top), (x, int(top + h)), 2)

    def _draw_exit(self, game: Game) -> None:
        if not game.exit_revealed:
            return
        rect = tile_rect(*game.exit_pos).inflate(-10, -6)
        color = (60, 200, 90) if game.exit_open else (90, 90, 90)
        pygame.draw.rect(self.screen, color, rect, border_radius=6)
        pygame.draw.rect(self.screen, (20, 20, 20), rect, 3, border_radius=6)
        pygame.draw.circle(self.screen, YELLOW, (rect.right - 9, rect.centery), 3)

    def _draw_powerups(self, game: Game) -> None:
        for (x, y), kind in game.powerups.items():
            color, letter = POWERUP_STYLE[kind]
            rect = tile_rect(x, y).inflate(-12, -12)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
            self._text(letter, self.font, WHITE, center=rect.center)

    def _draw_bombs(self, game: Game) -> None:
        for bomb in game.bombs:
            rect = tile_rect(bomb.x, bomb.y)
            pulse = 1.0 + 0.08 * math.sin((config.BOMB_FUSE - bomb.timer) * (6 + 10 / max(bomb.timer, 0.3)))
            radius = int(TS * 0.36 * pulse)
            pygame.draw.circle(self.screen, (20, 20, 25), rect.center, radius)
            pygame.draw.circle(self.screen, (80, 80, 90),
                               (rect.centerx - radius // 3, rect.centery - radius // 3), radius // 4)
            fuse_end = (rect.centerx + radius // 2, rect.centery - radius - 4)
            pygame.draw.line(self.screen, (200, 180, 120),
                             (rect.centerx + radius // 3, rect.centery - radius + 4), fuse_end, 3)
            if int(self.clock * 12) % 2 == 0:
                pygame.draw.circle(self.screen, YELLOW, fuse_end, 4)

    def _draw_flames(self, game: Game) -> None:
        for (x, y), remaining in game.flames.items():
            rect = tile_rect(x, y)
            strength = max(0.2, remaining / config.EXPLOSION_DURATION)
            outer = rect.inflate(-int(TS * (1 - strength) * 0.5), -int(TS * (1 - strength) * 0.5))
            pygame.draw.rect(self.screen, ORANGE, outer, border_radius=10)
            pygame.draw.rect(self.screen, YELLOW, outer.inflate(-14, -14), border_radius=8)

    def _eyes(self, cx: float, cy: float, facing: Direction, size: int) -> None:
        dx, dy = facing.dx * size // 2, facing.dy * size // 2
        for side in (-1, 1):
            ex = cx + side * size + dx
            ey = cy - size // 2 + dy
            pygame.draw.circle(self.screen, WHITE, (int(ex), int(ey)), size // 2 + 2)
            pygame.draw.circle(self.screen, (10, 10, 10), (int(ex + dx // 2), int(ey + dy // 2)), size // 3)

    def _draw_player(self, game: Game) -> None:
        p = game.player
        x, y = p.render_pos()
        rect = tile_rect(x, y)
        if not p.alive:
            # shrink & flash while dying
            t = max(0.0, game.state_timer / config.DEATH_DELAY)
            radius = int(TS * 0.4 * t)
            if radius > 2:
                pygame.draw.circle(self.screen, RED, rect.center, radius)
            return
        body = pygame.Rect(0, 0, int(TS * 0.7), int(TS * 0.78))
        body.center = (rect.centerx, rect.centery + 2)
        pygame.draw.ellipse(self.screen, WHITE, body)
        pygame.draw.ellipse(self.screen, BLUE, body, 3)
        pygame.draw.rect(self.screen, (230, 70, 140),
                         pygame.Rect(body.left + 4, body.centery + 4, body.width - 8, 5))
        self._eyes(rect.centerx, rect.centery, p.facing, 7)

    def _draw_enemy(self, enemy) -> None:
        x, y = enemy.render_pos()
        rect = tile_rect(x, y)
        color = ENEMY_COLORS.get(enemy.kind, RED)
        bob = int(2 * math.sin(self.clock * 6 + x + y))
        center = (rect.centerx, rect.centery + bob)
        pygame.draw.circle(self.screen, color, center, int(TS * 0.38))
        pygame.draw.circle(self.screen, (30, 20, 30), center, int(TS * 0.38), 2)
        facing = enemy.direction or Direction.DOWN
        self._eyes(center[0], center[1], facing, 6)
        if enemy.kind == "oneal":  # angry brows
            pygame.draw.line(self.screen, (20, 10, 20), (center[0] - 12, center[1] - 14),
                             (center[0] - 3, center[1] - 9), 3)
            pygame.draw.line(self.screen, (20, 10, 20), (center[0] + 12, center[1] - 14),
                             (center[0] + 3, center[1] - 9), 3)

    def _draw_hud(self, game: Game) -> None:
        pygame.draw.rect(self.screen, HUD_BG, (0, 0, config.SCREEN_WIDTH, TOP))
        p = game.player
        minutes, seconds = divmod(int(math.ceil(game.time_left)), 60)
        time_color = RED if game.time_left < 30 else WHITE
        y = TOP // 2
        self._text(f"LEVEL {game.level_number}/{game.level_count}", self.font_small, YELLOW,
                   center=(70, y))
        self._text(f"SCORE {game.score:06d}", self.font_small, WHITE, center=(215, y))
        self._text(f"{minutes}:{seconds:02d}", self.font, time_color, center=(345, y))
        self._text(f"LIVES {max(p.lives, 0)}", self.font_small, (255, 120, 120), center=(445, y))
        self._text(f"B{p.max_bombs} F{p.fire_range} S{int(p.speed)}", self.font_small, GREY,
                   center=(555, y))
        self._text(f"ENEMIES {game.enemies_remaining}", self.font_small, GREY, center=(662, y))

    # ------------------------------------------------------------ screens
    def draw_menu(self, options: list[str], selected: int, dt: float) -> None:
        self.clock += dt
        self.screen.fill(BG)
        cx = config.SCREEN_WIDTH // 2
        bob = int(6 * math.sin(self.clock * 2))
        self._text("BOMBERMAN", self.font_big, ORANGE, center=(cx, 170 + bob))
        self._text("Software Engineering Project", self.font_small, GREY, center=(cx, 225))
        for i, option in enumerate(options):
            color = YELLOW if i == selected else WHITE
            label = f"> {option} <" if i == selected else option
            self._text(label, self.font, color, center=(cx, 330 + i * 55))
        self._text("Arrows / WASD move   Space bomb   P pause", self.font_small, GREY,
                   center=(cx, config.SCREEN_HEIGHT - 50))

    def draw_name_entry(self, name: str, score: int, dt: float) -> None:
        self.clock += dt
        self.screen.fill(BG)
        cx = config.SCREEN_WIDTH // 2
        self._text("NEW HIGH SCORE!", self.font_big, YELLOW, center=(cx, 200))
        self._text(f"{score}", self.font, WHITE, center=(cx, 270))
        self._text("Enter your name:", self.font, GREY, center=(cx, 340))
        cursor = "_" if int(self.clock * 2) % 2 == 0 else " "
        self._text(name + cursor, self.font_big, WHITE, center=(cx, 410))
        self._text("Enter - save", self.font_small, GREY, center=(cx, 480))

    def draw_highscores(self, entries, highlight: int | None, dt: float) -> None:
        self.clock += dt
        self.screen.fill(BG)
        cx = config.SCREEN_WIDTH // 2
        self._text("HIGH SCORES", self.font_big, ORANGE, center=(cx, 130))
        if not entries:
            self._text("No scores yet - go play!", self.font, GREY, center=(cx, 300))
        for i, entry in enumerate(entries):
            color = YELLOW if highlight == i + 1 else WHITE
            self._text(f"{i + 1}.  {entry.name:<10}  {entry.score:>7}", self.font, color,
                       center=(cx, 230 + i * 50))
        self._text("Enter / Esc - back", self.font_small, GREY,
                   center=(cx, config.SCREEN_HEIGHT - 60))
