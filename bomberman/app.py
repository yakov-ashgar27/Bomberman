"""Application shell: window, main loop, keyboard input, sound and screen switching."""
from __future__ import annotations

import sys
from enum import Enum, auto
from pathlib import Path

import pygame

from . import config, i18n
from .game import Action, Game, GameState
from .highscores import HighScoreTable
from .level import load_level_texts
from .renderer import Renderer, make_window_icon
from .settings import Settings
from .sound import SOUND_EVENTS, SoundPlayer

ROOT = Path(__file__).resolve().parent.parent
LEVEL_DIR = ROOT / "levels"

MOVE_KEYS = {
    Action.UP: (pygame.K_UP, pygame.K_w),
    Action.DOWN: (pygame.K_DOWN, pygame.K_s),
    Action.LEFT: (pygame.K_LEFT, pygame.K_a),
    Action.RIGHT: (pygame.K_RIGHT, pygame.K_d),
}
CONFIRM_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER)
MENU_ITEMS = ["start", "language", "sound", "highscores", "quit"]


class Screen(Enum):
    MENU = auto()
    GAME = auto()
    NAME_ENTRY = auto()
    HIGHSCORES = auto()


def _set_windows_icon(ico_path: Path) -> None:
    """Give the window (and its taskbar button) the real .ico at every size.

    pygame only sets a small 32x32 icon, so on Windows the taskbar falls back
    to pythonw's own icon; sending WM_SETICON with the .ico fixes that."""
    if sys.platform != "win32" or not ico_path.exists():
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.LoadImageW.restype = ctypes.c_void_p
        user32.SendMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]
        hwnd = pygame.display.get_wm_info().get("window")
        if not hwnd:
            return
        IMAGE_ICON, LR_LOADFROMFILE, WM_SETICON = 1, 0x10, 0x0080
        big = user32.GetSystemMetrics(11)    # SM_CXICON for this screen's DPI
        small = user32.GetSystemMetrics(49)  # SM_CXSMICON
        for kind, size in ((1, max(big, 48)), (0, small or 16)):  # ICON_BIG = 1, ICON_SMALL = 0
            handle = user32.LoadImageW(None, str(ico_path), IMAGE_ICON, size, size, LR_LOADFROMFILE)
            if handle:
                user32.SendMessageW(hwnd, WM_SETICON, kind, handle)
    except Exception:
        pass


class App:
    def __init__(self):
        if sys.platform == "win32":  # own taskbar entry and icon, not Python's
            try:
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Bomberman.Game")
            except Exception:
                pass
        pygame.mixer.pre_init(config.SAMPLE_RATE, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Bomberman")
        pygame.display.set_icon(make_window_icon())
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        _set_windows_icon(ROOT / "assets" / "bomberman.ico")
        self.clock = pygame.time.Clock()
        self.settings_path = ROOT / config.SETTINGS_FILE
        self.settings = Settings.load(self.settings_path)
        self.renderer = Renderer(self.screen, self.settings.language)
        if self.settings.language == "he" and not self.renderer.hebrew_available:
            self.settings.language = "en"
            self.renderer.set_language("en")
        self.sound = SoundPlayer(enabled=self.settings.sound)
        self.game = Game(load_level_texts(LEVEL_DIR))
        self.highscores = HighScoreTable(ROOT / config.HIGHSCORE_FILE)
        self.current = Screen.MENU
        self.menu_index = 0
        self.menu_note = ""
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
        for event in self.game.events:
            if event in SOUND_EVENTS:
                self.sound.play(event)
            if event in ("game_over", "victory"):
                self.sound.stop_music()

    def draw(self, dt: float) -> None:
        if self.current is Screen.MENU:
            self.renderer.draw_menu(self.menu_labels(), self.menu_index, dt, self.menu_note)
        elif self.current is Screen.GAME:
            self.renderer.draw_game(self.game, dt)
        elif self.current is Screen.NAME_ENTRY:
            self.renderer.draw_name_entry(self.name_buffer, self.game.score, dt)
        elif self.current is Screen.HIGHSCORES:
            self.renderer.draw_highscores(self.highscores.entries, self.highlight_rank, dt)

    def _held_actions(self) -> set[Action]:
        pressed = pygame.key.get_pressed()
        return {action for action, keys in MOVE_KEYS.items() if any(pressed[k] for k in keys)}

    # ---------------------------------------------------------- settings
    def menu_labels(self) -> list[str]:
        lang = self.settings.language
        state = i18n.t("sound_on" if self.settings.sound else "sound_off", lang)
        return [
            i18n.t("menu_start", lang),
            i18n.t("menu_language", lang, name=i18n.LANGUAGE_NAMES[lang]),
            i18n.t("menu_sound", lang, state=state),
            i18n.t("menu_highscores", lang),
            i18n.t("menu_quit", lang),
        ]

    def toggle_language(self) -> None:
        new = i18n.next_language(self.settings.language)
        if new == "he" and not self.renderer.hebrew_available:
            self.menu_note = i18n.t("no_hebrew_font", self.settings.language)
            return
        self.menu_note = ""
        self.settings.language = new
        self.renderer.set_language(new)
        self.settings.save(self.settings_path)

    def toggle_sound(self) -> None:
        self.settings.sound = not self.settings.sound
        self.sound.set_enabled(self.settings.sound)
        if self.settings.sound and self.current is Screen.GAME and self.game.state is GameState.PLAYING:
            self.sound.start_music()
        self.settings.save(self.settings_path)

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
        item = MENU_ITEMS[self.menu_index]
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_index = (self.menu_index - 1) % len(MENU_ITEMS)
            self.sound.play("menu_move")
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_index = (self.menu_index + 1) % len(MENU_ITEMS)
            self.sound.play("menu_move")
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d) and \
                item in ("language", "sound"):
            self._activate(item)
        elif event.key in CONFIRM_KEYS:
            self._activate(item)
        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def _activate(self, item: str) -> None:
        self.sound.play("menu_select")
        if item == "start":
            self.game.start_new_game()
            self.current = Screen.GAME
            self.sound.start_music()
        elif item == "language":
            self.toggle_language()
        elif item == "sound":
            self.toggle_sound()
        elif item == "highscores":
            self.highlight_rank = None
            self.current = Screen.HIGHSCORES
        else:
            self.running = False

    def _game_key(self, event) -> None:
        state = self.game.state
        if event.key == pygame.K_m:
            self.toggle_sound()
        elif event.key in (pygame.K_p, pygame.K_ESCAPE) and state in (GameState.PLAYING, GameState.PAUSED):
            self.game.toggle_pause()
            self.sound.pause_music(self.game.state is GameState.PAUSED)
        elif event.key == pygame.K_q and state is GameState.PAUSED:
            self.sound.stop_music()
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
            self.sound.play("menu_select")
            self.current = Screen.HIGHSCORES
        elif event.key == pygame.K_BACKSPACE:
            self.name_buffer = self.name_buffer[:-1]
        elif event.unicode and event.unicode.isprintable() and \
                len(self.name_buffer) < config.MAX_NAME_LENGTH:
            self.name_buffer += event.unicode

    def _highscores_key(self, event) -> None:
        if event.key in CONFIRM_KEYS or event.key == pygame.K_ESCAPE:
            self.current = Screen.MENU
