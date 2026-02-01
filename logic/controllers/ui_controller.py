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
        start_y = panel_height - 170

        self._buttons = [
            _UiButtonStub("buy_bronze_coin", panel_x + pad, start_y, btn_w, btn_h,
                          self._format_button_text("Купить бронзовую", 50), 50),
            _UiButtonStub("buy_silver_coin", panel_x + pad, start_y - 84, btn_w, btn_h,
                          self._format_button_text("Купить серебряную", 200), 200),
            _UiButtonStub("buy_gold_coin", panel_x + pad, start_y - 168, btn_w, btn_h,
                          self._format_button_text("Купить золотую", 1000), 1000),

            # НОВАЯ КНОПКА: Взять золотую на ПКМ
            _UiButtonStub("grab_upgrade", panel_x + pad, start_y - 252, btn_w, btn_h,
                          "ПКМ Золото (500)", 500),

            _UiButtonStub("silver_crit_upgrade", panel_x + pad, start_y - 336, btn_w, btn_h,
                          self._format_button_text("Крит серебра", 500, 1), 500),
            _UiButtonStub("finish_game", panel_x + pad, start_y - 420, btn_w, btn_h, "Закончить игру", 0),

            _UiButtonStub("open_settings", panel_x + pad, start_y - 504, btn_w, btn_h, "Настройки", 0),
        ]

        self._enabled = {b.upgrade_id: True for b in self._buttons}
        self._pressed_id: Optional[str] = None
        self._pressed_down_id: Optional[str] = None

        # Состояния для новой кнопки
        self._has_gold = False
        self._grab_purchased = False

    def _format_number(self, num: int) -> str:
        if num == 0: return "0"
        suffixes = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc']
        magnitude = 0
        temp_num = abs(float(num))
        while temp_num >= 1000 and magnitude < len(suffixes) - 1:
            magnitude += 1
            temp_num /= 1000.0
        formatted_val = f"{temp_num:.1f}{suffixes[magnitude]}"
        return formatted_val

    def _format_button_text(self, name: str, cost: int, level: int = 0) -> str:
        cost_str = self._format_number(cost)
        if level > 0:
            return f"{name} LvL {level} ({cost_str})"
        return f"{name} ({cost_str})"

    def update_button(self, upgrade_id: str, cost: int, level: int = 0, name: str = None) -> None:
        base_names = {
            "buy_bronze_coin": "Купить бронзовую",
            "buy_silver_coin": "Купить серебряную",
            "buy_gold_coin": "Купить золотую",
            "silver_crit_upgrade": "Крит серебра",
        }
        if name is None:
            name = base_names.get(upgrade_id, upgrade_id)

        new_title = self._format_button_text(name, cost, level)
        for b in self._buttons:
            if b.upgrade_id == upgrade_id:
                b.title = new_title
                b.base_cost = cost
                break

    def update_grab_state(self, has_gold: bool, purchased: bool) -> None:
        """Обновляет состояние кнопки захвата"""
        self._has_gold = has_gold
        self._grab_purchased = purchased

    def update(self, balance_value: int) -> None:
        for b in self._buttons:
            if b.upgrade_id in ("finish_game", "open_settings"):
                self._enabled[b.upgrade_id] = True

            elif b.upgrade_id == "grab_upgrade":
                # Кнопка активна, если золото есть, апгрейд не куплен и денег хватает
                if self._has_gold and not self._grab_purchased:
                    self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                else:
                    self._enabled[b.upgrade_id] = False

                # Меняем текст, если уже куплено
                if self._grab_purchased:
                    b.title = "ПКМ Золото (Куплено)"
                elif not self._has_gold:
                    b.title = "ПКМ Золото (Нет золота)"
                else:
                    b.title = f"ПКМ Золото ({self._format_number(b.base_cost)})"

            else:
                self._enabled[b.upgrade_id] = balance_value >= b.base_cost

    def draw(self, balance_value: int) -> None:
        # Фон
        arcade.draw_lrbt_rectangle_filled(
            self.panel_x,
            self.panel_x + self.panel_width,
            0,
            self.panel_height,
            arcade.color.LIGHT_GRAY
        )

        # Шапка
        header_height = 70
        arcade.draw_lrbt_rectangle_filled(
            self.panel_x,
            self.panel_x + self.panel_width,
            self.panel_height - header_height,
            self.panel_height,
            arcade.color.DARK_GRAY
        )

        # Баланс
        formatted_balance = self._format_number(balance_value)
        arcade.draw_text(
            f"Баланс: {formatted_balance}",
            self.panel_x + self.panel_width - 20,
            self.panel_height - (header_height / 2),
            arcade.color.WHITE,
            28,
            anchor_x="right",
            anchor_y="center",
        )

        # Заголовок
        arcade.draw_text(
            "Апгрейды",
            self.panel_x + 16,
            self.panel_height - 90,
            arcade.color.BLACK,
            20
        )

        # Кнопки
        for b in self._buttons:
            enabled = self._enabled.get(b.upgrade_id, True)
            is_pressed = (self._pressed_id == b.upgrade_id)

            y = b.y - (6 if is_pressed else 0)

            fill = arcade.color.WHITE if enabled else arcade.color.GRAY
            border = arcade.color.DARK_GRAY

            arcade.draw_lrbt_rectangle_filled(b.x, b.x + b.w, y, y + b.h, fill)
            arcade.draw_lrbt_rectangle_outline(b.x, b.x + b.w, y, y + b.h, border, 2)

            color = arcade.color.BLACK if enabled else arcade.color.DARK_GRAY
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
    


class SettingsMenu:
    def __init__(self, x, y, width, height, music_manager):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.music_manager = music_manager
        self.visible = False
        self.slider_value = music_manager.get_volume()

    def draw(self):
        if not self.visible:
            return

        # фоновый прямоугольник
        arcade.draw_rectangle_filled(
            self.x + self.width / 2,
            self.y + self.height / 2,
            self.width,
            self.height,
            arcade.color.DARK_GRAY
        )

        arcade.draw_text(
            "Настройки",
            self.x + 20,
            self.y + self.height - 40,
            arcade.color.WHITE,
            24
        )

        # ——— СЛАЙДЕР ГРОМКОСТИ ———
        slider_y = self.y + self.height - 120

        arcade.draw_text(
            f"Громкость: {int(self.slider_value * 100)}%",
            self.x + 20,
            slider_y + 20,
            arcade.color.WHITE,
            16
        )

        # линия слайдера
        arcade.draw_line(
            self.x + 20,
            slider_y,
            self.x + self.width - 20,
            slider_y,
            arcade.color.LIGHT_GRAY,
            4
        )

        # бегунок
        knob_x = self.x + 20 + self.slider_value * (self.width - 40)

        arcade.draw_circle_filled(knob_x, slider_y, 10, arcade.color.WHITE)

    def on_mouse_press(self, x, y, button):
        if not self.visible:
            return

        slider_y = self.y + self.height - 120

        # проверка попадания по слайдеру
        if abs(y - slider_y) < 20:
            # вычисляем новое значение от положения мыши
            self.slider_value = (x - (self.x + 20)) / (self.width - 40)
            self.slider_value = max(0.0, min(1.0, self.slider_value))

            self.music_manager.set_volume(self.slider_value)
