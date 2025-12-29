from logic.assets.asset_manager import AssetManager


class SoundManager:
    def __init__(self, asset_manager: AssetManager) -> None:
        self.asset_manager = asset_manager
        # загрузить arcade.Sound позже
        self._enabled = True

    def play_coin_land(self) -> None:
        if not self._enabled:
            return
        # arcade.play_sound(...) сюда нафигачим асмр звук
        pass

    def play_click(self) -> None:
        if not self._enabled:
            return
        pass

    def play_crit(self) -> None:
        if not self._enabled:
            return
        pass
