import pygame
import sys
import os
import random
import math

from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
from logic.controllers.ui_controller import UIController
from logic.controllers.game_controller import GameController
from logic.assets.sprite_pygame import PygameSprite

# --- КОНСТАНТЫ ---
VIRTUAL_WIDTH = 1920
VIRTUAL_HEIGHT = 1080
PANEL_WIDTH = 500
WORLD_WIDTH = VIRTUAL_WIDTH - PANEL_WIDTH
FPS = 60
TITLE = "Incremental Coin Game (Pygame)"

STATE_MENU = 0
STATE_GAME = 1


class MenuCoin(PygameSprite):
    """Монетка для фона меню с простой физикой"""

    def __init__(self, x, y, tex_heads, tex_tails, scale):
        super().__init__(image=tex_heads, scale=scale)
        self.center_x = x
        self.center_y = y
        self.radius = 32 * scale
        speed = 225 * scale
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self, dt, width, height):
        self.center_x += self.vx * dt
        self.center_y += self.vy * dt

        # Отскок от стен
        if self.left < 0:
            self.left = 0
            self.vx *= -1
        elif self.right > width:
            self.right = width
            self.vx *= -1
        if self.bottom < 0:
            self.bottom = 0
            self.vy *= -1
        elif self.top > height:
            self.top = height
            self.vy *= -1


def _handle_menu_collisions(coins):
    """Простая физика столкновений для монет в меню"""
    n = len(coins)
    for i in range(n):
        for j in range(i + 1, n):
            c1 = coins[i]
            c2 = coins[j]

            dx = c1.center_x - c2.center_x
            dy = c1.center_y - c2.center_y
            dist_sq = dx * dx + dy * dy
            min_dist = c1.radius + c2.radius

            if dist_sq < min_dist * min_dist:
                dist = math.sqrt(dist_sq)
                if dist == 0: dist = 0.01

                overlap = min_dist - dist
                nx = dx / dist
                ny = dy / dist

                # 1. Раздвигаем монеты (чтобы не слипались)
                move = overlap / 2.0
                c1.center_x += nx * move
                c1.center_y += ny * move
                c2.center_x -= nx * move
                c2.center_y -= ny * move

                # 2. Упругий удар (меняем скорости по нормали)
                dvx = c1.vx - c2.vx
                dvy = c1.vy - c2.vy
                dot = dvx * nx + dvy * ny

                if dot < 0:  # Столкновение только если они сближаются
                    c1.vx -= dot * nx
                    c1.vy -= dot * ny
                    c2.vx += dot * nx
                    c2.vy += dot * ny


def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Настройка окна (80% от экрана)
    info = pygame.display.Info()
    start_w = int(info.current_w * 0.8)
    start_h = int(info.current_h * 0.8)
    screen = pygame.display.set_mode((start_w, start_h), pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)

    # Виртуальный канвас (на нем все рисуется)
    canvas = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    clock = pygame.time.Clock()

    print("Initializing Managers...")
    asset_manager = AssetManager()
    asset_manager.load_all()
    asset_manager.load_ui_assets()

    sound_manager = SoundManager()
    sound_manager.load_all()

    # Загрузка шрифтов
    font_path = asset_manager.ui_assets.get("font_name", "Arial")
    try:
        if font_path != "Arial" and os.path.exists(font_path):
            main_font = pygame.font.Font(font_path, 20)
            title_font = pygame.font.Font(font_path, 40)
        else:
            main_font = pygame.font.SysFont("Arial", 20)
            title_font = pygame.font.SysFont("Arial", 40)
    except:
        main_font = pygame.font.SysFont("Arial", 20)
        title_font = pygame.font.SysFont("Arial", 40)

    # Инициализация контроллеров
    scale_factor = 1.0
    ui = UIController(
        panel_x=WORLD_WIDTH,
        panel_width=PANEL_WIDTH,
        panel_height=VIRTUAL_HEIGHT,
        ui_assets=asset_manager.ui_assets,
        scale_factor=scale_factor
    )

    game = GameController(
        asset_manager=asset_manager,
        ui_controller=ui,
        sound_manager=sound_manager,
        world_width=WORLD_WIDTH,
        world_height=VIRTUAL_HEIGHT,
        scale_factor=scale_factor
    )

    # --- МЕНЮ ---
    state = STATE_MENU
    running = True

    # Проверка сохранения
    has_save = False
    save_path = game.get_save_path()
    if os.path.exists(save_path):
        if game.load_game():
            has_save = True
        else:
            try:
                os.remove(save_path)
            except:
                pass

    menu_coins = []

    def spawn_menu_coins():
        menu_coins.clear()

        def add_batch(tex_dict, count, scale):
            tex = tex_dict.get("heads")
            if tex:
                for _ in range(count):
                    x = random.randint(50, int(VIRTUAL_WIDTH - 50))
                    y = random.randint(50, int(VIRTUAL_HEIGHT - 50))
                    menu_coins.append(MenuCoin(x, y, tex, tex, scale))

        add_batch(asset_manager.bronze_coin_sprites, 15, 0.8)
        add_batch(asset_manager.silver_coin_sprites, 8, 1.0)
        add_batch(asset_manager.gold_coin_sprites, 4, 1.2)

    spawn_menu_coins()

    # Кнопки меню
    btn_w, btn_h = 300, 70
    cx, cy = VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2
    btn_play_rect = pygame.Rect(cx - btn_w // 2, cy, btn_w, btn_h)
    btn_help_rect = pygame.Rect(cx - btn_w // 2, cy + 90, btn_w, btn_h)
    btn_exit_rect = pygame.Rect(cx - btn_w // 2, cy + 180, btn_w, btn_h)

    show_help = False
    help_scroll_y = 0
    help_w, help_h = 600, 400

    # --- ГЛАВНЫЙ ЦИКЛ ---
    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.1: dt = 0.1

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if state == STATE_GAME: game.save_game()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                vmx = mx * (VIRTUAL_WIDTH / screen.get_width())
                vmy = my * (VIRTUAL_HEIGHT / screen.get_height())

                if state == STATE_MENU:
                    if show_help:
                        # Логика закрытия окна помощи
                        help_x = (VIRTUAL_WIDTH - help_w) // 2
                        help_y = (VIRTUAL_HEIGHT - help_h) // 2
                        close_btn_size = 30
                        # Кнопка X (справа вверху внутри окна)
                        close_rect = pygame.Rect(help_x + help_w - close_btn_size - 10, help_y + 10, close_btn_size,
                                                 close_btn_size)

                        if close_rect.collidepoint(vmx, vmy):
                            show_help = False
                            continue  # Важно: не пропускаем клик дальше
                    else:
                        # Логика кнопок главного меню
                        if btn_play_rect.collidepoint(vmx, vmy):
                            state = STATE_GAME
                            if not has_save: game.reset_game()
                        elif btn_help_rect.collidepoint(vmx, vmy):
                            show_help = True
                        elif btn_exit_rect.collidepoint(vmx, vmy):
                            running = False

                elif state == STATE_GAME:
                    logic_y = VIRTUAL_HEIGHT - vmy
                    if event.button == pygame.BUTTON_LEFT:
                        if vmx > WORLD_WIDTH:
                            ui.on_mouse_press(vmx, vmy)
                        else:
                            game.on_mouse_press(vmx, logic_y, pygame.BUTTON_LEFT)
                    elif event.button == pygame.BUTTON_RIGHT:
                        if vmx <= WORLD_WIDTH:
                            game.on_mouse_press_rmb(vmx, logic_y)

            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                vmx = mx * (VIRTUAL_WIDTH / screen.get_width())
                vmy = my * (VIRTUAL_HEIGHT / screen.get_height())
                logic_y = VIRTUAL_HEIGHT - vmy
                if state == STATE_GAME:
                    if event.button == pygame.BUTTON_RIGHT:
                        game.on_mouse_release_rmb(vmx, logic_y)
                    elif event.button == pygame.BUTTON_LEFT:
                        if vmx > WORLD_WIDTH:
                            upgrade_id = ui.on_mouse_release(vmx, vmy)
                            if upgrade_id:
                                if upgrade_id == "finish_game":
                                    game.save_game()
                                    running = False
                                else:
                                    game.try_buy_upgrade(upgrade_id)

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                vmx = mx * (VIRTUAL_WIDTH / screen.get_width())
                vmy = my * (VIRTUAL_HEIGHT / screen.get_height())
                logic_y = VIRTUAL_HEIGHT - vmy
                if state == STATE_GAME:
                    game.on_mouse_motion(vmx, logic_y, event.rel[0] * (VIRTUAL_WIDTH / screen.get_width()),
                                         -event.rel[1] * (VIRTUAL_HEIGHT / screen.get_height()))

            elif event.type == pygame.MOUSEWHEEL:
                mx, my = pygame.mouse.get_pos()
                vmx = mx * (VIRTUAL_WIDTH / screen.get_width())
                vmy = my * (VIRTUAL_HEIGHT / screen.get_height())

                if state == STATE_MENU and show_help:
                    help_scroll_y += event.y * 30
                    if help_scroll_y < 0: help_scroll_y = 0
                elif state == STATE_GAME:
                    if vmx > WORLD_WIDTH:
                        ui.on_mouse_scroll(vmx, vmy, event.y)

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # Обновление (UPDATE)
        if state == STATE_MENU:
            for c in menu_coins:
                c.update(dt, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
            _handle_menu_collisions(menu_coins)  # Физика меню
        elif state == STATE_GAME:
            game.update(dt)
            ui.update(game.balance.get(), game.get_coin_counts())

        # Отрисовка (DRAW)
        canvas.fill((255, 255, 255))  # Белый фон

        if state == STATE_MENU:
            # 1. Рисуем монеты
            for c in menu_coins:
                c.draw(canvas, VIRTUAL_HEIGHT)

            # 2. Полупрозрачная подложка
            overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 50))
            canvas.blit(overlay, (0, 0))

            if not show_help:
                # Заголовок
                title_surf = title_font.render("Incremental Coin Game", True, (0, 0, 0))
                title_rect = title_surf.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT * 0.2))
                canvas.blit(title_surf, title_rect)

                # Кнопки меню
                mx, my = pygame.mouse.get_pos()
                vmx = mx * (VIRTUAL_WIDTH / screen.get_width())
                vmy = my * (VIRTUAL_HEIGHT / screen.get_height())

                buttons = [(btn_play_rect, "Играть"), (btn_help_rect, "Как играть?"), (btn_exit_rect, "Выйти")]
                for rect, text in buttons:
                    color = (100, 100, 100) if rect.collidepoint(vmx, vmy) else (50, 50, 50)
                    pygame.draw.rect(canvas, color, rect, border_radius=5)
                    pygame.draw.rect(canvas, (200, 200, 200), rect, 2, border_radius=5)
                    txt_surf = main_font.render(text, True, (255, 255, 255))
                    txt_rect = txt_surf.get_rect(center=rect.center)
                    canvas.blit(txt_surf, txt_rect)

            else:
                # Окно "Как играть"
                help_x = (VIRTUAL_WIDTH - help_w) // 2
                help_y = (VIRTUAL_HEIGHT - help_h) // 2

                pygame.draw.rect(canvas, (30, 30, 30), (help_x, help_y, help_w, help_h))
                pygame.draw.rect(canvas, (255, 255, 255), (help_x, help_y, help_w, help_h), 2)

                # Текст справки
                help_lines = [
                    "ОСНОВНАЯ ЦЕЛЬ:", "Накапливайте баланс, покупайте улучшения.", "",
                    "ГЕЙМПЛЕЙ:", "Нажмите на монетку, чтобы подбросить её.",
                    "Если выпадет Орел, вы получаете деньги.", "Если Решка - ничего.",
                    "", "СЛИЯНИЕ:", "5 Бронзовых -> 1 Серебряная", "3 Серебряных -> 1 Золотая",
                    "", "Удачи!"
                ]

                # Отрисовка текста с обрезкой
                clip_rect = pygame.Rect(help_x, help_y, help_w, help_h)
                canvas.set_clip(clip_rect)

                text_y = help_y + 20 + help_scroll_y
                for line in help_lines:
                    l_surf = main_font.render(line, True, (200, 200, 200))
                    canvas.blit(l_surf, (help_x + 20, text_y))
                    text_y += 25

                canvas.set_clip(None)

                # Кнопка закрытия (X)
                close_btn_size = 30
                close_rect = pygame.Rect(help_x + help_w - close_btn_size - 10, help_y + 10, close_btn_size,
                                         close_btn_size)
                pygame.draw.rect(canvas, (200, 50, 50), close_rect, border_radius=5)
                x_surf = main_font.render("X", True, (255, 255, 255))
                canvas.blit(x_surf, x_surf.get_rect(center=close_rect.center))

        elif state == STATE_GAME:
            game.draw(canvas, VIRTUAL_HEIGHT)
            ui.draw(canvas, VIRTUAL_HEIGHT, game.balance.get())

        # Масштабирование на весь экран и показ
        pygame.transform.smoothscale(canvas, (screen.get_width(), screen.get_height()), screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()