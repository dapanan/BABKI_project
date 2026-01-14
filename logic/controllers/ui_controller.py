import arcade
from dataclasses import dataclass
from typing import Optional, List, Dict


# --- Вспомогательные классы ---

@dataclass
class _TabStub:
    tab_id: int
    title: str


@dataclass
class _UiButtonStub:
    upgrade_id: str
    title: str
    base_cost: int
    text_obj: arcade.Text = None


class UIController:
    def __init__(self, panel_x: int, panel_width: int, panel_height: int, ui_assets: dict) -> None:
        self.panel_x = panel_x
        self.panel_width = panel_width
        self.panel_height = panel_height

        self.ui_assets = ui_assets
        self.current_font = "RuneScape-ENA"  # Твой шрифт

        # --- НАСТРОЙКИ ЛАЙАУТА ---
        self.header_height = 70
        self.tab_bar_height = 50
        self.padding = 16

        # --- СОЗДАНИЕ ВКЛАДОК ---
        self.tabs = [
            _TabStub(0, "Общее"),
            _TabStub(1, "Золото"),
            _TabStub(2, "Серебро"),
            _TabStub(3, "Система"),
        ]
        self.active_tab_index = 0

        # --- ГРУППИРОВКА КНОПОК ПО ВКЛАДКАМ ---
        # Ключ - ID вкладки, Значение - список кнопок
        self.tab_content: Dict[int, List[_UiButtonStub]] = {}

        # Вкладка 0: Общее (Покупка монет + тестовые)
        self.tab_content[0] = [
            _UiButtonStub("buy_bronze_coin", "Купить бронзовую", 50),
            _UiButtonStub("buy_silver_coin", "Купить серебряную", 200),
            _UiButtonStub("buy_gold_coin", "Купить золотую", 1000),
        ]

        # Добавляем тестовые кнопки
        for i in range(1, 26):
            dummy_id = f"test_scroll_{i}"
            dummy_name = f"🚧 Тест прокрутки #{i}"
            dummy_cost = i * 100
            self.tab_content[0].append(_UiButtonStub(dummy_id, dummy_name, dummy_cost))

        # Вкладка 1: Золото (Апгрейды для золота)
        self.tab_content[1] = [
            _UiButtonStub("gold_explosion_upgrade", "Взрыв золота", 2000),
            _UiButtonStub("grab_upgrade", "ПКМ Золото", 500),
        ]

        # Вкладка 2: Серебро (Апгрейды для серебра)
        self.tab_content[2] = [
            _UiButtonStub("silver_crit_upgrade", "Крит серебра", 500),
        ]

        # Вкладка 3: Система (Выход)
        self.tab_content[3] = [
            _UiButtonStub("finish_game", "Закончить игру", 0),
        ]

        # --- СОСТОЯНИЕ UI ---
        self._enabled = {b.upgrade_id: True for tab_list in self.tab_content.values() for b in tab_list}
        self._pressed_id: Optional[str] = None
        self._pressed_down_id: Optional[str] = None

        self._has_gold = False
        self._grab_purchased = False
        self._explosion_purchased = False

        # Скролл списка кнопок
        self.scroll_y = 0
        self.btn_height = 64
        self.btn_gap = 10  # Отступ между кнопками

        # Инициализация текстовых объектов для кнопок
        self._init_button_texts()

        # Текст заголовка и баланса (ИЗМЕНЕН ЦВЕТ НА (50,50,50))
        self.header_text = arcade.Text("Апгрейды", self.panel_x + 16, self.panel_height - 45,
                                       (50, 50, 50, 255), 30, font_name=self.current_font)
        self.balance_text = arcade.Text("", 0, 0, arcade.color.WHITE, 28,
                                        anchor_x="right", anchor_y="center", font_name=self.current_font)

    def _init_button_texts(self):
        """Создаем текстовые объекты для всех кнопок во всех вкладках"""
        # ИЗМЕНЕН ЦВЕТ НА (50,50,50)
        for tab_buttons in self.tab_content.values():
            for b in tab_buttons:
                b.text_obj = arcade.Text("", 0, 0, (50, 50, 50, 255), 19, font_name=self.current_font)

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
        for tab_buttons in self.tab_content.values():
            for b in tab_buttons:
                if b.upgrade_id == upgrade_id:
                    b.title = new_title
                    b.base_cost = cost
                    return

    def update_grab_state(self, has_gold: bool, purchased: bool) -> None:
        self._has_gold = has_gold
        self._grab_purchased = purchased

    def update_explosion_state(self, purchased: bool) -> None:
        self._explosion_purchased = purchased

    def set_button_disabled(self, upgrade_id: str, title: str) -> None:
        for tab_buttons in self.tab_content.values():
            for b in tab_buttons:
                if b.upgrade_id == upgrade_id:
                    b.title = title
                    self._enabled[upgrade_id + "_bought"] = True
                    return

    def update(self, balance_value: int) -> None:
        # Обновляем доступность кнопок
        for tab_buttons in self.tab_content.values():
            for b in tab_buttons:
                if b.upgrade_id == "finish_game":
                    self._enabled[b.upgrade_id] = True

                elif b.upgrade_id == "grab_upgrade":
                    if self._has_gold and not self._grab_purchased:
                        self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                    else:
                        self._enabled[b.upgrade_id] = False

                    if self._grab_purchased:
                        b.title = "ПКМ Золото (Куплено)"
                    elif not self._has_gold:
                        b.title = "ПКМ Золото (Нет золота)"
                    else:
                        b.title = f"ПКМ Золото ({self._format_number(b.base_cost)})"

                elif b.upgrade_id == "gold_explosion_upgrade":
                    if self._explosion_purchased:
                        self._enabled[b.upgrade_id] = False
                    else:
                        self._enabled[b.upgrade_id] = balance_value >= b.base_cost

                else:
                    self._enabled[b.upgrade_id] = balance_value >= b.base_cost

    def draw(self, balance_value: int) -> None:
        # 1. Фон панели (Самый нижний слой)
        arcade.draw_lrbt_rectangle_filled(
            self.panel_x,
            self.panel_x + self.panel_width,
            0,
            self.panel_height,
            arcade.color.LIGHT_GRAY
        )

        # 2. КНОПКИ (Слой 1: Рисуем первыми, чтобы всё было поверх них)
        self._draw_content()

        # 3. ВКЛАДКИ (Слой 2: Закрывают кнопки сверху)
        self._draw_tab_bar()

        # 4. ШАПКА (Слой 3: Самый верхний слой, чтобы текст не перекрывался кнопками)
        header_bg_y_top = self.panel_height
        header_bg_y_bottom = self.panel_height - self.header_height
        arcade.draw_lrbt_rectangle_filled(
            self.panel_x,
            self.panel_x + self.panel_width,
            header_bg_y_bottom,
            header_bg_y_top,
            arcade.color.DARK_GRAY
        )

        formatted_balance = self._format_number(balance_value)
        self.balance_text.text = f"Баланс: {formatted_balance}"
        self.balance_text.x = self.panel_x + self.panel_width - 20
        self.balance_text.y = self.panel_height - (self.header_height / 2)
        self.balance_text.draw()

        self.header_text.draw()

    def _draw_tab_bar(self):
        """Рисует кнопки переключения вкладок"""
        tab_y = self.panel_height - self.header_height - self.tab_bar_height
        tab_w = self.panel_width / len(self.tabs)

        for i, tab in enumerate(self.tabs):
            x = self.panel_x + i * tab_w

            # --- ИЗМЕНЕНИЕ ЦВЕТОВ ВКЛАДОК ---
            if i == self.active_tab_index:
                bg_color = arcade.color.WHITE  # Активная вкладка: Белый фон
                text_color = arcade.color.BLACK  # Активная вкладка: Черный текст
            else:
                bg_color = arcade.color.GRAY  # Неактивная вкладка: Серый фон
                text_color = (50, 50, 50, 255)  # Неактивная вкладка: Темно-серый текст
            # ----------------------------------

            # Рисуем фон вкладки
            arcade.draw_lrbt_rectangle_filled(x, x + tab_w, tab_y, tab_y + self.tab_bar_height, bg_color)
            # Рисуем рамку
            arcade.draw_lrbt_rectangle_outline(x, x + tab_w, tab_y, tab_y + self.tab_bar_height, arcade.color.DARK_GRAY,
                                               2)

            # Текст вкладки
            text = arcade.Text(tab.title, x + tab_w / 2, tab_y + self.tab_bar_height / 2,
                               text_color, 16, anchor_x="center", anchor_y="center", font_name=self.current_font)
            text.draw()

    def _draw_content(self):
        """Рисует кнопки активной вкладки с учетом скролла и эффекта fade"""
        buttons = self.tab_content.get(self.active_tab_index, [])

        content_start_y = self.panel_height - self.header_height - self.tab_bar_height
        fade_margin = 40.0  # На сколько пикселей кнопки будут исчезать (радиус размытия)

        for i, b in enumerate(buttons):
            # Рассчитываем позицию Y (ИСПРАВЛЕНО: + self.scroll_y)
            b_y = content_start_y - (i * (self.btn_height + self.btn_gap)) - self.btn_height + self.scroll_y

            enabled = self._enabled.get(b.upgrade_id, True)
            is_pressed = (self._pressed_id == b.upgrade_id)

            y_draw = b_y - (6 if is_pressed else 0)

            # --- РАСЧЕТ ПРОЗРАЧНОСТИ (ALPHA) ---
            alpha = 255  # По умолчанию полностью видимая

            # 1. Исчезновение снизу (появление из-под окна)
            if b_y < fade_margin:
                factor = b_y / fade_margin
                alpha = int(255 * max(0, factor))

            # 2. Исчезновение сверху (заход под меню вкладок)
            button_top_edge = y_draw + self.btn_height
            dist_from_menu = button_top_edge - content_start_y

            if dist_from_menu > 0 and dist_from_menu < fade_margin:
                factor = 1.0 - (dist_from_menu / fade_margin)
                alpha = int(255 * max(0, factor))

            if alpha <= 0:
                continue
            # -------------------------------------

            # Рисуем кнопку
            texture_to_draw = None
            if self.ui_assets["btn_normal"]:
                if not enabled:
                    texture_to_draw = self.ui_assets["btn_disabled"]
                elif is_pressed:
                    texture_to_draw = self.ui_assets["btn_pressed"]
                else:
                    texture_to_draw = self.ui_assets["btn_normal"]

            if texture_to_draw:
                button_sprite = arcade.Sprite(texture_to_draw)
                button_sprite.width = self.panel_width - (self.padding * 2)
                button_sprite.height = self.btn_height
                button_sprite.center_x = self.panel_x + self.panel_width / 2
                button_sprite.center_y = y_draw + self.btn_height / 2

                button_sprite.color = (255, 255, 255, alpha)

                temp_sprite_list = arcade.SpriteList()
                temp_sprite_list.append(button_sprite)
                temp_sprite_list.draw()
            else:
                fill = arcade.color.WHITE if enabled else arcade.color.GRAY
                arcade.draw_lrbt_rectangle_filled(
                    self.panel_x + self.padding,
                    self.panel_x + self.panel_width - self.padding,
                    y_draw,
                    y_draw + self.btn_height,
                    fill
                )

            # Текст кнопки
            # --- ИЗМЕНЕНИЕ ЦВЕТА ТЕКСТА КНОПОК ---
            if enabled:
                color = (50, 50, 50, 255)  # Включенная кнопка: Темно-серый
            else:
                color = (120, 120, 120, 255)  # Выключенная кнопка: Светло-серый
            # -----------------------------------

            text_color = (color[0], color[1], color[2], alpha)

            b.text_obj.text = b.title
            b.text_obj.x = self.panel_x + self.padding + 14
            b.text_obj.y = y_draw + 22
            b.text_obj.color = text_color
            b.text_obj.draw()

    def _get_current_buttons(self):
        return self.tab_content.get(self.active_tab_index, [])

    def _hit_test_tabs(self, x: int, y: int) -> Optional[int]:
        """Проверяет клик по вкладкам. Возвращает индекс вкладки или None"""
        tab_y_top = self.panel_height - self.header_height
        tab_y_bottom = tab_y_top - self.tab_bar_height

        if tab_y_bottom < y < tab_y_top:
            tab_w = self.panel_width / len(self.tabs)
            if self.panel_x < x < self.panel_x + self.panel_width:
                col = int((x - self.panel_x) / tab_w)
                if 0 <= col < len(self.tabs):
                    return col
        return None

    def _hit_test_buttons(self, x: int, y: int) -> Optional[str]:
        """Проверяет клик по кнопкам текущей вкладки (Формула исправлена!)"""
        buttons = self._get_current_buttons()
        content_start_y = self.panel_height - self.header_height - self.tab_bar_height

        for i, b in enumerate(buttons):
            # ВАЖНО: Формула должна быть ТОЧНО такой же, как в _draw_content
            b_y = content_start_y - (i * (self.btn_height + self.btn_gap)) - self.btn_height + self.scroll_y

            bx = self.panel_x + self.padding
            by = b_y
            bw = self.panel_width - (self.padding * 2)
            bh = self.btn_height

            if bx <= x <= bx + bw and by <= y <= by + bh:
                return b.upgrade_id
        return None

    def on_mouse_press(self, x: int, y: int) -> None:
        # Сначала проверяем клик по вкладкам
        clicked_tab_index = self._hit_test_tabs(x, y)
        if clicked_tab_index is not None:
            self.active_tab_index = clicked_tab_index
            self.scroll_y = 0  # Сброс скролла при смене вкладки
            self._pressed_id = None
            self._pressed_down_id = None
            return

        # Проверяем клик по кнопкам
        upgrade_id = self._hit_test_buttons(x, y)
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
        # Если это было переключение вкладки, ничего не возвращаем
        # (Клик по вкладке обрабатывается в Press)

        released_over_id = self._hit_test_buttons(x, y)

        clicked_id: Optional[str] = None

        if self._pressed_down_id is not None and released_over_id == self._pressed_down_id:
            if self._enabled.get(self._pressed_down_id, True):
                clicked_id = self._pressed_down_id

        self._pressed_id = None
        self._pressed_down_id = None

        return clicked_id

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        buttons = self._get_current_buttons()

        content_height = len(buttons) * (self.btn_height + self.btn_gap)
        visible_height = self.panel_height - self.header_height - self.tab_bar_height

        # Если список короткий, скролл не нужен
        if content_height <= visible_height:
            self.scroll_y = 0
            return

        # --- ГРАНИЦЫ СКРОЛЛА ---

        # Верхняя граница: 0. Список прижат к верху. Пустоты сверху нет.
        # Нижняя граница: Высота контента минус видимая часть.
        # Это как далеко можно укатить список вниз, чтобы дно вышло к краю экрана.
        # Добавляем 50 пикселей запаса, чтобы можно было чуть-чуть прокрутить "под низ".
        max_scroll_limit = (content_height - visible_height) + 50

        # ЛОГИКА ДВИЖЕНИЯ (Смена формулы)
        # Чтобы двигать список вниз (на себя), scroll_y должен РАСТИ.
        # Колесо вниз (scroll_y < 0) -> нам нужно УВЕЛИЧИТЬ scroll_y.
        # Поэтому ставим минус.
        self.scroll_y -= scroll_y * 50

        # ЗАЩИТА ОТ ВЫЛЕТА
        if self.scroll_y < 0:
            self.scroll_y = 0  # Не даем скроллить вверх (пустота сверху)
        elif self.scroll_y > max_scroll_limit:
            self.scroll_y = max_scroll_limit  # Не даем скроллить слишком низ