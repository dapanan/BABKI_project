import json
import os


SETTINGS_FILE = "settings.json"


class Settings:
    def __init__(self):
        self.music_volume = 0.4
        self.sound_volume = 0.6
        self.fullscreen = False

        self.load()

    def load(self):
        if not os.path.exists(SETTINGS_FILE):
            return

        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.music_volume = data.get("music_volume", self.music_volume)
            self.sound_volume = data.get("sound_volume", self.sound_volume)
            self.fullscreen = data.get("fullscreen", self.fullscreen)

        except Exception as e:
            print(f"[Settings] load error: {e}")

    def save(self):
        data = {
            "music_volume": self.music_volume,
            "sound_volume": self.sound_volume,
            "fullscreen": self.fullscreen,
        }

        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            print(f"[Settings] save error: {e}")
