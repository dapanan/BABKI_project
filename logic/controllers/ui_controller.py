import arcade
from dataclasses import dataclass
from typing import Optional


@dataclass
class _UiButtonStub:
    upgrade_id: str
    x: float
    y: float
    w: float
    h: float
    title: str
    base_cost: int


class UIController:
    def __init__(self, panel_x: int, panel_width: int, panel_height: int) -> None:
        self.panel_x = panel_x
        self.panel_width = panel_width
        self.panel_height = panel_height

        pad = 16
        btn_h = 64
        btn_w = panel_width - pad * 2
        start_y = panel_height - 120

        self._buttons = [
            _UiButtonStub("buy_bronze_coin", panel_x + pad, start_y, btn_w, btn_h, "Купить бронзовую (50)", 50),

            # НОВАЯ КНОПКА: Золотая монета
            _UiButtonStub("buy_gold_coin", panel_x + pad, start_y - 84, btn_w, btn_h, "Купить золотую (1000)", 1000),

            # Сдвинули кнопку крита ниже
            _UiButtonStub("gold_crit_upgrade", panel_x + pad, start_y - 168, btn_w, btn_h, "Крит золота LvL 1 (500)",
                          500),

            # Сдвинули кнопку выхода еще ниже
            _UiButtonStub("finish_game", panel_x + pad, start_y - 252, btn_w, btn_h, "Закончить игру", 0),
        ]

        # Инициализация доступности кнопок
        self._enabled = {b.upgrade_id: True for b in self._buttons}

        self._pressed_id: Optional[str] = None
        self._pressed_down_id: Optional[str] = None

    def update(self, balance_value: int) -> None:
        # Обновляем доступность кнопок в зависимости от баланса
        for b in self._buttons:
            if b.upgrade_id == "finish_game":
                self._enabled[b.upgrade_id] = True
            else:
                # Кнопка активна, если хватает денег
                self._enabled[b.upgrade_id] = balance_value >= b.base_cost

    def draw(self, balance_value: int) -> None:
        # Фон панели
        arcade.draw_lrbt_rectangle_filled(
            self.panel_x,
            self.panel_x + self.panel_width,
            0,
            self.panel_height,
            arcade.color.WHITE_SMOKE
        )

        # Заголовок и баланс
        arcade.draw_text("Апгрейды", self.panel_x + 16, self.panel_height - 40, arcade.color.BLACK, 20)
        arcade.draw_text(f"Баланс: {balance_value}", self.panel_x + 16, self.panel_height - 70, arcade.color.BLACK, 14)

        for b in self._buttons:
            enabled = self._enabled.get(b.upgrade_id, True)
            is_pressed = (self._pressed_id == b.upgrade_id)

            y = b.y - (6 if is_pressed else 0)

            fill = arcade.color.LIGHT_GRAY if enabled else arcade.color.DARK_GRAY
            border = arcade.color.GRAY

            arcade.draw_lrbt_rectangle_filled(b.x, b.x + b.w, y, y + b.h, fill)
            arcade.draw_lrbt_rectangle_outline(b.x, b.x + b.w, y, y + b.h, border, 2)

            color = arcade.color.BLACK if enabled else arcade.color.GRAY
            arcade.draw_text(b.title, b.x + 14, y + 22, color, 13)

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