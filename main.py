from application import GameWindow
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
import arcade

def main():
    asset_manager = AssetManager()
    sound_manager = SoundManager()

    window = GameWindow(asset_manager, sound_manager)
    arcade.run()

if __name__ == "__main__":
    main()
