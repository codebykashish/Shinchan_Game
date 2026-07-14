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
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    WHITE, BLACK, GREEN, RED, YELLOW, GRAY,
    MAX_LIVES, LEVEL_COMPLETE_PAUSE_MS, LEVEL_START_INVULNERABLE_MS,
    PLAYER_SIZE, GOAL_SIZE, CAPSICUM_SIZE, NANNY_SIZE, MOM_SIZE, RANDOM_OBSTACLE_SIZE,
    OBSTACLE_SPAWN_SAFE_RADIUS,
    VIDEO_START_SCREEN,
    IMAGE_START_SCREEN_CHARACTER, IMAGE_PLAYER, IMAGE_GOAL,
    IMAGE_CAPSICUM, IMAGE_NANNY, IMAGE_MOM, IMAGE_RANDOM_OBSTACLE,
    IMAGE_MEME_CAPSICUM, IMAGE_MEME_MOM, IMAGE_MEME_NANNY,
    IMAGE_GAME_OVER_CHARACTER,
    SOUND_START, SOUND_CAUGHT, SOUND_HIT, SOUND_LEVEL_COMPLETE, SOUND_GAME_OVER,
    SOUND_WIN, SOUND_MEME,
)
import maze
from player import Player
from levels import build_goal, build_obstacles, TOTAL_LEVELS
from sound_manager import SoundManager
from video_player import VideoPlayer, extract_audio

# ---- States ----
STATE_START = "start"
STATE_PLAYING = "playing"
STATE_MEME = "meme"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"
STATE_ALL_COMPLETE = "all_complete"

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

        self.start_video = VideoPlayer(VIDEO_START_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_video_audio = extract_audio(VIDEO_START_SCREEN)

        self.start_character_image = self.load_image_safe(
            IMAGE_START_SCREEN_CHARACTER, max_height=220
        )
        self.meme_images = {
            "capsicum": self.load_image_safe(IMAGE_MEME_CAPSICUM, max_height=250),
            "mom": self.load_image_safe(IMAGE_MEME_MOM, max_height=250),
            "nanny": self.load_image_safe(IMAGE_MEME_NANNY, max_height=250),
        }
        self.game_over_image = self.load_image_cover(
            IMAGE_GAME_OVER_CHARACTER, (SCREEN_WIDTH, SCREEN_HEIGHT)
        )

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

    def load_image_cover(self, path, target_size):
        """Load an image scaled and center-cropped to fully cover target_size
        (like CSS background-size: cover), preserving its aspect ratio."""
        if not os.path.exists(path):
            print(f"[image] '{path}' not found — using placeholder shape instead.")
            return None
        image = pygame.image.load(path).convert_alpha()
        target_w, target_h = target_size
        scale = max(target_w / image.get_width(), target_h / image.get_height())
        new_size = (int(image.get_width() * scale) + 1, int(image.get_height() * scale) + 1)
        image = pygame.transform.smoothscale(image, new_size)
        crop_x = (new_size[0] - target_w) // 2
        crop_y = (new_size[1] - target_h) // 2
        return image.subsurface(pygame.Rect(crop_x, crop_y, target_w, target_h)).copy()

    def start_music(self):
        if self.start_video_audio:
            self.sound_manager.play_music(self.start_video_audio)

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
                        self.sound_manager.play_music(SOUND_START)
                    elif self.state == STATE_MEME:
                        self.resolve_meme()

                if event.key == pygame.K_r:
                    if self.state in (STATE_GAME_OVER, STATE_ALL_COMPLETE):
                        self.full_reset()
                        self.state = STATE_START
                        self.start_music()

        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            self.player.handle_movement(keys)

    # ---------------- UPDATE ----------------
    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state == STATE_START:
            self.start_video.update(current_time)

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
                self.sound_manager.play_music(SOUND_CAUGHT)
                if getattr(obstacle, "meme_on_hit", False):
                    self.state = STATE_MEME
                    meme_key = getattr(obstacle, "meme_key", "capsicum")
                    self.current_meme_key = meme_key
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
            self.sound_manager.play_music(SOUND_START)

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
            if self.game_over_image:
                self.screen.blit(self.game_over_image, (0, 0))
            else:
                self.screen.fill(BLACK)

            strip_rect = pygame.Rect(0, SCREEN_HEIGHT // 2 - 60, SCREEN_WIDTH, 140)
            strip = pygame.Surface(strip_rect.size, pygame.SRCALPHA)
            strip.fill((0, 0, 0, 165))
            self.screen.blit(strip, strip_rect)

            self.draw_center_text("GAME OVER", self.font_big, WHITE, -30)
            self.draw_center_text(
                f"Reached Level {self.level_number}", self.font_medium, WHITE, 20
            )
            self.draw_center_text("Press R to restart", self.font_medium, WHITE, 60)
        elif self.state == STATE_ALL_COMPLETE:
            self.draw_center_text("YOU REACHED NANAKO!", self.font_big, GREEN, -30)
            self.draw_center_text(f"You beat all {TOTAL_LEVELS} levels!", self.font_medium, BLACK, 20)
            self.draw_center_text("Press R to play again", self.font_medium, BLACK, 60)

        pygame.display.flip()

    def draw_start_screen(self):
        video_frame = self.start_video.get_surface()
        if video_frame:
            self.screen.blit(video_frame, (0, 0))

        if self.start_character_image:
            img_rect = self.start_character_image.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 190)
            )
            self.screen.blit(self.start_character_image, img_rect)

        self.draw_outlined_text(
            "SHINCHAN ARENA RUNNER", self.font_big, YELLOW, BLACK,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), outline_width=3,
        )

        pulse = 200 + int(55 * abs((pygame.time.get_ticks() % 1000) / 500 - 1))
        self.draw_outlined_text(
            "Press ENTER to start", self.font_medium, (255, pulse, pulse), BLACK,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60), outline_width=2,
        )

        hint_text = "Arrows or WASD to move  |  Reach Nanako, avoid everything else"
        hint_surf = self.font_small.render(hint_text, True, WHITE)
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        pill_rect = hint_rect.inflate(28, 16)
        pill = pygame.Surface(pill_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(pill, (0, 0, 0, 150), pill.get_rect(), border_radius=12)
        self.screen.blit(pill, pill_rect)
        self.screen.blit(hint_surf, hint_rect)

    def draw_outlined_text(self, text, font, fill_color, outline_color, center, outline_width=2):
        outline_surf = font.render(text, True, outline_color)
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx or dy:
                    self.screen.blit(outline_surf, outline_surf.get_rect(center=(center[0] + dx, center[1] + dy)))
        fill_surf = font.render(text, True, fill_color)
        self.screen.blit(fill_surf, fill_surf.get_rect(center=center))

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
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        meme_image = self.meme_images.get(self.current_meme_key)
        card_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
        content_size = meme_image.get_size() if meme_image else (300, 180)
        content_bottom = card_center[1] + content_size[1] // 2

        if meme_image:
            img_rect = meme_image.get_rect(center=card_center)
            self.screen.blit(meme_image, img_rect)
        else:
            no_img_surf = self.font_small.render("[ meme image goes here ]", True, WHITE)
            no_img_rect = no_img_surf.get_rect(center=card_center)
            self.screen.blit(no_img_surf, no_img_rect)

        lives_text = f"Lives left: {self.lives}"
        self.draw_center_text(lives_text, self.font_medium, YELLOW, content_bottom - SCREEN_HEIGHT // 2 + 30)

        pulse = 180 + int(60 * abs((pygame.time.get_ticks() % 1000) / 500 - 1))
        self.draw_center_text(
            "Press ENTER to continue", self.font_small, (pulse, pulse, pulse),
            content_bottom - SCREEN_HEIGHT // 2 + 65,
        )

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
