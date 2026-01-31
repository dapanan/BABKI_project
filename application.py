import arcade
import os
import random
import math

from logic.controllers.ui_controller import UIController
from logic.controllers.game_controller import GameController
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager

# --- АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ РАЗРЕШЕНИЯ ---
screen_width, screen_height = arcade.get_display_size()
scale_factor = screen_height / 1080.0


PANEL_WIDTH = int(500 * scale_factor)
SCREEN_TITLE = "Incremental Coin Game"

# Состояния игры
STATE_MENU = 0
STATE_GAME = 1


class MenuCoin(arcade.Sprite):
    """Класс монетки для главного меню с физикой (НЕ МЕНЯЕТ ОРЛА/РЕШКУ)"""

    def __init__(self, x, y, tex_heads, tex_tails, scale):
        super().__init__()
        # Используем только орла, меняться не будем
        self.texture = tex_heads

        self.scale = scale

        self.center_x = x
        self.center_y = y

        # Физика
        self.radius = 32 * scale

        # ИСПРАВЛЕНИЕ 3: Ускорили в 1.5 раза (было 150 * scale_factor)
        speed = 225 * scale_factor

        angle = random.uniform(0, 2 * math.pi)
        self.change_x = math.cos(angle) * speed
        self.change_y = math.sin(angle) * speed

    def update(self, dt):
        # 1. Движение
        self.center_x += self.change_x * dt
        self.center_y += self.change_y * dt

        # 2. Отскок от стен
        if self.left < 0:
            self.left = 0
            self.change_x *= -1
        # ИСПРАВЛЕНИЕ 2: Граница теперь ВЕСЬ экран (screen_width)
        elif self.right > screen_width:
            self.right = screen_width
            self.change_x *= -1

        if self.bottom < 0:
            self.bottom = 0
            self.change_y *= -1
        elif self.top > screen_height:
            self.top = screen_height
            self.change_y *= -1

        # ИСПРАВЛЕНИЕ 1: Логику переворота полностью убрали
        # Автовыбор не происходит


class GameWindow(arcade.Window):
    def __init__(self) -> None:
        super().__init__(
            width=screen_width,
            height=screen_height,
            title=SCREEN_TITLE,
            fullscreen=True,
            resizable=False,
            update_rate=1 / 60,  # Стандартные 60 FPS
            draw_rate=1 / 60,
        )

        self.background_color = arcade.color.BLACK

        # Инициализация менеджеров
        self.asset_manager = AssetManager()
        self.asset_manager.load_all()
        self.asset_manager.load_ui_assets()

        self.sound_manager = SoundManager()
        self.sound_manager.load_all()

        # Шрифт
        import pyglet.font
        font_dir = os.path.join("view", "ui", "fonts")
        if os.path.exists(font_dir):
            pyglet.font.add_directory(font_dir)
        self.menu_font = "RuneScape-ENA"

        # Инициализация контроллеров
        self.world_width = screen_width - PANEL_WIDTH
        self.world_height = screen_height

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
            world_width=self.world_width,
            world_height=self.world_height,
            scale_factor=scale_factor
        )

        # --- ЛОГИКА МЕНЮ ---
        self.state = STATE_MENU
        self.mouse_position = (0, 0)

        # Проверка сейва
        self.has_save = False
        save_path = self.game.get_save_path()
        if os.path.exists(save_path):
            if self.game.load_game():
                self.has_save = True
            else:
                try:
                    os.remove(save_path)
                except:
                    pass

        # Создание монеток для фона (20 бронза, 10 серебра, 5 золота)
        self.menu_coins = arcade.SpriteList()
        self._spawn_menu_coins()

        # Текст и кнопки
        cx = screen_width // 2
        cy = screen_height // 2
        btn_w = 240 * scale_factor
        btn_h = 60 * scale_factor

        self.btn_play = {"x": cx, "y": cy, "w": btn_w, "h": btn_h, "text": "Играть"}
        self.btn_exit = {"x": cx, "y": cy - (80 * scale_factor), "w": btn_w, "h": btn_h, "text": "Выйти"}

        self.title_text = arcade.Text(
            "Incremental coin game",
            cx, screen_height * 0.85, arcade.color.WHITE,
            font_size=int(40 * scale_factor), font_name=self.menu_font, anchor_x="center"
        )

        self.btn_play_text = arcade.Text("Играть", cx, cy, arcade.color.LIGHT_GRAY,
                                         font_size=int(20 * scale_factor), font_name=self.menu_font, anchor_x="center",
                                         anchor_y="center")
        self.btn_exit_text = arcade.Text("Выйти", cx, cy - (80 * scale_factor), arcade.color.LIGHT_GRAY,
                                         font_size=int(20 * scale_factor), font_name=self.menu_font, anchor_x="center",
                                         anchor_y="center")
        # --- Кнопка "Как играть?" ---
        self.showing_help = False  # Флаг показа окна справки
        self.btn_help = {
            "x": cx,
            "y": cy + (80 * scale_factor),  # Располагаем выше кнопки "Играть"
            "w": btn_w,
            "h": btn_h,
            "text": "Как играть?"
        }
        self.btn_help_text = arcade.Text(
            "Как играть?", cx, cy + (80 * scale_factor),
            arcade.color.LIGHT_GRAY,
            font_size=int(20 * scale_factor),
            font_name=self.menu_font,
            anchor_x="center",
            anchor_y="center"
        )

        # Параметры окна справки
        self.help_w = screen_width // 2
        self.help_h = screen_height // 2
        self.help_x = (screen_width - self.help_w) // 2
        self.help_y = (screen_height - self.help_h) // 2
        self.close_btn_size = 40 * scale_factor

        print(f"--- SYSTEM INFO ---")
        print(f"Save exists: {self.has_save}")

    def _spawn_menu_coins(self):
        """Создает фоновые монетки с физикой на весь экран"""

        def spawn_batch(count, type_key, heads_key, tails_key, scale_mod):
            for _ in range(count):
                h_tex = self.asset_manager.bronze_coin_sprites["heads"]
                t_tex = self.asset_manager.bronze_coin_sprites["tails"]

                if type_key == "bronze":
                    h_tex = self.asset_manager.bronze_coin_sprites["heads"]
                    t_tex = self.asset_manager.bronze_coin_sprites["tails"]
                elif type_key == "silver":
                    h_tex = self.asset_manager.silver_coin_sprites["heads"]
                    t_tex = self.asset_manager.silver_coin_sprites["tails"]
                elif type_key == "gold":
                    h_tex = self.asset_manager.gold_coin_sprites["heads"]
                    t_tex = self.asset_manager.gold_coin_sprites["tails"]

                # Позиция рандомная по всему экрану
                x = random.randint(50, int(screen_width - 50))
                y = random.randint(50, int(screen_height - 50))
                scale = scale_mod * self.game.scale_factor

                coin = MenuCoin(x, y, h_tex, t_tex, scale)
                self.menu_coins.append(coin)

        # 20 Bronze, 10 Silver, 5 Gold
        spawn_batch(20, "bronze", "heads", "tails", 0.8)
        spawn_batch(10, "silver", "heads", "tails", 1.1)
        spawn_batch(5, "gold", "heads", "tails", 1.5)

    def start_game(self):
        """Прямой запуск игры без анимации"""
        if not self.has_save:
            self.game.reset_game()

        self.state = STATE_GAME

    def on_update(self, delta_time: float) -> None:
        dt = min(delta_time, 0.05)

        if self.state == STATE_MENU:
            # Обновляем монетки меню
            self.menu_coins.update(dt)
            # Столкновения монеток меню
            self._handle_menu_collisions()

        elif self.state == STATE_GAME:
            self.game.update(dt)
            self.ui.update(self.game.balance.get(), self.game.get_coin_counts())

    def _handle_menu_collisions(self):
        """Простое разделение монет при столкновении"""
        coins = self.menu_coins
        n = len(coins)
        for i in range(n):
            c1 = coins[i]
            for j in range(i + 1, n):
                c2 = coins[j]

                dx = c1.center_x - c2.center_x
                dy = c1.center_y - c2.center_y
                dist_sq = dx * dx + dy * dy
                min_dist = c1.radius + c2.radius

                if dist_sq < min_dist * min_dist and dist_sq > 0:
                    dist = math.sqrt(dist_sq)
                    overlap = min_dist - dist
                    nx = dx / dist
                    ny = dy / dist

                    # Толкаем друг от друга
                    move = overlap / 2.0
                    c1.center_x += nx * move
                    c1.center_y += ny * move
                    c2.center_x -= nx * move
                    c2.center_y -= ny * move

    def on_draw(self) -> None:
        if self.state == STATE_MENU:
            arcade.set_background_color(arcade.color.BLACK)
        else:
            arcade.set_background_color(arcade.color.WHITE)

        self.clear()

        if self.state == STATE_MENU:
            self._draw_menu()
        elif self.state == STATE_GAME:
            self.game.draw()
            self.ui.draw(balance_value=self.game.balance.get())

    def _draw_menu(self):
        # 1. Монетки на фоне
        self.menu_coins.draw()

        # 2. Если открыто окно справки
        if self.showing_help:
            # Полупрозрачный фон затемнения
            arcade.draw_lrbt_rectangle_filled(0, screen_width, 0, screen_height, (0, 0, 0, 150))

            # Серый прямоугольник окна
            arcade.draw_lrbt_rectangle_filled(
                self.help_x, self.help_x + self.help_w,
                self.help_y, self.help_y + self.help_h,
                arcade.color.DARK_GRAY
            )
            # Белая рамка
            arcade.draw_lrbt_rectangle_outline(
                self.help_x, self.help_x + self.help_w,
                self.help_y, self.help_y + self.help_h,
                arcade.color.WHITE, 4
            )

            # Текст примера
            help_text = arcade.Text(
                "текст для примера",
                screen_width // 2, screen_height // 2,
                arcade.color.WHITE,
                font_size=int(24 * scale_factor),
                font_name=self.menu_font,
                anchor_x="center", anchor_y="center", multiline=True,
                width=self.help_w - 40
            )
            help_text.draw()

            # Крестик закрытия
            close_btn_size = self.close_btn_size
            close_left = self.help_x + self.help_w - close_btn_size
            close_right = self.help_x + self.help_w
            close_bottom = self.help_y + self.help_h - close_btn_size
            close_top = self.help_y + self.help_h

            arcade.draw_lrbt_rectangle_filled(
                close_left, close_right, close_bottom, close_top,
                arcade.color.RED
            )
            arcade.draw_text("X", (close_left + close_right) / 2, (close_bottom + close_top) / 2,
                             arcade.color.WHITE,
                             font_size=int(20 * scale_factor),
                             anchor_x="center", anchor_y="center")

        else:
            # Если окно закрыто - рисуем обычное меню
            self.title_text.draw()

            mx, my = self.mouse_position

            # Проверки наведения для кнопок
            p_hover = (self.btn_play["x"] - self.btn_play["w"] / 2 < mx < self.btn_play["x"] + self.btn_play[
                "w"] / 2 and
                       self.btn_play["y"] - self.btn_play["h"] / 2 < my < self.btn_play["y"] + self.btn_play[
                           "h"] / 2)

            h_hover = (self.btn_help["x"] - self.btn_help["w"] / 2 < mx < self.btn_help["x"] + self.btn_help[
                "w"] / 2 and
                       self.btn_help["y"] - self.btn_help["h"] / 2 < my < self.btn_help["y"] + self.btn_help[
                           "h"] / 2)

            e_hover = (self.btn_exit["x"] - self.btn_exit["w"] / 2 < mx < self.btn_exit["x"] + self.btn_exit[
                "w"] / 2 and
                       self.btn_exit["y"] - self.btn_exit["h"] / 2 < my < self.btn_exit["y"] + self.btn_exit[
                           "h"] / 2)

            # Список кнопок (Теперь включает Help)
            btns = [
                (self.btn_play, p_hover, self.btn_play_text),
                (self.btn_help, h_hover, self.btn_help_text),
                (self.btn_exit, e_hover, self.btn_exit_text)
            ]

            for btn, hover, text_obj in btns:
                color = arcade.color.GRAY if hover else arcade.color.DARK_GRAY
                text_obj.color = arcade.color.WHITE if hover else arcade.color.LIGHT_GRAY

                arcade.draw_lrbt_rectangle_filled(
                    btn["x"] - btn["w"] / 2, btn["x"] + btn["w"] / 2,
                    btn["y"] - btn["h"] / 2, btn["y"] + btn["h"] / 2,
                    color
                )
                arcade.draw_lrbt_rectangle_outline(
                    btn["x"] - btn["w"] / 2, btn["x"] + btn["w"] / 2,
                    btn["y"] - btn["h"] / 2, btn["y"] + btn["h"] / 2,
                    arcade.color.WHITE, 2
                )
                text_obj.draw()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        self.mouse_position = (x, y)
        if self.state == STATE_GAME:
            self.game.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.state == STATE_MENU and button == arcade.MOUSE_BUTTON_LEFT:
            # Если открыто окно справки - проверяем нажатие на крестик
            if self.showing_help:
                close_x = self.help_x + self.help_w - self.close_btn_size
                close_y = self.help_y + self.help_h - self.close_btn_size
                half = self.close_btn_size / 2

                if (close_x - half < x < close_x + half) and (close_y - half < y < close_y + half):
                    self.showing_help = False
                return

            # Если окно закрыто - проверяем кнопки меню
            if self._is_hover(self.btn_play, x, y):
                self.start_game()
            elif self._is_hover(self.btn_help, x, y):
                self.showing_help = True
            elif self._is_hover(self.btn_exit, x, y):
                arcade.close_window()
            return

        if self.state == STATE_GAME:
            if button == arcade.MOUSE_BUTTON_RIGHT:
                self.game.on_mouse_press_rmb(x, y)
                return
            if button != arcade.MOUSE_BUTTON_LEFT:
                return

            if x > self.world_width:
                self.ui.on_mouse_press(x, y)
            else:
                self.game.on_mouse_press(x, y, button)

    def _is_hover(self, btn, x, y):
        return (btn["x"] - btn["w"] / 2 < x < btn["x"] + btn["w"] / 2 and
                btn["y"] - btn["h"] / 2 < y < btn["y"] + btn["h"] / 2)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int) -> None:
        if self.state == STATE_GAME:
            if button == arcade.MOUSE_BUTTON_RIGHT:
                self.game.on_mouse_release_rmb(x, y)
                return
            if button != arcade.MOUSE_BUTTON_LEFT:
                return

            if x > self.world_width:
                upgrade_id = self.ui.on_mouse_release(x, y)
                if upgrade_id:
                    if upgrade_id == "finish_game":
                        self.game.save_game()
                        arcade.close_window()
                    else:
                        self.game.try_buy_upgrade(upgrade_id)

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        if self.state == STATE_GAME and x > self.world_width:
            self.ui.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_close(self):
        if self.state == STATE_GAME:
            self.game.save_game()
        super().on_close()