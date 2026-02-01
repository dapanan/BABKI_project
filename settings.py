class Settings:
    def __init__(self):
        self.music_volume = 0.4
        self.sfx_volume = 0.6
        self.fullscreen = False

class Music:
    def __init__(self, settings):
        self.settings = settings
        self.player = pyglet.media.Player()

    def update(self):
        self.player.volume = self.settings.music_volume
