import arcade

from logic.controllers.ui_controller import UIController
from logic.controllers.game_controller import GameController
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Incremental Coin Game"
PANEL_WIDTH = 500


class GameWindow(arcade.Window):
    def __init__(self, asset_manager: AssetManager, sound_manager: SoundManager) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, update_rate=1 / 60)

        arcade.set_background_color(arcade.color.AMAZON)

        self.asset_manager = asset_manager
        self.sound_manager = sound_manager

        # Границы игрового поля (без UI)
        self.world_width = SCREEN_WIDTH - PANEL_WIDTH
        self.world_height = SCREEN_HEIGHT

        self.game = GameController(
            asset_manager=self.asset_manager,
            sound_manager=self.sound_manager,
            world_width=self.world_width,
            world_height=self.world_height,
        )

        self.ui = UIController(
            asset_manager=self.asset_manager,
            panel_x=self.world_width,
            panel_width=PANEL_WIDTH,
            panel_height=SCREEN_HEIGHT,
        )

    def run(self) -> None:
        arcade.run()

    def on_update(self, delta_time: float) -> None:
        self.game.update(delta_time)
        self.ui.update(self.game.balance.get())

    def on_draw(self) -> None:
        self.clear()

        # (позже добавим draw монет)
        self.game.draw()

        self.ui.draw(balance_value=self.game.balance.get())

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        self.ui.on_mouse_press(x, y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        upgrade_id = self.ui.on_mouse_release(x, y)
        if upgrade_id:
            self._handle_upgrade(upgrade_id)

    def _handle_upgrade(self, upgrade_id: str) -> None:
        if upgrade_id == "finish_game":
            arcade.close_window()
            return

        self.game.try_buy_upgrade(upgrade_id)