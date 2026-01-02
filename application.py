import arcade
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
from logic.controllers.game_controller import GameController
from logic.controllers.ui_controller import UIController

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Incremental Coin Game"
PANEL_WIDTH = 500


class GameWindow(arcade.Window):
    def __init__(self) -> None:
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            update_rate=1 / 60,
        )

        arcade.set_background_color(arcade.color.WHITE)

        self.asset_manager = AssetManager()
        self.asset_manager.load_all()

        self.sound_manager = SoundManager(self.asset_manager)

        self.world_width = SCREEN_WIDTH - PANEL_WIDTH
        self.world_height = SCREEN_HEIGHT

        # Сначала создаем UI
        self.ui = UIController(
            panel_x=self.world_width,
            panel_width=PANEL_WIDTH,
            panel_height=SCREEN_HEIGHT,
        )

        # Потом создаем Game, передавая туда ссылку на UI
        self.game = GameController(
            asset_manager=self.asset_manager,
            ui_controller=self.ui
        )

    def on_update(self, delta_time: float) -> None:
        self.game.update(delta_time)
        self.ui.update(self.game.balance.get())

    def on_draw(self) -> None:
        self.clear()
        self.game.draw()
        self.ui.draw(balance_value=self.game.balance.get())

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if x > self.world_width:
            self.ui.on_mouse_press(x, y)
        else:
            self.game.on_mouse_press(x, y)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if x > self.world_width:
            upgrade_id = self.ui.on_mouse_release(x, y)
            if upgrade_id:
                self._handle_upgrade(upgrade_id)

    def _handle_upgrade(self, upgrade_id: str) -> None:
        if upgrade_id == "finish_game":
            arcade.close_window()
            return

        # Теперь GameController сам обновляет UI внутри try_buy_upgrade
        self.game.try_buy_upgrade(upgrade_id)