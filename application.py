from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
from logic.view.game_window import GameWindow


class Application:
    def __init__(self) -> None:
        self.asset_manager = AssetManager()
        self.sound_manager = SoundManager(self.asset_manager)

        self.window = GameWindow(self.asset_manager, self.sound_manager)

    def run(self) -> None:
        self.asset_manager.load_all()
        self.window.run()