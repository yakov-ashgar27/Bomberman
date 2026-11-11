"""Application shell: window, main loop, keyboard input and screen switching."""
from __future__ import annotations

from enum import Enum, auto
from pathlib import Path

import pygame

from . import config
from .game import Action, Game, GameState
from .highscores import HighScoreTable
from .level import load_level_texts
from .renderer import Renderer

ROOT = Path(__file__).resolve().parent.parent
LEVEL_DIR = ROOT / "levels"

MOVE_KEYS = {
    Action.UP: (pygame.K_UP, pygame.K_w),
    Action.DOWN: (pygame.K_DOWN, pygame.K_s),
    Action.LEFT: (pygame.K_LEFT, pygame.K_a),
    Action.RIGHT: (pygame.K_RIGHT, pygame.K_d),
}
CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER)
MENU_OPTIONS = ["Start Game", "High Scores", "Quit"]


class Screen(Enum):
    MENU = auto()
    GAME = auto()
    NAME_ENTRY = auto()
    HIGHSCORES = auto()


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Bomberman")
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self.game = Game(load_level_texts(LEVEL_DIR))
        self.highscores = HighScoreTable(ROOT / config.HIGHSCORE_FILE)
        self.current = Screen.MENU
        self.menu_index = 0
        self.name_buffer = ""
        self.highlight_rank: int | None = None
        self.bomb_pressed = False
        self.running = True

    # -------------------------------------------------------------- loop
    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(config.FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw(dt)
            pygame.display.flip()
        pygame.quit()

    def update(self, dt: float) -> None:
        if self.current is not Screen.GAME:
            return
        actions = self._held_actions()
        if self.bomb_pressed:
            actions.add(Action.BOMB)
            self.bomb_pressed = False
        self.game.update(dt, actions)

    def draw(self, dt: float) -> None:
        if self.current is Screen.MENU:
            self.renderer.draw_menu(MENU_OPTIONS, self.menu_index, dt)
        elif self.current is Screen.GAME:
            self.renderer.draw_game(self.game, dt)
        elif self.current is Screen.NAME_ENTRY:
            self.renderer.draw_name_entry(self.name_buffer, self.game.score, dt)
        elif self.current is Screen.HIGHSCORES:
            self.renderer.draw_highscores(self.highscores.entries, self.highlight_rank, dt)

    def _held_actions(self) -> set[Action]:
        pressed = pygame.key.get_pressed()
        return {action for action, keys in MOVE_KEYS.items() if any(pressed[k] for k in keys)}

    # ------------------------------------------------------------- input
    def handle_event(self, event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type != pygame.KEYDOWN:
            return
        handler = {
            Screen.MENU: self._menu_key,
            Screen.GAME: self._game_key,
            Screen.NAME_ENTRY: self._name_key,
            Screen.HIGHSCORES: self._highscores_key,
        }[self.current]
        handler(event)

    def _menu_key(self, event) -> None:
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(MENU_OPTIONS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(MENU_OPTIONS)
        elif event.key in CONFIRM_KEYS:
            choice = MENU_OPTIONS[self.menu_index]
            if choice == "Start Game":
                self.game.start_new_game()
                self.current = Screen.GAME
            elif choice == "High Scores":
                self.highlight_rank = None
                self.current = Screen.HIGHSCORES
            else:
                self.running = False
        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def _game_key(self, event) -> None:
        state = self.game.state
        if event.key in (pygame.K_p, pygame.K_ESCAPE) and state in (GameState.PLAYING, GameState.PAUSED):
            self.game.toggle_pause()
        elif event.key == pygame.K_q and state is GameState.PAUSED:
            self.current = Screen.MENU
        elif event.key == pygame.K_SPACE and state is GameState.PLAYING:
            self.bomb_pressed = True
        elif event.key in CONFIRM_KEYS and state in (GameState.GAME_OVER, GameState.VICTORY):
            if self.highscores.qualifies(self.game.score):
                self.name_buffer = ""
                self.current = Screen.NAME_ENTRY
            else:
                self.highlight_rank = None
                self.current = Screen.HIGHSCORES

    def _name_key(self, event) -> None:
        if event.key in CONFIRM_KEYS:
            self.highlight_rank = self.highscores.add(self.name_buffer, self.game.score)
            self.current = Screen.HIGHSCORES
        elif event.key == pygame.K_BACKSPACE:
            self.name_buffer = self.name_buffer[:-1]
        elif event.unicode and event.unicode.isprintable() and \
                len(self.name_buffer) < config.MAX_NAME_LENGTH:
            self.name_buffer += event.unicode

    def _highscores_key(self, event) -> None:
        if event.key in CONFIRM_KEYS or event.key == pygame.K_ESCAPE:
            self.current = Screen.MENU
