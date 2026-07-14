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
LEVEL_START_INVULNERABLE_MS = 600  # short safety window right as a level begins
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
# 1-7 climb gently (capsicum + nanny only, growing corridor maze).
# 8-10 jump up noticeably - the open rectangular arena with multiple
# chasing moms is meant to be the hard tier.
LEVEL_SPEED_SCALE = {
    1: 1.0, 2: 1.0, 3: 1.05, 4: 1.08,
    5: 1.12, 6: 1.16, 7: 1.2,
    8: 1.3, 9: 1.4, 10: 1.5,
}

# ---- Lives ----
MAX_LIVES = 4

# ---- Game zone border (drawn as a black stroke around the walkable
# path's outline; everything else is plain white) ----
GAME_ZONE_BORDER_WIDTH = 4

# ---- Level complete pause ----
LEVEL_COMPLETE_PAUSE_MS = 1500

# ---- Video paths ----
VIDEO_START_SCREEN = "assets/videos/dance.mp4"
VIDEO_MEME_MOM = "assets/videos/shinchan_danger.mp4"  # played muted on the mom meme screen

# ---- Image paths ----
IMAGE_START_SCREEN_CHARACTER = "assets/images/character.png"  # not supplied yet - placeholder shown until added
IMAGE_PLAYER = "assets/images/shinchan.png"
IMAGE_GOAL = "assets/images/nanako.png"
IMAGE_CAPSICUM = "assets/images/capcicum.png"
IMAGE_NANNY = "assets/images/nanny.png"
IMAGE_MOM = "assets/images/misai.png"
IMAGE_RANDOM_OBSTACLE = "assets/images/random_obstacle.png"  # not supplied yet - placeholder shown until added
IMAGE_MEME_CAPSICUM = "assets/images/shinchan eating cap.png"
IMAGE_MEME_MOM = "assets/images/misaiangry.jpg"
IMAGE_MEME_NANNY = "assets/images/nanny on fire.png"
IMAGE_GAME_OVER_CHARACTER = "assets/images/sad_shinchan.jpg"

# ---- Sound paths ----
MUSIC_THEME = "assets/sounds/theme_song.mp3"
SOUND_START = "assets/sounds/Shinchan_balle_balle.mp3"
SOUND_CAUGHT = "assets/sounds/sad_song.mp3"
SOUND_HIT = "assets/sounds/hit.wav"
SOUND_LEVEL_COMPLETE = "assets/sounds/level_complete.wav"
SOUND_GAME_OVER = "assets/sounds/game_over.wav"
SOUND_WIN = "assets/sounds/win.wav"
SOUND_MEME = "assets/sounds/meme.wav"
