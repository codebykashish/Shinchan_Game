"""
Shinchan Arena Runner (working title) - basic version.

Controls:
  Arrow keys or WASD - move Shinchan freely
  ENTER              - start game / continue past meme screen / advance
  R                  - restart after game over or winning
  ESC                - quit
"""

import os
import sys
import random
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, GREEN, RED,
    MAX_LIVES, LEVEL_COMPLETE_PAUSE_MS, LEVEL_START_INVULNERABLE_MS,
    PLAYER_SIZE, GOAL_SIZE, CAPSICUM_SIZE, NANNY_SIZE, MOM_SIZE, RANDOM_OBSTACLE_SIZE,
    OBSTACLE_SPAWN_SAFE_RADIUS,
    IMAGE_START_SCREEN_CHARACTER, IMAGE_PLAYER, IMAGE_GOAL,
    IMAGE_CAPSICUM, IMAGE_NANNY, IMAGE_MOM, IMAGE_RANDOM_OBSTACLE,
    IMAGE_MEME_CAPSICUM, IMAGE_MEME_MOM, IMAGE_MEME_NANNY,
    MUSIC_THEME, SOUND_HIT, SOUND_LEVEL_COMPLETE, SOUND_GAME_OVER,
    SOUND_WIN, SOUND_MEME,
)
import maze
from player import Player
from levels import build_goal, build_obstacles, TOTAL_LEVELS
from sound_manager import SoundManager

# ---- States ----
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_MEME = "meme"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"
STATE_ALL_COMPLETE = "all_complete"

# Captions and placeholder image slots per obstacle type. Each hit
# type gets its own little meme moment - swap the image paths in
# settings.py once real pictures/gifs are ready.
MEME_CAPTIONS = {
    "capsicum": [
        "Shinchan touches capsicum.\nShinchan regrets everything.",
        "[ MEME PLACEHOLDER ]\nSwap this for your own image/gif.",
        "Capsicum: 1   Shinchan: 0",
        "Some things in life cannot be unseen.\nCapsicum is one of them.",
    ],
    "mom": [
        "Caught by Mom.\nMisae is NOT happy right now.",
        "Mom: 1   Shinchan: 0",
    ],
    "nanny": [
        "[ MEME PLACEHOLDER ]\nNanny drags Shinchan off to play house-house.",
        "Not the house-house game again...",
    ],
}


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Shinchan Arena Runner (basic version)")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont(None, 60)
        self.font_medium = pygame.font.SysFont(None, 34)
        self.font_small = pygame.font.SysFont(None, 26)

        self.sound_manager = SoundManager()
        self.sound_manager.load_sound("hit", SOUND_HIT)
        self.sound_manager.load_sound("level_complete", SOUND_LEVEL_COMPLETE)
        self.sound_manager.load_sound("game_over", SOUND_GAME_OVER)
        self.sound_manager.load_sound("win", SOUND_WIN)
        self.sound_manager.load_sound("meme", SOUND_MEME)

        self.start_character_image = self.load_image_safe(
            IMAGE_START_SCREEN_CHARACTER, max_height=220
        )
        self.meme_images = {
            "capsicum": self.load_image_safe(IMAGE_MEME_CAPSICUM, max_height=250),
            "mom": self.load_image_safe(IMAGE_MEME_MOM, max_height=250),
            "nanny": self.load_image_safe(IMAGE_MEME_NANNY, max_height=250),
        }

        # Sprite images shared by all levels (loaded once, scaled to
        # match each entity's actual hitbox size)
        self.player_image = self.load_image_safe(IMAGE_PLAYER, size=PLAYER_SIZE)
        self.goal_image = self.load_image_safe(IMAGE_GOAL, size=GOAL_SIZE)
        self.capsicum_image = self.load_image_safe(IMAGE_CAPSICUM, size=CAPSICUM_SIZE)
        self.nanny_image = self.load_image_safe(IMAGE_NANNY, size=NANNY_SIZE)
        self.mom_image = self.load_image_safe(IMAGE_MOM, size=MOM_SIZE)
        self.random_obstacle_image = self.load_image_safe(IMAGE_RANDOM_OBSTACLE, size=RANDOM_OBSTACLE_SIZE)

        self.state = STATE_START
        self.full_reset()
        self.start_music()

    # ---------------- SETUP / RESET ----------------
    def full_reset(self):
        self.lives = MAX_LIVES
        self.level_number = 1
        self.player = Player()
        self.player.image = self.player_image
        self.pending_life_loss = False
        self.level_complete_timer = 0
        self.load_level(self.level_number)

    def load_level(self, level_number):
        maze.set_level(level_number)
        self.goal = build_goal(level_number)
        self.goal.image = self.goal_image
        self.obstacles = build_obstacles(level_number)
        for obstacle in self.obstacles:
            if obstacle.__class__.__name__ == "Capsicum":
                obstacle.image = self.capsicum_image
            elif obstacle.__class__.__name__ == "NannyObstacle":
                obstacle.image = self.nanny_image
            elif obstacle.__class__.__name__ == "MomObstacle":
                obstacle.image = self.mom_image
            elif obstacle.__class__.__name__ == "RandomObstacle":
                obstacle.image = self.random_obstacle_image
        self.player.respawn(pygame.time.get_ticks(), LEVEL_START_INVULNERABLE_MS)
        self.reposition_obstacles_away_from_player()

    def load_image_safe(self, path, max_height=None, size=None):
        if not os.path.exists(path):
            print(f"[image] '{path}' not found — using placeholder shape instead.")
            return None
        image = pygame.image.load(path).convert_alpha()
        if size:
            # Sprites are scaled to their exact gameplay hitbox size,
            # regardless of the source image's resolution/aspect ratio.
            image = pygame.transform.smoothscale(image, (size, size))
        elif max_height:
            scale = max_height / image.get_height()
            new_size = (int(image.get_width() * scale), max_height)
            image = pygame.transform.smoothscale(image, new_size)
        return image

    def start_music(self):
        self.sound_manager.play_music(MUSIC_THEME)

    # ---------------- INPUT ----------------
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_RETURN:
                    if self.state == STATE_START:
                        self.state = STATE_PLAYING
                    elif self.state == STATE_MEME:
                        self.resolve_meme()

                if event.key == pygame.K_r:
                    if self.state in (STATE_GAME_OVER, STATE_ALL_COMPLETE):
                        self.full_reset()
                        self.state = STATE_START

        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            self.player.handle_movement(keys)

    # ---------------- UPDATE ----------------
    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state == STATE_PLAYING:
            self.goal.update()
            for obstacle in self.obstacles:
                if obstacle.__class__.__name__ == "MomObstacle":
                    obstacle.update(self.player.rect)
                else:
                    obstacle.update()

            if not self.player.is_invulnerable(current_time):
                self.check_collisions(current_time)

            if self.player.rect.colliderect(self.goal.rect):
                self.on_level_complete(current_time)

        elif self.state == STATE_LEVEL_COMPLETE:
            if current_time >= self.level_complete_timer:
                self.advance_level()

    def check_collisions(self, current_time):
        for obstacle in self.obstacles:
            if self.player.rect.colliderect(obstacle.rect):
                self.sound_manager.play("hit")
                if getattr(obstacle, "meme_on_hit", False):
                    self.state = STATE_MEME
                    meme_key = getattr(obstacle, "meme_key", "capsicum")
                    self.current_meme_key = meme_key
                    self.current_meme_caption = random.choice(MEME_CAPTIONS[meme_key])
                    self.sound_manager.play("meme")
                else:
                    self.apply_life_loss(current_time)
                return  # only process one hit per frame

    def resolve_meme(self):
        current_time = pygame.time.get_ticks()
        self.apply_life_loss(current_time)
        if self.state != STATE_GAME_OVER:
            self.state = STATE_PLAYING

    def apply_life_loss(self, current_time):
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_GAME_OVER
            self.sound_manager.play("game_over")
        else:
            self.player.respawn(current_time)
            self.reposition_obstacles_away_from_player()

    def reposition_obstacles_away_from_player(self):
        """
        Whenever the player (re)spawns, teleport any obstacle that's
        already sitting on top of the spawn point elsewhere on the
        path - otherwise a life is lost the instant invulnerability
        wears off, with no real chance to react.
        """
        px, py = self.player.rect.center
        radius_sq = OBSTACLE_SPAWN_SAFE_RADIUS ** 2
        for obstacle in self.obstacles:
            ox, oy = obstacle.rect.center
            if (ox - px) ** 2 + (oy - py) ** 2 < radius_sq:
                margin = obstacle.rect.width // 2
                obstacle.rect.center = maze.random_walkable_point(
                    margin=margin, avoid=(px, py), avoid_radius=OBSTACLE_SPAWN_SAFE_RADIUS
                )

    def on_level_complete(self, current_time):
        self.sound_manager.play("level_complete")
        if self.level_number >= TOTAL_LEVELS:
            self.state = STATE_ALL_COMPLETE
            self.sound_manager.play("win")
        else:
            self.state = STATE_LEVEL_COMPLETE
            self.level_complete_timer = current_time + LEVEL_COMPLETE_PAUSE_MS

    def advance_level(self):
        self.level_number += 1
        self.load_level(self.level_number)
        self.state = STATE_PLAYING

    # ---------------- DRAW ----------------
    def draw(self):
        self.screen.fill(WHITE)

        if self.state == STATE_START:
            self.draw_start_screen()
        elif self.state in (STATE_PLAYING, STATE_MEME, STATE_LEVEL_COMPLETE):
            self.draw_gameplay()
            if self.state == STATE_MEME:
                self.draw_meme_overlay()
            elif self.state == STATE_LEVEL_COMPLETE:
                self.draw_center_text(
                    f"Level {self.level_number} Complete!", self.font_big, GREEN, 0
                )
        elif self.state == STATE_GAME_OVER:
            self.draw_center_text("GAME OVER", self.font_big, RED, -30)
            self.draw_center_text(
                f"Reached Level {self.level_number}", self.font_medium, BLACK, 20
            )
            self.draw_center_text("Press R to restart", self.font_medium, BLACK, 60)
        elif self.state == STATE_ALL_COMPLETE:
            self.draw_center_text("YOU REACHED NANAKO!", self.font_big, GREEN, -30)
            self.draw_center_text(f"You beat all {TOTAL_LEVELS} levels!", self.font_medium, BLACK, 20)
            self.draw_center_text("Press R to play again", self.font_medium, BLACK, 60)

        pygame.display.flip()

    def draw_start_screen(self):
        if self.start_character_image:
            img_rect = self.start_character_image.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 190)
            )
            self.screen.blit(self.start_character_image, img_rect)
        self.draw_center_text("SHINCHAN ARENA RUNNER", self.font_big, BLACK, 0)
        self.draw_center_text("Press ENTER to start", self.font_medium, BLACK, 60)
        self.draw_center_text(
            "Arrows or WASD to move  |  Reach Nanako, avoid everything else",
            self.font_small, BLACK, 100
        )

    def draw_gameplay(self):
        maze.draw(self.screen)
        self.goal.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.player.draw(self.screen, pygame.time.get_ticks())
        self.draw_hud()

    def draw_hud(self):
        level_surf = self.font_medium.render(f"Level {self.level_number}/{TOTAL_LEVELS}", True, BLACK)
        lives_surf = self.font_medium.render(f"Lives: {self.lives}", True, BLACK)
        self.screen.blit(level_surf, (20, 20))
        self.screen.blit(lives_surf, (20, 55))

    def draw_meme_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(210)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        meme_image = self.meme_images.get(self.current_meme_key)
        if meme_image:
            img_rect = meme_image.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)
            )
            self.screen.blit(meme_image, img_rect)
        else:
            placeholder_rect = pygame.Rect(0, 0, 300, 180)
            placeholder_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
            pygame.draw.rect(self.screen, WHITE, placeholder_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, placeholder_rect, width=2, border_radius=10)
            no_img_surf = self.font_small.render("[ meme image goes here ]", True, BLACK)
            no_img_rect = no_img_surf.get_rect(center=placeholder_rect.center)
            self.screen.blit(no_img_surf, no_img_rect)

        lines = self.current_meme_caption.split("\n")
        for i, line in enumerate(lines):
            self.draw_center_text(line, self.font_medium, WHITE, 100 + i * 32)
        self.draw_center_text("Press ENTER to continue", self.font_small, WHITE, 180)

    def draw_center_text(self, text, font, color, y_offset):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        self.screen.blit(surf, rect)

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    Game().run()
