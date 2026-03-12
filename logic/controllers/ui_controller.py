import pygame
import os
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
    base_name: str
    base_cost: int
    is_one_time: bool = True
    is_purchased: bool = False
    purchased_text: str = "уже куплен"
    level: int = 0
    max_level: int = -1


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
        self.scale_factor = scale_factor
        self._has_tornado = False

        # --- ШРИФТЫ ---
        raw_font_path = self.ui_assets.get("font_name", "Arial")
        try:
            if raw_font_path != "Arial" and os.path.exists(raw_font_path):
                self.game_font_path = raw_font_path
            else:
                self.game_font_path = None
        except:
            self.game_font_path = None

        if self.game_font_path:
            try:
                self.base_font = pygame.font.Font(self.game_font_path, 20)
            except:
                self.base_font = pygame.font.SysFont("Arial", 20)
        else:
            self.base_font = pygame.font.SysFont("Arial", 20)

        # --- НАСТРОЙКИ ЛАЙАУТА (Увеличены для удобства) ---
        self.header_height = int(80 * self.scale_factor) # Было 70
        self.tab_bar_height = int(50 * self.scale_factor)
        self.padding = int(20 * self.scale_factor)     # Было 16
        self.btn_height = int(70 * self.scale_factor)   # Было 64 (Кнопки выше)
        self.group_header_height = int(40 * self.scale_factor)
        self.btn_gap = int(10 * self.scale_factor)

        self.tabs = [
            _TabStub(0, "Монетки"),
            _TabStub(1, "Карта"),
            _TabStub(2, "Общее"),
        ]
        self.active_tab_index = 0
        self.tab_content: Dict[int, List[_UiGroupStub]] = {}

        # === ВКЛАДКА 0 ===
        self.tab_content[0] = [
            _UiGroupStub("Бронзовая монетка", [
                _UiButtonStub("buy_bronze_coin", "Купить бронзовую монетку", "Купить бронзовую", 10, is_one_time=False,
                              level=1, max_level=-1),
                _UiButtonStub("bronze_value_upgrade", "Цена бронзовой монетки x2", "Цена бронзовой x2", 50,
                              is_one_time=False, level=0, max_level=50),
            ]),
            _UiGroupStub("Серебряная монетка", [
                _UiButtonStub("silver_crit_chance_upgrade", "Шанс крита серебрянной монетки", "Шанс крита", 500,
                              is_one_time=False, level=1, max_level=50),
                _UiButtonStub("silver_crit_upgrade", "Размер крита серебра", "Размер крита", 2000, is_one_time=False,
                              level=1, max_level=20),
                _UiButtonStub("silver_value_upgrade", "Цена серебрянной монетки x2", "Цена серебрянной x2", 1000,
                              is_one_time=False, level=0, max_level=50),
            ]),
            _UiGroupStub("Золотая монетка", [
                _UiButtonStub("gold_explosion_upgrade", "Золотая переворачивает другие",
                              "Золотая переворачивает другие", 15000, is_one_time=True),
                _UiButtonStub("grab_upgrade", "Взять золотую на ПКМ", "Взять золотую на ПКМ", 25000, is_one_time=True),
                _UiButtonStub("gold_value_upgrade", "Цена золотой монетки x2", "Цена золотой x2", 5000,
                              is_one_time=False, level=0, max_level=50),
            ]),
            _UiGroupStub("Комбо", [
                _UiButtonStub("unlock_combo", "Открыть комбо", "Открыть комбо", 50000000, is_one_time=True),
                _UiButtonStub("upgrade_combo_limit", "Лимит комбо", "Лимит комбо", 100000000, is_one_time=False,
                              level=1, max_level=10),
            ]),
            _UiGroupStub("Общее для монеток", [
                _UiButtonStub("auto_flip_upgrade", "Авто-переворот", "Авто-переворот", 1000, is_one_time=False, level=0,
                              max_level=10),
                _UiButtonStub("fuse_to_silver", "Слияние в серебро (5->1)", "Слияние в серебро", 0, is_one_time=False,
                              max_level=-1),
                _UiButtonStub("fuse_to_gold", "Слияние в золото (3->1)", "Слияние в золото", 0, is_one_time=False,
                              max_level=-1),
            ])
        ]
        # === ВКЛАДКА 1 ===
        self.tab_content[1] = [
            _UiGroupStub("Летающий висп", [
                _UiButtonStub("wisp_spawn", "Висп", "Висп", 50000, is_one_time=True),
                _UiButtonStub("wisp_speed", "Скорость виспа", "Скорость виспа", 10000, is_one_time=False, level=0,
                              max_level=30),
                _UiButtonStub("wisp_size", "Размер виспа", "Размер виспа", 10000, is_one_time=False, level=0,
                              max_level=30),
            ]),
            _UiGroupStub("Зона x2", [
                _UiButtonStub("spawn_zone_2", "Зона x2", "Зона x2", 80000, is_one_time=True),
                _UiButtonStub("upgrade_zone_2_size", "Размер зоны x2", "Размер зоны x2", 20000, is_one_time=False,
                              level=0, max_level=20),
                _UiButtonStub("upgrade_zone_2_mult", "Множитель зоны x2", "Множитель зоны x2", 40000, is_one_time=False,
                              level=0, max_level=10),
            ]),
            _UiGroupStub("Зона x5", [
                _UiButtonStub("spawn_zone_5", "Зона x5", "Зона x5", 500000, is_one_time=True),
                _UiButtonStub("upgrade_zone_5_size", "Размер зоны x5", "Размер зоны x5", 100000, is_one_time=False,
                              level=0, max_level=20),
                _UiButtonStub("upgrade_zone_5_mult", "Множитель зоны x5", "Множитель зоны x5", 200000,
                              is_one_time=False, level=0, max_level=10),
            ]),
            _UiGroupStub("Торнадо", [
                _UiButtonStub("spawn_tornado", "Торнадо", "Торнадо", 2000000, is_one_time=True),
                _UiButtonStub("tornado_cooldown_upgrade", "КД Торнадо", "КД Торнадо", 500000, is_one_time=False,
                              level=0, max_level=10),
            ]),
            _UiGroupStub("Метеорит", [
                _UiButtonStub("spawn_meteor", "Метеорит", "Метеорит", 10000000, is_one_time=True),
                _UiButtonStub("meteor_cooldown_upgrade", "КД метеорита", "КД метеорита", 2000000, is_one_time=False,
                              level=0, max_level=10),
            ]),
        ]
        # === ВКЛАДКА 2 ===
        self.tab_content[2] = [
            _UiGroupStub("Настройки", [
                _UiButtonStub("new_game", "Новая игра(потерять прогресс)", "Новая игра", 0, is_one_time=True),
                _UiButtonStub("finish_game", "Выйти из игры", "Выйти", 0, is_one_time=True),
                _UiButtonStub("buy_victory", "Победа??", "Победа", 10_000_000_000_000_000_000_000_000,
                              is_one_time=True),
            ]),
        ]

        self._enabled = {b.upgrade_id: True
                         for tab_groups in self.tab_content.values()
                         for grp in tab_groups
                         for b in grp.buttons}

        self._pressed_id: Optional[str] = None
        self._pressed_down_id: Optional[str] = None

        self._has_gold = False
        self._grab_purchased = False
        self._explosion_purchased = False
        self._has_wisp = False
        self._has_zone_2 = False
        self._has_zone_5 = False
        self._meteor_unlocked = False

        self.scroll_y = 0

        self.font_size_header = int(32 * self.scale_factor) # Было 30
        self.font_size_balance = int(30 * self.scale_factor) # Было 28
        self.font_size_button = int(22 * self.scale_factor)  # Было 19 (Шрифт больше)
        self.font_size_tab = int(18 * self.scale_factor)
        self.font_size_group = int(22 * self.scale_factor)  # Было 20

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

    def update_button(self, upgrade_id: str, cost: int, level: int = 0, name: str = None) -> None:
        for tab_groups in self.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:
                    if b.upgrade_id == upgrade_id:
                        b.base_cost = cost
                        b.level = level
                        if name is not None:
                            b.base_name = name
                            b.title = name
                        if b.upgrade_id in ["new_game", "finish_game"]:
                            b.title = b.base_name
                            return
                        price_str = self._format_number(cost)
                        if b.is_one_time:
                            if not b.is_purchased:
                                b.title = f"{b.base_name} ({price_str})"
                        else:
                            if level > 0:
                                b.title = f"{b.base_name} ({level}) ({price_str})"
                            else:
                                b.title = f"{b.base_name} ({price_str})"
                        return

    # Сокращенные методы обновления состояния (без изменений логики)
    def update_grab_state(self, has_gold: bool, purchased: bool) -> None:
        self._has_gold = has_gold
        self._grab_purchased = purchased

    def update_explosion_state(self, purchased: bool) -> None:
        self._explosion_purchased = purchased

    def update_wisp_state(self, has_wisp: bool) -> None:
        self._has_wisp = has_wisp

    def update_meteor_state(self, unlocked: bool) -> None:
        self._meteor_unlocked = unlocked

    def update_zone_state(self, has_zone_2=None, has_zone_5=None) -> None:
        if has_zone_2 is not None: self._has_zone_2 = has_zone_2
        if has_zone_5 is not None: self._has_zone_5 = has_zone_5

    def update_tornado_state(self, unlocked: bool):
        self._has_tornado = unlocked

    def set_button_disabled(self, upgrade_id: str, title: str) -> None:
        for tab_groups in self.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:
                    if b.upgrade_id == upgrade_id:
                        b.title = title
                        self._enabled[upgrade_id] = False
                        return

    def update(self, balance_value: int, coin_counts=None) -> None:
        for tab_groups in self.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:

                    # --- ФИНАЛЬНАЯ ПРОВЕРКА (Исправление белых кнопок) ---
                    # Если в названии уже написано "Макс.", отключаем кнопку насильно
                    if "Макс." in b.title or "(Max.)" in b.title:
                        self._enabled[b.upgrade_id] = False
                        continue  # Переходим к следующей кнопке
                    # ----------------------------------------------------------

                    # 1. Системные кнопки
                    if b.upgrade_id in ["new_game", "finish_game"]:
                        self._enabled[b.upgrade_id] = True
                        b.title = b.base_name
                        continue

                    # 2. Победа
                    if b.upgrade_id == "buy_victory":
                        self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                        continue

                    # 3. Проверка Максимального Уровня (Дублирование защиты)
                    if b.max_level > 0 and b.level >= b.max_level:
                        b.title = f"{b.base_name} (Макс.)"
                        self._enabled[b.upgrade_id] = False
                        continue

                    # 4. Если уже куплено
                    if b.is_purchased:
                        self._enabled[b.upgrade_id] = False
                        continue

                    # --- ЛОГИКА СПЕЦИАЛЬНЫХ КНОПОК (Остальное без изменений) ---

                    elif b.upgrade_id == "silver_crit_upgrade":
                        self._enabled[b.upgrade_id] = balance_value >= b.base_cost

                    elif b.upgrade_id == "grab_upgrade":
                        if self._has_gold and not b.is_purchased:
                            self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                        else:
                            self._enabled[b.upgrade_id] = False

                    elif b.upgrade_id == "gold_explosion_upgrade":
                        self._enabled[b.upgrade_id] = (not self._explosion_purchased) and (balance_value >= b.base_cost)

                    elif b.upgrade_id == "wisp_spawn":
                        if self._has_wisp:
                            b.title = "Висп уже призван"
                            self._enabled[b.upgrade_id] = False
                        else:
                            self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                    elif "wisp" in b.upgrade_id and b.upgrade_id != "wisp_spawn":
                        self._enabled[b.upgrade_id] = self._has_wisp and (balance_value >= b.base_cost)

                    elif b.upgrade_id == "spawn_zone_2":
                        if self._has_zone_2:
                            b.title = "Зона x2 (Куплено)"
                            self._enabled[b.upgrade_id] = False
                        else:
                            self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                    elif b.upgrade_id == "spawn_zone_5":
                        if self._has_zone_5:
                            b.title = "Зона x5 (Куплено)"
                            self._enabled[b.upgrade_id] = False
                        else:
                            self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                    elif "upgrade_zone_2" in b.upgrade_id:
                        self._enabled[b.upgrade_id] = self._has_zone_2 and (balance_value >= b.base_cost)
                    elif "upgrade_zone_5" in b.upgrade_id:
                        self._enabled[b.upgrade_id] = self._has_zone_5 and (balance_value >= b.base_cost)

                    elif "meteor" in b.upgrade_id and b.upgrade_id != "spawn_meteor":
                        if not self._meteor_unlocked:
                            self._enabled[b.upgrade_id] = False
                        else:
                            if b.level < b.max_level:
                                self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                            else:
                                self._enabled[b.upgrade_id] = False

                    elif b.upgrade_id == "spawn_tornado":
                        if self._has_tornado:
                            b.title = "Торнадо (Куплено)"
                            self._enabled[b.upgrade_id] = False
                        else:
                            self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                    elif "tornado" in b.upgrade_id and b.upgrade_id != "spawn_tornado":
                        if not self._has_tornado:
                            self._enabled[b.upgrade_id] = False
                        else:
                            if b.level < b.max_level:
                                self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                            else:
                                self._enabled[b.upgrade_id] = False

                    elif b.upgrade_id == "fuse_to_silver":
                        if coin_counts and coin_counts.get('bronze', 0) >= 5:
                            self._enabled[b.upgrade_id] = True
                            b.title = f"Слияние в серебро (5->1)"
                        else:
                            self._enabled[b.upgrade_id] = False
                            needed = 5 - coin_counts.get('bronze', 0) if coin_counts else 5
                            b.title = f"Слияние в серебро (нужно {needed})"
                    elif b.upgrade_id == "fuse_to_gold":
                        if coin_counts and coin_counts.get('silver', 0) >= 3:
                            self._enabled[b.upgrade_id] = True
                            b.title = f"Слияние в золото (3->1)"
                        else:
                            self._enabled[b.upgrade_id] = False
                            needed = 3 - coin_counts.get('silver', 0) if coin_counts else 3
                            b.title = f"Слияние в золото (нужно {needed})"

                    elif b.upgrade_id == "auto_flip_upgrade":
                        self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                    elif "value_upgrade" in b.upgrade_id:
                        self._enabled[b.upgrade_id] = balance_value >= b.base_cost
                    else:
                        self._enabled[b.upgrade_id] = balance_value >= b.base_cost

    def draw(self, surface, screen_height, balance_value: int) -> None:
        # 1. Фон панели (Серый)
        pygame.draw.rect(surface, (200, 200, 200), (self.panel_x, 0, self.panel_width, self.panel_height))

        # Координаты на экране
        header_rect = pygame.Rect(self.panel_x, 0, self.panel_width, self.header_height)
        tabs_rect = pygame.Rect(self.panel_x, self.header_height, self.panel_width, self.tab_bar_height)

        # 2. Рисуем Хедер (Темный фон, Баланс сверху)
        pygame.draw.rect(surface, (50, 50, 50), header_rect)

        # Заголовок текст
        head_font = pygame.font.Font(self.game_font_path,
                                     self.font_size_header) if self.game_font_path else pygame.font.SysFont("Arial",
                                                                                                            self.font_size_header)
        title_surf = head_font.render("Апгрейды", True, (200, 200, 200))
        surface.blit(title_surf, (self.panel_x + self.padding, 20))

        # Баланс текст (Справа вверху)
        formatted_balance = self._format_number(balance_value)
        bal_font = pygame.font.Font(self.game_font_path,
                                    self.font_size_balance) if self.game_font_path else pygame.font.SysFont("Arial",
                                                                                                            self.font_size_balance)
        bal_surf = bal_font.render(f"Баланс: {formatted_balance}", True, (255, 255, 255))
        bal_rect = bal_surf.get_rect(midright=(self.panel_x + self.panel_width - 20, self.header_height / 2))
        surface.blit(bal_surf, bal_rect)

        # 3. Рисуем Табы
        self._draw_tab_bar(surface, tabs_rect)

        # 4. Рисуем Контент (С обрезкой и скроллом)
        content_start_y = self.header_height + self.tab_bar_height
        content_height = self.panel_height - content_start_y
        clip_rect = pygame.Rect(self.panel_x, content_start_y, self.panel_width, content_height)

        surface.set_clip(clip_rect)

        # Смещение для рисования
        current_draw_y = content_start_y - self.scroll_y

        group_font = pygame.font.Font(self.game_font_path,
                                      self.font_size_group) if self.game_font_path else pygame.font.SysFont("Arial",
                                                                                                            self.font_size_group)
        btn_font = pygame.font.Font(self.game_font_path,
                                    self.font_size_button) if self.game_font_path else pygame.font.SysFont("Arial",
                                                                                                           self.font_size_button)

        groups = self.tab_content.get(self.active_tab_index, [])

        for grp in groups:
            # Заголовок группы
            grp_surf = group_font.render(grp.title, True, (30, 30, 30))
            surface.blit(grp_surf, (self.panel_x + self.padding, current_draw_y + 10))
            pygame.draw.line(surface, (100, 100, 100), (self.panel_x + self.padding, current_draw_y + 35),
                             (self.panel_x + self.panel_width - self.padding, current_draw_y + 35), 1)

            current_draw_y += self.group_header_height

            # Кнопки
            for b in grp.buttons:
                # Если кнопка вышла за пределы видимости снизу - прерываем (оптимизация)
                if current_draw_y > content_start_y + content_height:
                    break

                enabled = self._enabled.get(b.upgrade_id, True)
                is_pressed = (self._pressed_id == b.upgrade_id)
                y_draw = current_draw_y + (6 if is_pressed else 0)  # Эффект нажатия

                # Рисуем кнопку
                texture_to_draw = None
                if self.ui_assets["btn_normal"]:
                    if not enabled:
                        texture_to_draw = self.ui_assets["btn_disabled"]
                    elif is_pressed:
                        texture_to_draw = self.ui_assets["btn_pressed"]
                    else:
                        texture_to_draw = self.ui_assets["btn_normal"]

                btn_w = self.panel_width - (self.padding * 2)

                if texture_to_draw:
                    scaled_tex = pygame.transform.scale(texture_to_draw, (btn_w, self.btn_height))
                    surface.blit(scaled_tex, (self.panel_x + self.padding, y_draw))
                else:
                    fill = (255, 255, 255) if enabled else (150, 150, 150)
                    pygame.draw.rect(surface, fill, (self.panel_x + self.padding, y_draw, btn_w, self.btn_height))
                    pygame.draw.rect(surface, (50, 50, 50),
                                     (self.panel_x + self.padding, y_draw, btn_w, self.btn_height), 1)

                # Текст кнопки
                color = (50, 50, 50) if enabled else (100, 100, 100)
                text_surf = btn_font.render(b.title, True, color)
                surface.blit(text_surf, (self.panel_x + self.padding + 14, y_draw + 22))

                current_draw_y += self.btn_height + self.btn_gap

            current_draw_y += 20  # Отступ между группами

        surface.set_clip(None)

    def _draw_tab_bar(self, surface, rect):
        tab_w = self.panel_width / len(self.tabs)
        tab_font = pygame.font.Font(self.game_font_path,
                                    self.font_size_tab) if self.game_font_path else pygame.font.SysFont("Arial",
                                                                                                        self.font_size_tab)

        for i, tab in enumerate(self.tabs):
            x = rect.x + i * tab_w
            # Фон таба
            if i == self.active_tab_index:
                bg_color = (255, 255, 255)
                text_color = (0, 0, 0)
            else:
                bg_color = (180, 180, 180)
                text_color = (50, 50, 50)

            pygame.draw.rect(surface, bg_color, (x, rect.y, tab_w, rect.height))
            pygame.draw.rect(surface, (100, 100, 100), (x, rect.y, tab_w, rect.height), 1)

            # Текст таба
            text_surf = tab_font.render(tab.title, True, text_color)
            text_rect = text_surf.get_rect(center=(x + tab_w / 2, rect.y + rect.height / 2))
            surface.blit(text_surf, text_rect)

    def _hit_test_tabs(self, x: int, y: int) -> Optional[int]:
        # Проверка клика по табам
        if self.header_height < y < self.header_height + self.tab_bar_height:
            if self.panel_x < x < self.panel_x + self.panel_width:
                tab_w = self.panel_width / len(self.tabs)
                col = int((x - self.panel_x) / tab_w)
                if 0 <= col < len(self.tabs): return col
        return None

    def _hit_test_buttons(self, x: int, y: int) -> Optional[str]:
        # Проверка клика по кнопкам с учетом скролла
        content_start_y = self.header_height + self.tab_bar_height
        current_y = content_start_y - self.scroll_y

        groups = self.tab_content.get(self.active_tab_index, [])
        for grp in groups:
            current_y += self.group_header_height
            for b in grp.buttons:
                bx = self.panel_x + self.padding
                by = current_y
                bw = self.panel_width - (self.padding * 2)
                bh = self.btn_height
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    return b.upgrade_id
                current_y += self.btn_height + self.btn_gap
            current_y += 20
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

    def on_mouse_scroll(self, x: int, y: int, scroll_y: int) -> None:
        # Инвертируем логику: Крутим колесо ВВЕРХ (scroll_y < 0) -> Список идет ВВЕРХ (scroll_y уменьшается)
        self.scroll_y -= scroll_y * 20

        # Ограничения скролла
        content_h = 0
        for grp in self.tab_content.get(self.active_tab_index, []):
            h = self.group_header_height
            h += len(grp.buttons) * (self.btn_height + self.btn_gap)
            h += 20
            content_h += h

        visible_h = self.panel_height - self.header_height - self.tab_bar_height
        max_scroll = max(0, content_h - visible_h)

        if self.scroll_y < 0: self.scroll_y = 0
        if self.scroll_y > max_scroll: self.scroll_y = max_scroll

    def mark_purchased(self, upgrade_id: str) -> None:
        for tab_groups in self.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:
                    if b.upgrade_id == upgrade_id:
                        b.is_purchased = True
                        b.title = f"{b.base_name} ({b.purchased_text})"
                        self._enabled[upgrade_id] = False
                        return