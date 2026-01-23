import arcade
import os
import random


class SoundManager:
    def __init__(self) -> None:
        # Списки для бронзы
        self.bronze_toss_sounds = []
        self.bronze_landing_sounds = []

        # Списки для серебра
        self.silver_toss_sounds = []
        self.silver_landing_sounds = []

        # Списки для золота
        self.gold_toss_sounds = []
        self.gold_landing_sounds = []

        # История проигранных звуков
        self._last_bronze_toss = None
        self._last_bronze_land = None
        self._last_silver_toss = None
        self._last_silver_land = None
        self._last_gold_toss = None
        self._last_gold_land = None
        self.beetle_dead_sound = None

    def load_all(self) -> None:
        base_sound_dir = "view/sounds"

        print("--- Loading Bronze Sounds ---")
        # Пробуем сначала папку bronze_sounds, если нет - смотрим в silver_and_bronze_sounds
        bronze_paths = [
            os.path.join(base_sound_dir, "bronze_sounds/tossing"),
            os.path.join(base_sound_dir, "silver_and_bronze_sounds/tossing")
        ]
        bronze_paths_land = [
            os.path.join(base_sound_dir, "bronze_sounds/landing"),
            os.path.join(base_sound_dir, "silver_and_bronze_sounds/landing")
        ]

        self._load_sounds_from_dir(bronze_paths, self.bronze_toss_sounds, "Bronze Toss")
        self._load_sounds_from_dir(bronze_paths_land, self.bronze_landing_sounds, "Bronze Land")

        print("--- Loading Silver Sounds ---")
        # Пробуем сначала папку silver_sounds, если нет - смотрим в silver_and_bronze_sounds
        silver_paths = [
            os.path.join(base_sound_dir, "silver_sounds/tossing"),
            os.path.join(base_sound_dir, "silver_and_bronze_sounds/tossing")
        ]
        silver_paths_land = [
            os.path.join(base_sound_dir, "silver_sounds/landing"),
            os.path.join(base_sound_dir, "silver_and_bronze_sounds/landing")
        ]

        self._load_sounds_from_dir(silver_paths, self.silver_toss_sounds, "Silver Toss")
        self._load_sounds_from_dir(silver_paths_land, self.silver_landing_sounds, "Silver Land")

        print("--- Loading Gold Sounds ---")
        self._load_sounds_from_dir(
            [os.path.join(base_sound_dir, "gold_sounds/tossing")],
            self.gold_toss_sounds, "Gold Toss"
        )
        self._load_sounds_from_dir(
            [os.path.join(base_sound_dir, "gold_sounds/landing")],
            self.gold_landing_sounds, "Gold Land"
        )

        print(f"Bronze Toss: {len(self.bronze_toss_sounds)}")
        print(f"Bronze Land: {len(self.bronze_landing_sounds)}")
        print(f"Silver Toss: {len(self.silver_toss_sounds)}")
        print(f"Silver Land: {len(self.silver_landing_sounds)}")
        print(f"Gold Toss: {len(self.gold_toss_sounds)}")
        print(f"Gold Land: {len(self.gold_landing_sounds)}")
        print("--- Loading Beetle Sound ---")

        # Формируем правильный путь: view/sounds/beetle/beetle_dead.mp3
        beetle_sound_dir = os.path.join(base_sound_dir, "beetle")
        beetle_sound_path = os.path.join(beetle_sound_dir, "beetle_dead.mp3")

        if os.path.exists(beetle_sound_path):
            self.beetle_dead_sound = arcade.load_sound(beetle_sound_path)
            print("  -> Loaded Beetle sound")
        else:
            print(f"  -> WARNING: Beetle sound not found at {beetle_sound_path}")

    def _load_sounds_from_dir(self, directory_paths: list[str], target_list: list, label: str) -> None:
        """Ищет звуки в первой доступной папке из списка directory_paths"""
        for directory_path in directory_paths:
            if os.path.exists(directory_path):
                files = sorted(os.listdir(directory_path))
                count = 0
                for f in files:
                    if f.endswith(".mp3") or f.endswith(".wav"):
                        sound_path = os.path.join(directory_path, f)
                        target_list.append(arcade.load_sound(sound_path))
                        count += 1

                if count > 0:
                    print(f"  -> Loaded {count} {label} from {os.path.basename(directory_path)}")
                    return  # Успешно загрузили, прерываем поиск

        # Если ничего не нашлось в подходящих папках
        print(f"  -> WARNING: No sounds found for {label}!")

    def play_toss(self, coin_type: str) -> None:
        if coin_type == "gold":
            sound = self._pick_sound(self.gold_toss_sounds, self._last_gold_toss)
            self._last_gold_toss = sound
        elif coin_type == "silver":
            sound = self._pick_sound(self.silver_toss_sounds, self._last_silver_toss)
            self._last_silver_toss = sound
        else:  # bronze
            sound = self._pick_sound(self.bronze_toss_sounds, self._last_bronze_toss)
            self._last_bronze_toss = sound

        if sound:
            arcade.play_sound(sound)

    def play_land(self, coin_type: str) -> None:
        if coin_type == "gold":
            sound = self._pick_sound(self.gold_landing_sounds, self._last_gold_land)
            self._last_gold_land = sound
        elif coin_type == "silver":
            sound = self._pick_sound(self.silver_landing_sounds, self._last_silver_land)
            self._last_silver_land = sound
        else:  # bronze
            sound = self._pick_sound(self.bronze_landing_sounds, self._last_bronze_land)
            self._last_bronze_land = sound

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