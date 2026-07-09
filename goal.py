import random
import pygame
from settings import (
    GOAL_SIZE, GOAL_START_X, GOAL_START_Y, GOAL_WANDER_RANGE, PINK
)


class Goal:
    """
    Nanako. Depending on the level, she either stays still or wanders
    gently within a small area around her start point.
    """

    def __init__(self, movement="static", speed=0.0):
        self.rect = pygame.Rect(0, 0, GOAL_SIZE, GOAL_SIZE)
        self.rect.center = (GOAL_START_X, GOAL_START_Y)
        self.movement = movement  # "static" or "wander"
        self.speed = speed
        self.target = pygame.Vector2(self.rect.center)
        self.image = None
        self._pick_new_wander_target()

    def _pick_new_wander_target(self):
        base_x, base_y = GOAL_START_X, GOAL_START_Y
        self.target = pygame.Vector2(
            base_x + random.randint(-GOAL_WANDER_RANGE, GOAL_WANDER_RANGE),
            base_y + random.randint(-GOAL_WANDER_RANGE, GOAL_WANDER_RANGE),
        )

    def update(self):
        if self.movement != "wander":
            return

        current = pygame.Vector2(self.rect.center)
        direction = self.target - current
        if direction.length() < 4:
            self._pick_new_wander_target()
            return
        direction = direction.normalize() * self.speed
        self.rect.centerx += int(direction.x)
        self.rect.centery += int(direction.y)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.circle(screen, PINK, self.rect.center, GOAL_SIZE // 2)
