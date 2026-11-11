"""Game-wide constants. Every tunable number lives here so balancing never touches logic."""

# --- Screen / grid -------------------------------------------------------
TILE_SIZE = 48
GRID_WIDTH = 15
GRID_HEIGHT = 13
HUD_HEIGHT = 56
SCREEN_WIDTH = GRID_WIDTH * TILE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE + HUD_HEIGHT
FPS = 60
MAX_FRAME_DT = 0.05  # clamp long frames so the simulation never "jumps"

# --- Bombs & explosions --------------------------------------------------
BOMB_FUSE = 2.5            # seconds until a bomb explodes
EXPLOSION_DURATION = 0.5   # seconds a flame tile stays deadly

# --- Player --------------------------------------------------------------
PLAYER_START_LIVES = 3
PLAYER_BASE_SPEED = 5.0    # tiles per second
PLAYER_SPEED_STEP = 1.0
PLAYER_MAX_SPEED = 8.0
PLAYER_START_BOMBS = 1
PLAYER_MAX_BOMBS = 8
PLAYER_START_FIRE = 1
PLAYER_MAX_FIRE = 8
CONTACT_DISTANCE = 0.6     # player/enemy overlap (in tiles) that counts as a hit

# --- Level flow ----------------------------------------------------------
LEVEL_TIME = 180.0         # seconds per level
DEATH_DELAY = 1.5          # pause after the player dies
LEVEL_COMPLETE_DELAY = 2.0 # pause on the "level complete" screen

# --- Scoring -------------------------------------------------------------
SCORE_BRICK = 10
SCORE_POWERUP = 50
SCORE_LEVEL_COMPLETE = 500
SCORE_TIME_BONUS_PER_SECOND = 5

# --- Enemies -------------------------------------------------------------
# speed in tiles/sec; chase_range 0 = never chases the player
ENEMY_STATS = {
    "balloon": {"speed": 2.0, "points": 100, "chase_range": 0},
    "oneal": {"speed": 3.0, "points": 200, "chase_range": 6},
}
ENEMY_TURN_CHANCE = 0.2    # chance a wandering enemy turns at a junction

# --- Sound ---------------------------------------------------------------
SAMPLE_RATE = 22050
SFX_VOLUME = 0.7
MUSIC_VOLUME = 0.35

# --- Settings ------------------------------------------------------------
SETTINGS_FILE = "settings.json"
# fonts tried, in order, for Hebrew text (pygame's built-in font has no Hebrew)
HEBREW_FONT_FILES = ["arial.ttf", "segoeui.ttf", "tahoma.ttf", "david.ttf", "calibri.ttf"]  # Windows
HEBREW_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",                # Linux
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",                   # macOS
    "/Library/Fonts/Arial Unicode.ttf",
]
HEBREW_FONTS = ["arial", "segoeui", "tahoma", "dejavusans", "freesans",
                "liberationsans", "notosanshebrew", "david", "arialunicodems"]

# --- High scores ---------------------------------------------------------
HIGHSCORE_FILE = "highscores.json"
MAX_HIGHSCORES = 5
MAX_NAME_LENGTH = 10
