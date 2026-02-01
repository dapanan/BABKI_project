from application import GameWindow
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager


def main():
    asset_manager = AssetManager()
    asset_manager.load_all()

    sound_manager = SoundManager()
    sound_manager.load_all()

    window = GameWindow(asset_manager, sound_manager)
    window.run()


if __name__ == "__main__":
    main()
