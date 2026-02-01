import arcade
from logic.controllers.ui_controller import UIController
from logic.controllers.game_controller import GameController

PANEL_WIDTH = 500
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


class GameView(arcade.View):
    def __init__(self, asset_manager, sound_manager):
        super().__init__()

        self.asset_manager = asset_manager
        self.sound_manager = sound_manager

        arcade.set_background_color(arcade.color.AMAZON)

        self.world_width = SCREEN_WIDTH - PANEL_WIDTH

        self.game = GameController(
            asset_manager=self.asset_manager
        )

        self.ui = UIController(
            asset_manager=self.asset_manager,
            panel_x=self.world_width,
            panel_width=PANEL_WIDTH,
            panel_height=SCREEN_HEIGHT,
        )

    def on_update(self, delta_time):
        self.game.update(delta_time)
        self.ui.update(self.game.balance.get())

    def on_draw(self):
        self.clear()
        self.game.draw()
        self.ui.draw(balance_value=self.game.balance.get())

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.game.on_mouse_press(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        upgrade_id = self.ui.on_mouse_release(x, y)
        if upgrade_id:
            self._handle_upgrade(upgrade_id)

    def _handle_upgrade(self, upgrade_id):
        if upgrade_id == "finish_game":
            arcade.close_window()
            return

        self.game.try_buy_upgrade(upgrade_id)
