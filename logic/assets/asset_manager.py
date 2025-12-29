from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class AssetPaths:
    root_view_dir: str = "view"
    sprites_dir: str = "view/sprites"
    sounds_dir: str = "view/sounds"
    ui_dir: str = "view/ui"


class AssetManager:
    def __init__(self) -> None:
        self.paths = AssetPaths()
        self._loaded = False

    def load_all(self) -> None:
        #подгрузим спрайты монет эльдара, звуки и т.д.
        self._loaded = True

    def is_loaded(self) -> bool:
        return self._loaded
