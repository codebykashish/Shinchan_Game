import os
import pygame


class SoundManager:
    """
    Wraps sound/music playback so missing placeholder files never crash
    the game — it just prints a reminder instead.
    """

    def __init__(self):
        self.sounds = {}
        self.missing_warned = set()

    def load_sound(self, key, path):
        if os.path.exists(path):
            self.sounds[key] = pygame.mixer.Sound(path)
        else:
            self.sounds[key] = None

    def play(self, key):
        sound = self.sounds.get(key)
        if sound:
            sound.play()
        elif key not in self.missing_warned:
            print(f"[sound] '{key}' file not found — add it to assets/sounds/ to hear it.")
            self.missing_warned.add(key)

    def play_music(self, path, loop=True):
        if not os.path.exists(path):
            print(f"[music] '{path}' not found — add it to hear background music.")
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play(-1 if loop else 0)
        except pygame.error as e:
            print(f"[music] '{path}' couldn't be played ({e}) — is it a valid audio file?")
