import arcade

from logic.economy.balance import Balance
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager


class GameController:
    def __init__(
        self,
        asset_manager: AssetManager,
        sound_manager: SoundManager,
        world_width: int,
        world_height: int,
    ) -> None:
        self.asset_manager = asset_manager
        self.sound_manager = sound_manager
        self.world_width = world_width
        self.world_height = world_height

        self.balance = Balance()

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        # линия-разделитель
        arcade.draw_line(self.world_width, 0, self.world_width, self.world_height, arcade.color.LIGHT_GRAY, 2)

    def try_buy_upgrade(self, upgrade_id: str) -> bool:
        # пока заглушка
        return False
