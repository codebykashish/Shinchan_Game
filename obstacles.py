import random
import pygame
from settings import (
    CAPSICUM_SIZE, CAPSICUM_SPEED,
    NANNY_SIZE, NANNY_SPEED,
    MOM_SIZE, MOM_SPEED,
    RANDOM_OBSTACLE_SIZE, RANDOM_OBSTACLE_SPEED, RANDOM_DIRECTION_CHANGE_MS,
    GREEN, BROWN, PURPLE, TEAL,
    PLAYER_START_X, PLAYER_START_Y, OBSTACLE_SPAWN_SAFE_RADIUS,
)
from maze import is_walkable, random_walkable_point

PLAYER_START = (PLAYER_START_X, PLAYER_START_Y)


def _spawn_point(margin):
    return random_walkable_point(
        margin=margin, avoid=PLAYER_START, avoid_radius=OBSTACLE_SPAWN_SAFE_RADIUS
    )


def _bounce_move(rect, velocity):
    """
    Moves rect by velocity but never leaves the walkable corridors -
    if an axis move would land in a wall, that axis is reverted and
    its velocity reflected, so obstacles bounce off corridor edges
    instead of drifting into (or spawning inside) the gray walls.
    """
    moved_x = rect.move(int(velocity.x), 0)
    if is_walkable(moved_x):
        rect = moved_x
    else:
        velocity.x *= -1

    moved_y = rect.move(0, int(velocity.y))
    if is_walkable(moved_y):
        rect = moved_y
    else:
        velocity.y *= -1

    return rect, velocity


class Capsicum:
    """
    Shinchan's nemesis - LINEAR-ish movement. Travels across the
    walkable corridors and bounces off corridor edges, staying inside
    the maze path instead of cutting through the gray walls. Hitting
    this one triggers the meme screen (handled in main.py).
    """

    meme_on_hit = True
    meme_key = "capsicum"

    def __init__(self, speed_multiplier=1.0):
        self.image = None
        self.speed = CAPSICUM_SPEED * speed_multiplier
        self._respawn()

    def _respawn(self):
        x, y = _spawn_point(CAPSICUM_SIZE)
        self.rect = pygame.Rect(0, 0, CAPSICUM_SIZE, CAPSICUM_SIZE)
        self.rect.center = (x, y)

        target_x, target_y = random_walkable_point(margin=CAPSICUM_SIZE)
        direction = pygame.Vector2(target_x - x, target_y - y)
        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)
        self.velocity = direction.normalize() * self.speed

    def update(self):
        self.rect, self.velocity = _bounce_move(self.rect, self.velocity)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, GREEN, self.rect, border_radius=6)


class NannyObstacle:
    """
    DIAGONAL movement - bounces around the maze area at a 45-degree
    angle, like a classic screensaver bouncing off the bounding box edges.
    """

    meme_on_hit = True
    meme_key = "nanny"

    def __init__(self, speed_multiplier=1.0):
        self.image = None
        speed = NANNY_SPEED * speed_multiplier
        self.velocity = pygame.Vector2(
            speed * random.choice([-1, 1]),
            speed * random.choice([-1, 1]),
        )
        x, y = _spawn_point(NANNY_SIZE)
        self.rect = pygame.Rect(0, 0, NANNY_SIZE, NANNY_SIZE)
        self.rect.center = (x, y)

    def update(self):
        self.rect, self.velocity = _bounce_move(self.rect, self.velocity)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, BROWN, self.rect, border_radius=6)


class MomObstacle:
    """
    CHASING movement - continuously moves toward the player's current
    position, but slower than the player so she's always escapable.
    """

    meme_on_hit = True
    meme_key = "mom"

    def __init__(self, speed_multiplier=1.0):
        self.image = None
        self.speed = MOM_SPEED * speed_multiplier
        x, y = _spawn_point(MOM_SIZE)
        self.rect = pygame.Rect(0, 0, MOM_SIZE, MOM_SIZE)
        self.rect.center = (x, y)

    def update(self, player_rect):
        direction = pygame.Vector2(player_rect.centerx - self.rect.centerx,
                                    player_rect.centery - self.rect.centery)
        if direction.length() > 1:
            direction = direction.normalize() * self.speed

        # Move per-axis and only commit each axis if it stays on the
        # walkable path, so she slides along walls instead of cutting
        # through them while chasing.
        moved_x = self.rect.move(int(direction.x), 0)
        if is_walkable(moved_x):
            self.rect = moved_x
        moved_y = self.rect.move(0, int(direction.y))
        if is_walkable(moved_y):
            self.rect = moved_y

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, PURPLE, self.rect, border_radius=10)


class RandomObstacle:
    """
    RANDOM movement - picks a new random direction every so often and
    wanders the maze area unpredictably.
    """

    meme_on_hit = False

    def __init__(self, speed_multiplier=1.0):
        self.image = None
        self.speed = RANDOM_OBSTACLE_SPEED * speed_multiplier
        x, y = _spawn_point(RANDOM_OBSTACLE_SIZE)
        self.rect = pygame.Rect(0, 0, RANDOM_OBSTACLE_SIZE, RANDOM_OBSTACLE_SIZE)
        self.rect.center = (x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.next_direction_change = 0
        self._pick_new_direction()

    def _pick_new_direction(self):
        angle = random.uniform(0, 360)
        self.velocity = pygame.Vector2(1, 0).rotate(angle) * self.speed

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time >= self.next_direction_change:
            self._pick_new_direction()
            self.next_direction_change = current_time + RANDOM_DIRECTION_CHANGE_MS

        self.rect, self.velocity = _bounce_move(self.rect, self.velocity)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, TEAL, self.rect, border_radius=6)
