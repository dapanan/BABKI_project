import arcade
from dataclasses import dataclass
from typing import Optional, List, Dict


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


@dataclass
class _UiGroupStub:
    title: str
    buttons: List[_UiButtonStub]


class UIController:
    def __init__(self, panel_x: int, panel_width: int, panel_height: int, ui_assets: dict,
                 scale_factor: float = 1.0) -> None:
        self.panel_x = panel_x
        self.panel_width = panel_width
        self.panel_height = panel_height

        self.ui_assets = ui_assets
        self.current_font = "RuneScape-ENA"
        self.scale_factor = scale_factor

        self.header_height = int(70 * self.scale_factor)
        self.tab_bar_height = int(50 * self.scale_factor)
        self.padding = int(16 * self.scale_factor)
        self.btn_height = int(64 * self.scale_factor)
        self.group_header_height = int(40 * self.scale_factor)
        self.btn_gap = int(10 * self.scale_factor)

        self.tabs = [
            _TabStub(0, "Монетки"),
            _TabStub(1, "Карта"),
            _TabStub(2, "Общее"),
        ]
        self.active_tab_index = 0
        self.tab_content: Dict[int, List[_UiGroupStub]] = {}

        self.tab_content[0] = [
            _UiGroupStub("Бронзовая монетка", [_UiButtonStub("buy_bronze_coin", "Купить бронзовую", 50)]),
            _UiGroupStub("Серебряная монетка", [
                _UiButtonStub("buy_silver_coin", "Купить серебряную", 200),
                _UiButtonStub("silver_crit_upgrade", "Крит серебра", 500),
            ]),
            _UiGroupStub("Золотая монетка", [
                _UiButtonStub("buy_gold_coin", "Купить золотую", 1000),
                _UiButtonStub("gold_explosion_upgrade", "Взрыв золота", 2000),
                _UiButtonStub("grab_upgrade", "ПКМ Золото", 500),
            ]),
        ]

        self.tab_content[1] = [
            _UiGroupStub("Летающий висп", [
                _UiButtonStub("wisp_spawn", "Призыв виспа", 5000),
                _UiButtonStub("wisp_speed", "Скорость виспа", 1000),
                _UiButtonStub("wisp_size", "Размер виспа", 1000),
            ]),
            _UiGroupStub("Маятник", [_UiButtonStub("pendulum_unlock", "Разблокировать маятник", 2000)]),
        ]

        self.tab_content[2] = [
            _UiGroupStub("Система", [_UiButtonStub("finish_game", "Закончить игру", 0)]),
        ]

        self._enabled = {b.upgrade_id: True for tab_groups in self.tab_content.values() for grp in tab_groups for b in
                         grp.buttons}
        self._pressed_id: Optional[str] = None
        self._pressed_down_id: Optional[str] = None
        self._has_gold = False
        self._grab_purchased = False
        self._explosion_purchased = False
        self._has_wisp = False
        self.scroll_y = 0

        self.font_size_header = int(30 * self.scale_factor)
        self.font_size_balance = int(28 * self.scale_factor)
        self.font_size_button = int(19 * self.scale_factor)
        self.font_size_tab = int(16 * self.scale_factor)
        self.font_size_group = int(20 * self.scale_factor)

        self._init_button_texts()
        self.header_text = arcade.Text("Апгрейды", self.panel_x + self.padding,
                                       self.panel_height - int(40 * self.scale_factor),
                                       (50, 50, 50, 255), self.font_size_header, font_name=self.current_font)
        self.balance_text = arcade.Text("", 0, 0, arcade.color.WHITE, self.font_size_balance,
                                        anchor_x="right", anchor_y="center", font_name=self.current_font)

    def _init_button_texts(self):
        for tab_groups in self.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:
                    b.text_obj = arcade.Text("", 0, 0, (50, 50, 50, 255), self.font_size_button,
                                             font_name=self.current_font)

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
        if level > 0: return f"{name} LvL {level} ({cost_str})"
        return f"{name} ({cost_str})"

    def update_button(self, upgrade_id: str, cost: int, level: int = 0, name: str = None) -> None:
        base_names = {"buy_bronze_coin": "Купить бронзовую", "buy_silver_coin": "Купить серебряную",
                      "buy_gold_coin": "Купить золотую", "silver_crit_upgrade": "Крит серебра"}
        if name is None: name = base_names.get(upgrade_id, upgrade_id)
        new_title = self._format_button_text(name, cost, level)
        for tab_groups in self.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:
                    if b.upgrade_id == upgrade_id:
                        b.title = new_title
                        b.base_cost = cost
                        return

    def update_grab_state(self, has_gold: bool, purchased: bool) -> None:
        self._has_gold = has_gold
        self._grab_purchased = purchased

    def update_explosion_state(self, purchased: bool) -> None:
        self._explosion_purchased = purchased

    def update_wisp_state(self, has_wisp: bool) -> None:
        self._has_wisp = has_wisp

    def set_button_disabled(self, upgrade_id: str, title: str) -> None:
        for tab_groups in self.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:
                    if b.upgrade_id == upgrade_id:
                        b.title = title
                        self._enabled[upgrade_id + "_bought"] = True
                        return

    def update(self, balance_value: int) -> None:
        for tab_groups in self.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:
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
                    elif b.upgrade_id == "wisp_spawn":
                        if self._has_wisp:
                            b.title = "Висп уже призван"
                            self._enabled[b.upgrade_id] = False
                        else:
                            self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                    elif b.upgrade_id == "wisp_speed":
                        if self._has_wisp:
                            self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                        else:
                            self._enabled[b.upgrade_id] = False
                    elif b.upgrade_id == "wisp_size":
                        if self._has_wisp:
                            self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                        else:
                            self._enabled[b.upgrade_id] = False
                    else:
                        self._enabled[b.upgrade_id] = balance_value >= b.base_cost

    def draw(self, balance_value: int) -> None:
        arcade.draw_lrbt_rectangle_filled(self.panel_x, self.panel_x + self.panel_width, 0, self.panel_height,
                                          arcade.color.LIGHT_GRAY)
        self._draw_content()
        self._draw_tab_bar()

        header_bg_y_top = self.panel_height
        header_bg_y_bottom = self.panel_height - self.header_height
        arcade.draw_lrbt_rectangle_filled(self.panel_x, self.panel_x + self.panel_width, header_bg_y_bottom,
                                          header_bg_y_top, arcade.color.DARK_GRAY)

        formatted_balance = self._format_number(balance_value)
        self.balance_text.text = f"Баланс: {formatted_balance}"
        self.balance_text.x = self.panel_x + self.panel_width - 20
        self.balance_text.y = self.panel_height - (self.header_height / 2)
        self.balance_text.draw()
        self.header_text.draw()

    def _draw_tab_bar(self):
        tab_y = self.panel_height - self.header_height - self.tab_bar_height
        tab_w = self.panel_width / len(self.tabs)
        for i, tab in enumerate(self.tabs):
            x = self.panel_x + i * tab_w
            if i == self.active_tab_index:
                bg_color = arcade.color.WHITE
                text_color = arcade.color.BLACK
            else:
                bg_color = arcade.color.GRAY
                text_color = (50, 50, 50, 255)
            arcade.draw_lrbt_rectangle_filled(x, x + tab_w, tab_y, tab_y + self.tab_bar_height, bg_color)
            arcade.draw_lrbt_rectangle_outline(x, x + tab_w, tab_y, tab_y + self.tab_bar_height, arcade.color.DARK_GRAY,
                                               2)
            text = arcade.Text(tab.title, x + tab_w / 2, tab_y + self.tab_bar_height / 2, text_color, 16,
                               anchor_x="center", anchor_y="center", font_name=self.current_font)
            text.draw()

    def _draw_content(self):
        groups = self.tab_content.get(self.active_tab_index, [])
        content_start_y = self.panel_height - self.header_height - self.tab_bar_height
        fade_margin = 40.0
        current_base_y = content_start_y + self.scroll_y
        for grp in groups:
            header_y_top = current_base_y
            header_y_bottom = header_y_top - self.group_header_height
            if header_y_top > 0 and header_y_bottom < content_start_y:
                grp_text = arcade.Text(grp.title, self.panel_x + self.padding,
                                       header_y_bottom + int(10 * self.scale_factor),
                                       (30, 30, 30, 255), self.font_size_group, font_name=self.current_font, bold=True)
                grp_text.draw()
                arcade.draw_line(self.panel_x + self.padding, header_y_bottom, self.panel_x + self.padding + 2,
                                 header_y_bottom, (50, 50, 50, 255), 2)
            current_base_y -= self.group_header_height
            for b in grp.buttons:
                b_y = current_base_y - self.btn_height
                enabled = self._enabled.get(b.upgrade_id, True)
                is_pressed = (self._pressed_id == b.upgrade_id)
                y_draw = b_y - (6 if is_pressed else 0)
                alpha = 255
                if b_y < fade_margin:
                    factor = b_y / fade_margin
                    alpha = int(255 * max(0, factor))
                button_top_edge = y_draw + self.btn_height
                dist_from_menu = button_top_edge - content_start_y
                if dist_from_menu > 0 and dist_from_menu < fade_margin:
                    factor = 1.0 - (dist_from_menu / fade_margin)
                    alpha = int(255 * max(0, factor))
                if alpha <= 0:
                    current_base_y -= (self.btn_height + self.btn_gap)
                    continue
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
                    arcade.draw_lrbt_rectangle_filled(self.panel_x + self.padding,
                                                      self.panel_x + self.panel_width - self.padding, y_draw,
                                                      y_draw + self.btn_height, fill)
                if enabled:
                    color = (50, 50, 50, 255)
                else:
                    color = (120, 120, 120, 255)
                text_color = (color[0], color[1], color[2], alpha)
                b.text_obj.text = b.title
                b.text_obj.x = self.panel_x + self.padding + 14
                b.text_obj.y = y_draw + 22
                b.text_obj.color = text_color
                b.text_obj.draw()
                current_base_y -= (self.btn_height + self.btn_gap)

    def _get_current_buttons(self):
        return self.tab_content.get(self.active_tab_index, [])

    def _hit_test_tabs(self, x: int, y: int) -> Optional[int]:
        tab_y_top = self.panel_height - self.header_height
        tab_y_bottom = tab_y_top - self.tab_bar_height
        if tab_y_bottom < y < tab_y_top:
            tab_w = self.panel_width / len(self.tabs)
            if self.panel_x < x < self.panel_x + self.panel_width:
                col = int((x - self.panel_x) / tab_w)
                if 0 <= col < len(self.tabs): return col
        return None

    def _hit_test_buttons(self, x: int, y: int) -> Optional[str]:
        groups = self.tab_content.get(self.active_tab_index, [])
        content_start_y = self.panel_height - self.header_height - self.tab_bar_height
        current_base_y = content_start_y + self.scroll_y
        for grp in groups:
            current_base_y -= self.group_header_height
            for b in grp.buttons:
                b_y = current_base_y - self.btn_height
                bx = self.panel_x + self.padding
                by = b_y
                bw = self.panel_width - (self.padding * 2)
                bh = self.btn_height
                if bx <= x <= bx + bw and by <= y <= by + bh: return b.upgrade_id
                current_base_y -= (self.btn_height + self.btn_gap)
        return None

    def on_mouse_press(self, x: int, y: int) -> None:
        clicked_tab_index = self._hit_test_tabs(x, y)
        if clicked_tab_index is not None:
            self.active_tab_index = clicked_tab_index
            self.scroll_y = 0
            self._pressed_id = None
            self._pressed_down_id = None
            return
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
        released_over_id = self._hit_test_buttons(x, y)
        clicked_id: Optional[str] = None
        if self._pressed_down_id is not None and released_over_id == self._pressed_down_id:
            if self._enabled.get(self._pressed_down_id, True):
                clicked_id = self._pressed_down_id
        self._pressed_id = None
        self._pressed_down_id = None
        return clicked_id

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        groups = self.tab_content.get(self.active_tab_index, [])
        content_height = 0
        for grp in groups:
            header_h = self.group_header_height
            buttons_h = len(grp.buttons) * (self.btn_height + self.btn_gap)
            content_height += (header_h + buttons_h)
        visible_height = self.panel_height - self.header_height - self.tab_bar_height
        if content_height <= visible_height:
            self.scroll_y = 0
            return
        max_scroll_limit = (content_height - visible_height) + 50
        self.scroll_y -= scroll_y * 50
        if self.scroll_y < 0:
            self.scroll_y = 0
        elif self.scroll_y > max_scroll_limit:
            self.scroll_y = max_scroll_limit