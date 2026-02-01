import arcade
import os
import random


class SoundManager:
    def __init__(self) -> None:
        self.toss_sounds = []
        self.landing_sounds = []

        self.gold_toss_sounds = []
        self.gold_landing_sounds = []

        self._last_played_bronze_toss = None
        self._last_played_bronze_land = None
        self._last_played_gold_toss = None
        self._last_played_gold_land = None

    def load_all(self) -> None:
        print("--- Loading Bronze/Silver Sounds ---")
        self._load_sounds_from_dir("view/sounds/silver_and_bronze_sounds/tossing", self.toss_sounds)
        self._load_sounds_from_dir("view/sounds/silver_and_bronze_sounds/landing", self.landing_sounds)

        print("--- Loading Gold Sounds ---")
        self._load_sounds_from_dir("view/sounds/gold_sounds/tossing", self.gold_toss_sounds)
        self._load_sounds_from_dir("view/sounds/gold_sounds/landing", self.gold_landing_sounds)

        print(f"Bronze/Silver Toss: {len(self.toss_sounds)}")
        print(f"Bronze/Silver Land: {len(self.landing_sounds)}")
        print(f"Gold Toss: {len(self.gold_toss_sounds)}")
        print(f"Gold Land: {len(self.gold_landing_sounds)}")

    def _load_sounds_from_dir(self, directory_path: str, target_list: list) -> None:
        if not os.path.exists(directory_path):
            print(f"Warning: Folder not found: {directory_path}")
            return

        files = sorted(os.listdir(directory_path))
        count = 0
        for f in files:
            if f.endswith(".mp3") or f.endswith(".wav"):
                sound_path = os.path.join(directory_path, f)
                target_list.append(arcade.load_sound(sound_path))
                count += 1
        print(f"  -> Loaded {count} files from {os.path.basename(directory_path)}")

    def play_toss(self, is_gold: bool = False) -> None:
        if is_gold:
            sound = self._pick_sound(self.gold_toss_sounds, self._last_played_gold_toss)
            self._last_played_gold_toss = sound
        else:
            sound = self._pick_sound(self.toss_sounds, self._last_played_bronze_toss)
            self._last_played_bronze_toss = sound

        if sound:
            arcade.play_sound(sound)

    def play_land(self, is_gold: bool = False) -> None:
        if is_gold:
            sound = self._pick_sound(self.gold_landing_sounds, self._last_played_gold_land)
            self._last_played_gold_land = sound
        else:
            sound = self._pick_sound(self.landing_sounds, self._last_played_bronze_land)
            self._last_played_bronze_land = sound

        if sound:
            arcade.play_sound(sound)

    def _pick_sound(self, pool: list, last_sound: any) -> any:
        if not pool:
            return None

        if len(pool) == 1:
            return pool[0]

        candidates = [s for s in pool if s != last_sound]

        if not candidates:
            return random.choice(pool)

        return random.choice(candidates)