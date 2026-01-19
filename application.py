import arcade
import math

from logic.controllers.ui_controller import UIController
from logic.controllers.game_controller import GameController
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager

# --- АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ РАЗРЕШЕНИЯ ---
# Получаем размер монитора пользователя (для 4K, для ноутбука и т.д.)
# Это автоматически даст тебе 3840x2160 на 4К мониторе
screen_width, screen_height = arcade.get_display_size()

# Вычисляем коэффициент масштабирования.
# Базовое разрешение 1080p (высота). Если у тебя 2160 (4К), scale будет 2.0.
scale_factor = screen_height / 1080.0
# Ограничиваем масштаб снизу до 1.0 (чтобы на маленьких экранах не было гигантских кнопок)
scale_factor = max(scale_factor, 1.0)

PANEL_WIDTH = int(500 * scale_factor)  # Ширина панели UI тоже масштабируется
SCREEN_TITLE = "Incremental Coin Game"


class GameWindow(arcade.Window):
    def __init__(self) -> None:
        # --- НАСТРОЙКИ ОКНА ---
        super().__init__(
            width=screen_width,
            height=screen_height,
            title=SCREEN_TITLE,
            fullscreen=True,
            resizable=False,
            # ВАЖНО: Ставим очень высокую частоту (1/1000).
            # Это снимет ограничение 60 FPS и даст работать на 144 Гц и выше.
            # Игра не "ускорится" (физика зависит от delta_time), но станет плавнее.
            update_rate=1 / 1000,
            draw_rate=1 / 1000,
        )

        # Фон
        self.background_color = arcade.color.WHITE

        self.asset_manager = AssetManager()
        self.asset_manager.load_all()

        self.sound_manager = SoundManager()
        self.sound_manager.load_all()

        # Параметры мира
        self.world_width = screen_width - PANEL_WIDTH
        self.world_height = screen_height

        self.asset_manager.load_ui_assets()

        import pyglet.font
        import os

        font_dir = "view/ui/fonts"
        if not os.path.isabs(font_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            font_dir = os.path.join(script_dir, font_dir)

        if os.path.exists(font_dir):
            pyglet.font.add_directory(font_dir)
            print(f"DEBUG: Pyglet font directory added: {font_dir}")
        # Передаем масштаб в UI
        self.ui = UIController(
            panel_x=self.world_width,
            panel_width=PANEL_WIDTH,
            panel_height=screen_height,
            ui_assets=self.asset_manager.ui_assets,
            scale_factor=scale_factor
        )

        self.game = GameController(
            asset_manager=self.asset_manager,
            ui_controller=self.ui,
            sound_manager=self.sound_manager,
            world_width=self.world_width,      # <--- Передаем реальную ширину
            world_height=self.world_height,    # <--- Передаем реальную высоту
            scale_factor=scale_factor         # <--- Передаем масштаб для монеток
        )

        print(f"--- SYSTEM INFO ---")
        print(f"Resolution: {screen_width}x{screen_height}")
        print(f"Scale Factor: {scale_factor:.2f}x")
        print(f"UI Panel Width: {PANEL_WIDTH}px")
        print(f"FPS Cap: Uncapped (Monitor Limit)")

    def on_update(self, delta_time: float) -> None:
        self.game.update(delta_time)
        self.ui.update(self.game.balance.get())

    def on_draw(self) -> None:
        self.clear()
        self.game.draw()
        self.ui.draw(balance_value=self.game.balance.get())

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.game.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.game.on_mouse_press_rmb(x, y)
            return

        if button != arcade.MOUSE_BUTTON_LEFT:
            return

        if x > self.world_width:
            self.ui.on_mouse_press(x, y)
        else:
            self.game.on_mouse_press(x, y, button)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.game.on_mouse_release_rmb(x, y)
            return

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

        self.game.try_buy_upgrade(upgrade_id)

    # --- ДОБАВЛЯЕМ ПОДДЕРЖКУ КОЛЕСИКА ---
    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        if x > self.world_width:
            self.ui.on_mouse_scroll(x, y, scroll_x, scroll_y)