import pygame
from settings import (
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_START_X, PLAYER_START_Y,
    PLAYER_INVULNERABLE_MS, RED
)
from maze import is_walkable


class Player:
    """
    Shinchan. Moves freely with arrows or WASD, but is blocked by maze
    walls. Movement is checked per-axis so hitting a wall diagonally
    still lets you slide along it instead of stopping dead.
    """

    def __init__(self):
        self.rect = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
        self.rect.center = (PLAYER_START_X, PLAYER_START_Y)
        self.invulnerable_until = 0
        self.image = None

    def respawn(self, current_time_ms, invulnerable_ms=PLAYER_INVULNERABLE_MS):
        self.rect.center = (PLAYER_START_X, PLAYER_START_Y)
        self.invulnerable_until = current_time_ms + invulnerable_ms

    def is_invulnerable(self, current_time_ms):
        return current_time_ms < self.invulnerable_until

    def handle_movement(self, keys):
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        # Try horizontal movement on its own
        moved_x = self.rect.move(int(dx * PLAYER_SPEED), 0)
        if is_walkable(moved_x):
            self.rect = moved_x

        # Try vertical movement on its own - this is what lets the
        # player slide along a wall instead of getting fully stuck
        moved_y = self.rect.move(0, int(dy * PLAYER_SPEED))
        if is_walkable(moved_y):
            self.rect = moved_y

    def draw(self, screen, current_time_ms):
        if self.is_invulnerable(current_time_ms) and (current_time_ms // 150) % 2 == 0:
            return
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, RED, self.rect, border_radius=8)
