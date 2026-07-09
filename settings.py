"""
All constants for the game live here. Tune numbers here to change
difficulty, speed, sizes, etc. without touching the game logic.
"""

# ---- Screen ----
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# ---- Colors ----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
GREEN = (60, 180, 75)
RED = (220, 50, 50)
YELLOW = (240, 200, 30)
GRAY = (100, 100, 100)
PINK = (240, 140, 170)
ORANGE = (240, 130, 40)
PURPLE = (150, 80, 180)
BROWN = (140, 95, 60)
TEAL = (30, 150, 150)

# ---- Player (Shinchan) ----
PLAYER_SIZE = 40
PLAYER_SPEED = 4
PLAYER_START_X = 200   # starts in the alcove, bottom-left
PLAYER_START_Y = 510
PLAYER_INVULNERABLE_MS = 1200  # brief safety window after a mid-level respawn
LEVEL_START_INVULNERABLE_MS = 2000  # longer safety window right as a level begins
OBSTACLE_SPAWN_SAFE_RADIUS = 150  # obstacles won't spawn this close to the player's start

# ---- Goal (Nanako) ----
GOAL_SIZE = 42
GOAL_START_X = 670     # sits in the entrance corridor, top-right
GOAL_START_Y = 150
GOAL_WANDER_SLOW_SPEED = 1.0
GOAL_WANDER_MEDIUM_SPEED = 1.8
GOAL_WANDER_RANGE = 60  # how far from its start point it wanders

# ---- Obstacles ----
CAPSICUM_SIZE = 32
CAPSICUM_SPEED = 3.0

NANNY_SIZE = 38
NANNY_SPEED = 3.2   # diagonal bouncing movement

MOM_SIZE = 42
MOM_SPEED = 2.6   # kept below PLAYER_SPEED so she's escapable

RANDOM_OBSTACLE_SIZE = 34
RANDOM_OBSTACLE_SPEED = 2.8
RANDOM_DIRECTION_CHANGE_MS = 1200  # how often it picks a new random direction

# Multiplier applied to obstacle speeds per level (levels are 1-indexed).
# Gentle, steady growth so level 10 is noticeably harder than level 1 but
# still beatable - 1-2 easiest, 3-4 easy, climbing gradually from there.
LEVEL_SPEED_SCALE = {
    1: 1.0, 2: 1.0, 3: 1.05, 4: 1.08,
    5: 1.12, 6: 1.16, 7: 1.2, 8: 1.24,
    9: 1.28, 10: 1.32,
}

# ---- Lives ----
MAX_LIVES = 4

# ---- Game zone border (drawn as a black stroke around the walkable
# path's outline; everything else is plain white) ----
GAME_ZONE_BORDER_WIDTH = 4

# ---- Level complete pause ----
LEVEL_COMPLETE_PAUSE_MS = 1500

# ---- Image paths ----
IMAGE_START_SCREEN_CHARACTER = "assets/images/character.png"  # not supplied yet - placeholder shown until added
IMAGE_PLAYER = "assets/images/shinchan.png"
IMAGE_GOAL = "assets/images/nanako.jpg"
IMAGE_CAPSICUM = "assets/images/capcicum.png"
IMAGE_NANNY = "assets/images/nanny.jpg"
IMAGE_MOM = "assets/images/misai.jpg"
IMAGE_RANDOM_OBSTACLE = "assets/images/random_obstacle.png"  # not supplied yet - placeholder shown until added
IMAGE_MEME_CAPSICUM = "assets/memes/capsicum_meme.png"  # not supplied yet - placeholder shown until added
IMAGE_MEME_MOM = "assets/images/misaiangry.jpg"
IMAGE_MEME_NANNY = "assets/images/nands.jpg"

# ---- Sound paths ----
# theme_song.mp4 currently on disk is a broken placeholder (a failed
# download, not real audio) - point MUSIC_THEME at it and swap in a real
# .ogg/.mp3/.wav file whenever it's ready, no code changes needed.
MUSIC_THEME = "assets/sounds/theme_song.mp4"
SOUND_HIT = "assets/sounds/hit.wav"
SOUND_LEVEL_COMPLETE = "assets/sounds/level_complete.wav"
SOUND_GAME_OVER = "assets/sounds/game_over.wav"
SOUND_WIN = "assets/sounds/win.wav"
SOUND_MEME = "assets/sounds/meme.wav"
