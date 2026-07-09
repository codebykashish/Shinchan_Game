import os
import subprocess

import cv2
import imageio_ffmpeg
import pygame


def extract_audio(video_path):
    """
    Pulls the audio track out of an mp4 into a standalone .ogg file
    (cached next to the video) so pygame.mixer.music can loop it —
    pygame can't play audio straight out of an mp4 container.
    """
    audio_path = os.path.splitext(video_path)[0] + "_audio.ogg"
    if os.path.exists(audio_path) and os.path.getmtime(audio_path) >= os.path.getmtime(video_path):
        return audio_path

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    try:
        subprocess.run(
            [ffmpeg_exe, "-y", "-i", video_path, "-vn", "-acodec", "libvorbis", audio_path],
            check=True, capture_output=True,
        )
        return audio_path
    except Exception as e:
        print(f"[video] couldn't extract audio from '{video_path}' ({e})")
        return None


class VideoPlayer:
    """
    Decodes an mp4 with OpenCV and hands back pygame surfaces, looping
    forever. pygame itself has no video codec, so this is the bridge.
    """

    def __init__(self, path, size):
        self.size = size
        self.cap = None
        self.frame_delay_ms = 1000 / 30
        self.next_frame_time = 0
        self.current_surface = None

        if os.path.exists(path):
            self.cap = cv2.VideoCapture(path)
            fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.frame_delay_ms = 1000 / fps
        else:
            print(f"[video] '{path}' not found — start screen will show a plain background instead.")

    def update(self, current_time_ms):
        if not self.cap:
            return
        if self.current_surface is not None and current_time_ms < self.next_frame_time:
            return

        ok, frame = self.cap.read()
        if not ok:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = self.cap.read()
            if not ok:
                return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, self.size)
        self.current_surface = pygame.image.frombuffer(frame.tobytes(), self.size, "RGB")
        self.next_frame_time = current_time_ms + self.frame_delay_ms

    def get_surface(self):
        return self.current_surface
