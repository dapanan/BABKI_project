from __future__ import annotations
import os
import arcade


class AssetManager:
    def __init__(self) -> None:
        self._loaded = False

        # Словари для спрайтов. Используем одни и те же для бронзы и золота для примера,
        # пока неь отдельных папок для бронзы.
        self.coin_sprites: dict[str, list[arcade.Texture] | arcade.Texture] = {}

    def load_all(self) -> None:
        self._load_coin_sprites("gold_coin")
        self._loaded = True

    def _load_coin_sprites(self, folder_name: str) -> None:
        base = os.path.join("view", "sprites", folder_name)
        if not os.path.exists(base):
            print(f"Warning: Folder {base} not found!")
            return

        def load_dir(name: str) -> list[arcade.Texture]:
            path = os.path.join(base, name)
            if not os.path.exists(path): return []
            files = sorted(os.listdir(path))
            return [
                arcade.load_texture(os.path.join(path, f))
                for f in files if f.endswith(".png")
            ]

        self.coin_sprites = {
            "up": load_dir("up"),
            "down": load_dir("down"),
            "left": load_dir("left"),
            "right": load_dir("right"),
            "heads": arcade.load_texture(os.path.join(base, "heads", "gold_heads.png")),
            "tails": arcade.load_texture(os.path.join(base, "tails", "gold_tails.png")),
        }

    def is_loaded(self) -> bool:
        return self._loaded