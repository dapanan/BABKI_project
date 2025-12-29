import arcade
from dataclasses import dataclass
from typing import Optional

from logic.assets.asset_manager import AssetManager


@dataclass
class _UiButtonStub:
    upgrade_id: str
    x: float
    y: float
    w: float
    h: float
    title: str


class UIController:
    def __init__(self, asset_manager: AssetManager, panel_x: int, panel_width: int, panel_height: int) -> None:
        self.asset_manager = asset_manager
        self.panel_x = panel_x
        self.panel_width = panel_width
        self.panel_height = panel_height

        pad = 16
        btn_h = 64
        btn_w = panel_width - pad * 2
        start_y = panel_height - 120

        self._buttons = [
            _UiButtonStub("buy_bronze_coin", panel_x + pad, start_y, btn_w, btn_h, "Купить бронзовую монету"),
            _UiButtonStub("gold_crit_upgrade", panel_x + pad, start_y - 84, btn_w, btn_h, "Крит для золота"),
            _UiButtonStub("finish_game", panel_x + pad, start_y - 168, btn_w, btn_h, "Закончить игру"),
        ]

        # какая кнопка сейчас нажата (для продавливания)
        self._pressed_id: Optional[str] = None

        # какая кнопка "зажата" именно мышью (чтобы отпускание работало правильно)
        self._pressed_down_id: Optional[str] = None

        # позже сюда привяжем логику стоимости
        self._enabled = {b.upgrade_id: True for b in self._buttons}

    def update(self, balance_value: int) -> None:
        #тут надо выставлять когда появятся стоимости — enabled/disabled
        pass

    def draw(self, balance_value: int) -> None:
        # фон панели
        arcade.draw_lrbt_rectangle_filled(
            self.panel_x,
            self.panel_x + self.panel_width,
            0,
            self.panel_height,
            arcade.color.WHITE_SMOKE
        )

        # заголовок и баланс
        arcade.draw_text("Апгрейды", self.panel_x + 16, self.panel_height - 40, arcade.color.BLACK, 20)
        arcade.draw_text(f"Баланс: {balance_value}", self.panel_x + 16, self.panel_height - 70, arcade.color.BLACK, 14)

        for b in self._buttons:
            enabled = self._enabled.get(b.upgrade_id, True)
            is_pressed = (self._pressed_id == b.upgrade_id)

            # продавливание: смещаем вниз
            y = b.y - (6 if is_pressed else 0)

            fill = arcade.color.LIGHT_GRAY if enabled else arcade.color.DARK_GRAY
            border = arcade.color.GRAY

            arcade.draw_lrbt_rectangle_filled(b.x, b.x + b.w, y, y + b.h, fill)
            arcade.draw_lrbt_rectangle_outline(b.x, b.x + b.w, y, y + b.h, border, 2)

            arcade.draw_text(b.title, b.x + 14, y + 22, arcade.color.BLACK, 13)

    def _hit_test(self, x: int, y: int) -> Optional[str]:
        for b in self._buttons:
            if b.x <= x <= b.x + b.w and b.y <= y <= b.y + b.h:
                return b.upgrade_id
        return None

    def on_mouse_press(self, x: int, y: int) -> None:
        upgrade_id = self._hit_test(x, y)
        if upgrade_id is None:
            self._pressed_id = None
            self._pressed_down_id = None
            return

        if not self._enabled.get(upgrade_id, True):
            self._pressed_id = None
            self._pressed_down_id = None
            return

        self._pressed_id = upgrade_id
        self._pressed_down_id = upgrade_id

    def on_mouse_release(self, x: int, y: int) -> Optional[str]:

        released_over_id = self._hit_test(x, y)

        clicked_id: Optional[str] = None
        if self._pressed_down_id is not None and released_over_id == self._pressed_down_id:
            if self._enabled.get(self._pressed_down_id, True):
                clicked_id = self._pressed_down_id
        self._pressed_id = None
        self._pressed_down_id = None

        return clicked_id
