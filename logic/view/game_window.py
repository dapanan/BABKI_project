import arcade

from logic.controllers.ui_controller import UIController
from logic.controllers.game_controller import GameController
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
from logic.controllers.ui_controller import SettingsMenu



SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Incremental Coin Game"
PANEL_WIDTH = 500


class GameWindow(arcade.Window):
    def __init__(
        self,
        asset_manager: AssetManager,
        sound_manager: SoundManager,
    ) -> None:
        super().__init__(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            SCREEN_TITLE,
            update_rate=1 / 60,

        )


        self.mode = "game"
        self.music_volume = 0.4
        self.settings_menu = SettingsMenu(
            x=600,
            y=200,
            width=400,
            height=400,
            music_manager=self.music_manager
        )
        arcade.set_background_color(arcade.color.AMAZON)

        self.asset_manager = asset_manager
        self.sound_manager = sound_manager

        self.world_width = SCREEN_WIDTH - PANEL_WIDTH
        self.world_height = SCREEN_HEIGHT

        self.game = GameController(
            asset_manager=self.asset_manager,
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

    def on_draw(self):
        self.clear()

        if self.mode == "game":
            self.game.draw()
            self.ui.draw(balance_value=self.game.balance.get())

        elif self.mode == "settings":
            self.draw_settings()



    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        self.game.on_mouse_press(x, y)
        if self.settings_menu.visible:
            self.settings_menu.on_mouse_press(x, y, button)
            return


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
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            if self.mode == "game":
                self.mode = "settings"
            else:
                self.mode = "game"


    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.window.settings_view)

    def draw_settings(self):
        arcade.draw_text(
            "SETTINGS",
            self.width // 2,
            self.height - 100,
            arcade.color.WHITE,
            40,
            anchor_x="center"
    )

        arcade.draw_text(
            f"Music volume: {int(self.music_volume * 100)}%",
            self.width // 2,
            self.height // 2,
            arcade.color.WHITE,
            24,
            anchor_x="center"
    )

        arcade.draw_text(
            "ESC — back",
            self.width // 2,
            100,
            arcade.color.GRAY,
            20,
            anchor_x="center"
    )
