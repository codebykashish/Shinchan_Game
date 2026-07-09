import random
import pygame
from settings import WHITE, BLACK, GAME_ZONE_BORDER_WIDTH

# The maze is defined as a set of overlapping rectangles that make up the
# walkable path. Anything outside the union of these rects is a wall.
# This avoids needing to model individual wall segments - a rect is only
# "walkable" if it's inside at least one of these regions (they overlap
# at corridor junctions so movement flows naturally between them).
#
# Every layout keeps the same START (bottom-left) and GOAL (top-right)
# rooms so the player/goal spawn points are always valid, and only the
# corridor shape connecting them changes level to level.

START_ROOM = pygame.Rect(80, 460, 280, 120)   # bottom-left, player starts here
GOAL_ROOM = pygame.Rect(590, 90, 170, 380)    # top-right, goal sits here

LAYOUTS = {
    # Levels 1-2: easiest - one wide, direct corridor.
    1: [
        GOAL_ROOM,
        pygame.Rect(140, 270, 620, 150),
        pygame.Rect(140, 270, 180, 280),
        START_ROOM,
    ],
    2: [
        GOAL_ROOM,
        pygame.Rect(140, 210, 620, 150),
        pygame.Rect(140, 210, 180, 340),
        START_ROOM,
    ],
    # Levels 3-4: easy - still one bend, shifted around a bit more.
    3: [
        GOAL_ROOM,
        pygame.Rect(140, 330, 620, 140),
        pygame.Rect(140, 330, 180, 250),
        START_ROOM,
    ],
    4: [
        GOAL_ROOM,
        pygame.Rect(220, 270, 540, 140),
        pygame.Rect(220, 270, 180, 310),
        START_ROOM,
    ],
    # Levels 5-6: goal starts wandering - single-bend shapes, different jogs.
    5: [
        GOAL_ROOM,
        pygame.Rect(140, 190, 620, 140),
        pygame.Rect(140, 190, 180, 370),
        START_ROOM,
    ],
    6: [
        GOAL_ROOM,
        pygame.Rect(200, 350, 560, 120),
        pygame.Rect(200, 350, 160, 230),
        START_ROOM,
    ],
    # Levels 7-10: two bends (a gentle S-shape) - more turns, but every
    # corridor stays wide, so it's trickier without being a dead end maze.
    7: [
        GOAL_ROOM,
        pygame.Rect(400, 150, 360, 140),
        pygame.Rect(400, 150, 160, 300),
        pygame.Rect(140, 300, 400, 130),
        pygame.Rect(140, 300, 180, 280),
        START_ROOM,
    ],
    8: [
        GOAL_ROOM,
        pygame.Rect(380, 150, 380, 130),
        pygame.Rect(380, 150, 150, 350),
        pygame.Rect(140, 350, 390, 120),
        pygame.Rect(140, 350, 180, 230),
        START_ROOM,
    ],
    9: [
        GOAL_ROOM,
        pygame.Rect(460, 140, 300, 140),
        pygame.Rect(460, 140, 140, 300),
        pygame.Rect(220, 320, 340, 110),
        pygame.Rect(220, 320, 180, 260),
        START_ROOM,
    ],
    10: [
        GOAL_ROOM,
        pygame.Rect(420, 130, 340, 130),
        pygame.Rect(420, 130, 150, 320),
        pygame.Rect(180, 280, 360, 120),
        pygame.Rect(180, 280, 180, 300),
        START_ROOM,
    ],
}

_current_level = 1
_current_rects = LAYOUTS[1]
_current_bounds = None
_outline_cache = {}


def _bounding_rect(rects):
    left = min(r.left for r in rects)
    top = min(r.top for r in rects)
    right = max(r.right for r in rects)
    bottom = max(r.bottom for r in rects)
    return pygame.Rect(left, top, right - left, bottom - top)


def set_level(level_number):
    """Switches the active maze shape - call this before building the
    goal/obstacles/player for a new level."""
    global _current_level, _current_rects, _current_bounds
    _current_level = level_number
    _current_rects = LAYOUTS.get(level_number, LAYOUTS[1])
    _current_bounds = _bounding_rect(_current_rects)


set_level(1)


def _compute_path_outline():
    bounds = _current_bounds.inflate(4, 4)
    mask_surface = pygame.Surface((bounds.width, bounds.height), pygame.SRCALPHA)
    for region in _current_rects:
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), region.move(-bounds.left, -bounds.top))
    outline = pygame.mask.from_surface(mask_surface).outline()
    return [(x + bounds.left, y + bounds.top) for x, y in outline]


def get_path_outline():
    if _current_level not in _outline_cache:
        _outline_cache[_current_level] = _compute_path_outline()
    return _outline_cache[_current_level]


def is_walkable(rect):
    """
    A rect counts as walkable only if ALL FOUR corners land inside at
    least one region. Corners can each be in a different region since
    the regions overlap at junctions - that's what lets movement flow
    from one corridor into the next.
    """
    corners = [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]
    for corner in corners:
        if not any(region.collidepoint(corner) for region in _current_rects):
            return False
    return True


def random_walkable_point(margin=20, avoid=None, avoid_radius=0):
    """
    Picks a random point that sits inside one of the current level's
    walkable corridors (shrunk inward by `margin`), used to spawn
    obstacles so they never appear inside the walls. If `avoid`/
    `avoid_radius` are given, it retries a few times to land outside
    that radius (used to keep obstacles away from the player on spawn).
    """
    point = None
    for _ in range(30):
        region = random.choice(_current_rects)
        shrunk = region.inflate(-margin * 2, -margin * 2)
        if shrunk.width <= 0 or shrunk.height <= 0:
            point = region.center
        else:
            point = (
                random.randint(shrunk.left, shrunk.right),
                random.randint(shrunk.top, shrunk.bottom),
            )
        if avoid is None:
            return point
        dx, dy = point[0] - avoid[0], point[1] - avoid[1]
        if dx * dx + dy * dy >= avoid_radius * avoid_radius:
            return point
    return point


def draw(screen):
    screen.fill(WHITE)  # background everywhere, including the walkable path itself
    outline = get_path_outline()
    if len(outline) >= 3:
        pygame.draw.polygon(screen, BLACK, outline, width=GAME_ZONE_BORDER_WIDTH)
