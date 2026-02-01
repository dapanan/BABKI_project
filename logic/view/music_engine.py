import pyglet
import os
import random
import settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_FOLDER = os.path.join(BASE_DIR, "music")

class Music:
    def __init__(self, settings):
        self.settings = settings
        self.player = pyglet.media.Player()
        self.player.volume = self.settings.music_volume

        # путь к музыке
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MUSIC_FOLDER = os.path.join(BASE_DIR, "music")
        if not os.path.isdir(MUSIC_FOLDER):
            raise FileNotFoundError(f"Папка с музыкой не найдена: {MUSIC_FOLDER}")

        self.music_list = [
            os.path.join(MUSIC_FOLDER, f)
            for f in os.listdir(MUSIC_FOLDER)
            if f.lower().endswith((".mp3", ".wav", ".ogg"))
        ]

        if not self.music_list:
            raise FileNotFoundError("В папке music нет аудиофайлов!")

    def set_volume(self, value: float):
        self.player.volume = value

    def play_next_song(self):
        import random, pyglet
        track = random.choice(self.music_list)
        source = pyglet.media.load(track, streaming=True)
        self.player.queue(source)
        self.player.play()

        @self.player.event
        def on_eos():
            self.play_next_song()

    def start(self):
        self.play_next_song()

    def update(self):
        self.set_volume(self.settings.music_volume)
