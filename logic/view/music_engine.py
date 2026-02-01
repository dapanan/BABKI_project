import pyglet
import os
import random
import settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_FOLDER = os.path.join(BASE_DIR, "music")

class Music:
    def __init__(self):
        self.settings = settings
        self.music_list = [
            os.path.join(MUSIC_FOLDER, f)
            for f in os.listdir(MUSIC_FOLDER)
            if f.lower().endswith((".mp3", ".wav", ".ogg"))
        ]

        self.settings = settings
        self.player = pyglet.media.Player()
        self.player.volume = self.settings.music_volume
        self.player = pyglet.media.Player()

    def play_next_song(self):
        track = random.choice(self.music_list)
        source = pyglet.media.load(track, streaming=True)
        self.player.queue(source)
        self.player.volume = 0.4
        self.player.play()

        @self.player.event
        def on_eos():
            self.play_next_song()

    def set_volume(self, volume: float):
        self.player.volume = max(0.0, min(1.0, volume))
        self.settings.music_volume = self.player.volume
        self.settings.save()


    def get_volume(self):
        return self.player.volume

    def start(self):
        self.play_next_song()
