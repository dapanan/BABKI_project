import pygame
import sys
import os
import random
import math
import time
import asyncio
import platform

from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
from logic.controllers.ui_controller import UIController
from logic.controllers.game_controller import GameController
from logic.assets.sprite_pygame import PygameSprite

import localization
import yandex_helper

# --- CONSTANTS ---
VIRTUAL_WIDTH = 1920
VIRTUAL_HEIGHT = 1080
PANEL_WIDTH = 500
WORLD_WIDTH = VIRTUAL_WIDTH - PANEL_WIDTH
FPS = 60
TITLE = "COINS"

STATE_MENU = 0
STATE_GAME = 1

DEBUG_MODE = True


# MenuCoin class (same as before)
class MenuCoin(PygameSprite):
    def __init__(self, x, y, sprites_dict, scale=1.0):
        start_face = random.choice(["heads", "tails"])
        start_tex = sprites_dict.get(start_face)
        if not start_tex:
            start_tex = pygame.Surface((64, 64), pygame.SRCALPHA)
            start_tex.fill((255, 0, 0))
        super().__init__(image=start_tex, scale=scale)
        self.center_x = x
        self.center_y = y
        self.sprites = sprites_dict
        self.base_width = start_tex.get_width()
        self.radius = (self.base_width * scale) * 0.45
        speed = 150 * scale
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.is_moving = False
        self.anim = []
        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.05
        self.timer = 0.0
        self.next_action_time = random.uniform(0, 8.0)
        self.is_cooldown = False

    def update(self, dt, width, height):
        if not self.is_moving:
            self.timer += dt
            if self.is_cooldown:
                if self.timer >= 4.0:
                    self.is_cooldown = False
                    self.timer = 0.0
                    self.next_action_time = random.uniform(0, 8.0)
            else:
                if self.timer >= self.next_action_time:
                    self._do_toss()

        if self.is_moving:
            self.center_x += self.vx * dt
            self.center_y += self.vy * dt
            if self.left < 0:
                self.left = 0
                self.vx = abs(self.vx)
            elif self.right > width:
                self.right = width
                self.vx = -abs(self.vx)
            if self.bottom < 0:
                self.bottom = 0
                self.vy = abs(self.vy)
            elif self.top > height:
                self.top = height
                self.vy = -abs(self.vy)
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_index += 1
                if self.anim_index >= len(self.anim):
                    self.land()
        else:
            self.center_x += self.vx * dt
            self.center_y += self.vy * dt
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

    def _do_toss(self):
        self.is_moving = True
        force = random.uniform(600, 900)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * force
        self.vy = math.sin(angle) * force
        self._select_flying_animation()
        self.anim_index = 0
        self.anim_timer = 0

    def land(self):
        self.is_moving = False
        if random.random() < 0.5:
            self.texture = self.sprites.get("heads")
        else:
            self.texture = self.sprites.get("tails")
        self.is_cooldown = True
        self.timer = 0.0

    def _select_flying_animation(self):
        if abs(self.vx) > 1.5 * abs(self.vy):
            self.anim = self.sprites.get("right", []) if self.vx > 0 else self.sprites.get("left", [])
        elif abs(self.vy) > 1.5 * abs(self.vx):
            self.anim = self.sprites.get("up", []) if self.vy > 0 else self.sprites.get("down", [])
        else:
            if self.vx > 0 and self.vy > 0:
                self.anim = self.sprites.get("up_right", [])
            elif self.vx > 0 and self.vy < 0:
                self.anim = self.sprites.get("down_right", [])
            elif self.vx < 0 and self.vy > 0:
                self.anim = self.sprites.get("up_left", [])
            else:
                self.anim = self.sprites.get("down_left", [])
        if not self.anim:
            self.anim = [self.sprites.get("heads")]

    def draw(self, surface, screen_height):
        super().draw(surface, screen_height)


def _handle_menu_collisions(coins):
    n = len(coins)
    for i in range(n):
        for j in range(i + 1, n):
            c1 = coins[i]
            c2 = coins[j]
            if c1.is_moving or c2.is_moving:
                continue
            dx = c2.center_x - c1.center_x
            dy = c2.center_y - c1.center_y
            dist_sq = dx * dx + dy * dy
            min_dist = c1.radius + c2.radius
            if dist_sq < min_dist * min_dist and dist_sq > 0:
                dist = math.sqrt(dist_sq)
                nx = dx / dist
                ny = dy / dist
                overlap = min_dist - dist
                c1.center_x -= nx * overlap * 0.5
                c1.center_y -= ny * overlap * 0.5
                c2.center_x += nx * overlap * 0.5
                c2.center_y += ny * overlap * 0.5
                dvx = c1.vx - c2.vx
                dvy = c1.vy - c2.vy
                dot = dvx * nx + dvy * ny
                if dot > 0:
                    c1.vx -= dot * nx
                    c1.vy -= dot * ny
                    c2.vx += dot * nx
                    c2.vy += dot * ny


def render_gradient_text(text, font, outline_color):
    text_surf = font.render(text, True, (255, 255, 255))
    w, h = text_surf.get_size()
    final_surf = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx != 0 or dy != 0:
                temp = font.render(text, True, outline_color)
                final_surf.blit(temp, (dx + 2, dy + 2))
    colors = [(255, 235, 200), (255, 235, 150), (255, 215, 0), (218, 165, 32)]
    stripe_h = h // len(colors)
    if stripe_h < 1: stripe_h = 1
    for i, color in enumerate(colors):
        y_start = 2 + (i * stripe_h)
        rect_h = h - (i * stripe_h) if i == len(colors) - 1 else stripe_h
        clip_rect = pygame.Rect(2, y_start, w, rect_h)
        final_surf.set_clip(clip_rect)
        temp = font.render(text, True, color)
        final_surf.blit(temp, (2, 2))
    final_surf.set_clip(None)
    return final_surf


def draw_text_outline(surf, text, font, color, outline_color, x, y):
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                txt = font.render(text, True, outline_color)
                surf.blit(txt, (x + dx, y + dy))
    txt = font.render(text, True, color)
    surf.blit(txt, (x, y))


async def main():
    pygame.init()

    # FIX: Larger buffer for stability in browser
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=8192)
    pygame.mixer.init()
    pygame.mixer.set_num_channels(16)

    yandex_helper.initialize_environment()

    # Screen setup
    if platform.system() == "Emscripten":
        screen_width = 1920
        screen_height = 1080
        screen = pygame.display.set_mode((screen_width, screen_height))
    else:
        info = pygame.display.Info()
        screen_width = int(info.current_w * 0.8)
        screen_height = int(info.current_h * 0.8)
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

    pygame.display.set_caption(TITLE)

    canvas = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    clock = pygame.time.Clock()

    print("Initializing Managers...")
    asset_manager = AssetManager()
    asset_manager.load_all()
    asset_manager.load_ui_assets()

    sound_manager = SoundManager()
    sound_manager.load_all()

    font_path = asset_manager.ui_assets.get("font_name", "Arial")
    try:
        if font_path != "Arial" and os.path.exists(font_path):
            main_font = pygame.font.Font(font_path, 20)
            title_font = pygame.font.Font(font_path, 40)
            logo_font = pygame.font.Font(font_path, 90)
        else:
            main_font = pygame.font.SysFont("Arial", 20)
            title_font = pygame.font.SysFont("Arial", 40)
            logo_font = pygame.font.SysFont("Arial", 90)
    except:
        main_font = pygame.font.SysFont("Arial", 20)
        title_font = pygame.font.SysFont("Arial", 40)
        logo_font = pygame.font.SysFont("Arial", 90)

    try:
        prestige_font = pygame.font.Font(font_path, 32) if font_path != "Arial" and os.path.exists(
            font_path) else pygame.font.SysFont("Arial", 32)
        help_font = pygame.font.Font(font_path, 24) if font_path != "Arial" and os.path.exists(
            font_path) else pygame.font.SysFont("Arial", 24)
        dialog_font = pygame.font.Font(font_path, 28) if font_path != "Arial" and os.path.exists(
            font_path) else pygame.font.SysFont("Arial", 28)
    except:
        prestige_font = pygame.font.SysFont("Arial", 32)
        help_font = pygame.font.SysFont("Arial", 24)
        dialog_font = pygame.font.SysFont("Arial", 28)

    # FIX: Pre-render heavy assets
    logo_surf = render_gradient_text("COINS", logo_font, (0, 0, 0))
    menu_overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
    menu_overlay.fill((0, 0, 0, 50))

    # FIX: Pre-render menu buttons text
    # We create a small cache for text
    text_cache = {}

    def get_cached_text(text, font, color=(255, 255, 255)):
        key = (text, color)
        if key not in text_cache:
            text_cache[key] = font.render(text, True, color)
        return text_cache[key]

    scale_factor = 1.0
    ui = UIController(
        panel_x=WORLD_WIDTH, panel_width=PANEL_WIDTH, panel_height=VIRTUAL_HEIGHT,
        ui_assets=asset_manager.ui_assets, scale_factor=scale_factor
    )

    game = GameController(
        asset_manager=asset_manager, ui_controller=ui, sound_manager=sound_manager,
        world_width=WORLD_WIDTH, world_height=VIRTUAL_HEIGHT, scale_factor=scale_factor
    )

    game.is_mobile_device = yandex_helper.is_mobile()
    print(f"Is Mobile Device: {game.is_mobile_device}")

    state = STATE_MENU
    running = True
    has_save = False
    if game.load_game():
        has_save = True

    menu_coins = []

    def spawn_menu_coins():
        menu_coins.clear()

        def add_batch(sprites_dict, count, scale):
            if not sprites_dict: return
            for _ in range(count):
                x = random.randint(100, int(VIRTUAL_WIDTH - 100))
                y = random.randint(100, int(VIRTUAL_HEIGHT - 100))
                menu_coins.append(MenuCoin(x, y, sprites_dict, scale))

        add_batch(asset_manager.bronze_coin_sprites, 15, 0.8)
        add_batch(asset_manager.silver_coin_sprites, 8, 1.0)
        add_batch(asset_manager.gold_coin_sprites, 4, 1.2)

    spawn_menu_coins()

    btn_w, btn_h = 300, 70
    cx, cy = VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2
    btn_play_rect = pygame.Rect(cx - btn_w // 2, cy, btn_w, btn_h)
    btn_help_rect = pygame.Rect(cx - btn_w // 2, cy + 90, btn_w, btn_h)

    settings_btn_w = 100
    settings_btn_h = 50
    settings_margin = 20
    btn_lang_rect = pygame.Rect(VIRTUAL_WIDTH - settings_btn_w - settings_margin, settings_margin, settings_btn_w,
                                settings_btn_h)
    btn_sound_rect = pygame.Rect(VIRTUAL_WIDTH - (settings_btn_w * 2) - (settings_margin * 2), settings_margin,
                                 settings_btn_w, settings_btn_h)

    game_btn_w = 110
    game_btn_h = 50
    game_btn_margin = 20
    game_mute_rect = pygame.Rect(VIRTUAL_WIDTH - game_btn_w - game_btn_margin, game_btn_margin, game_btn_w, game_btn_h)
    game_lang_rect = pygame.Rect(VIRTUAL_WIDTH - (game_btn_w * 2) - (game_btn_margin * 2), game_btn_margin, game_btn_w,
                                 game_btn_h)

    show_help = False
    help_scroll_y = 0
    help_w, help_h = 600, 400
    is_dragging_help = False
    help_last_drag_y = 0

    active_dialog = None
    is_dragging_ui = False
    last_drag_y = 0
    potential_click = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        if dt > 0.1: dt = 0.1

        if yandex_helper.check_ad_pause():
            dt = 0.0

        mx, my = pygame.mouse.get_pos()
        vmx = int(mx * VIRTUAL_WIDTH / screen_width)
        vmy = int(my * VIRTUAL_HEIGHT / screen_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if state == STATE_GAME: game.save_game()
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if state == STATE_MENU:
                    if show_help:
                        help_x = (VIRTUAL_WIDTH - help_w) // 2
                        help_y = (VIRTUAL_HEIGHT - help_h) // 2
                        close_rect = pygame.Rect(help_x + help_w - 40, help_y + 10, 30, 30)
                        if close_rect.collidepoint(vmx, vmy):
                            show_help = False
                            continue
                        help_rect = pygame.Rect(help_x, help_y, help_w, help_h)
                        if help_rect.collidepoint(vmx, vmy):
                            is_dragging_help = True
                            help_last_drag_y = vmy
                    else:
                        if btn_play_rect.collidepoint(vmx, vmy):
                            state = STATE_GAME
                            if not has_save: game.reset_game()
                        elif btn_help_rect.collidepoint(vmx, vmy):
                            show_help = True
                        elif btn_lang_rect.collidepoint(vmx, vmy):
                            localization.toggle_language()
                            ui.reload_texts()
                            text_cache.clear()  # Clear cache on lang change
                        elif btn_sound_rect.collidepoint(vmx, vmy):
                            sound_manager.toggle_mute()

                elif state == STATE_GAME:
                    if active_dialog:
                        dialog_w, dialog_h = 500, 250
                        dialog_x = (VIRTUAL_WIDTH - dialog_w) // 2
                        dialog_y = (VIRTUAL_HEIGHT - dialog_h) // 2
                        btn_w_d, btn_h_d = 120, 50
                        btn_yes = pygame.Rect(dialog_x + 50, dialog_y + dialog_h - 70, btn_w_d, btn_h_d)
                        btn_no = pygame.Rect(dialog_x + dialog_w - 170, dialog_y + dialog_h - 70, btn_w_d, btn_h_d)
                        btn_close_d = pygame.Rect(dialog_x + dialog_w - 40, dialog_y + 10, 30, 30)

                        if event.button == pygame.BUTTON_LEFT:
                            if btn_yes.collidepoint(vmx, vmy):
                                if active_dialog == 'prestige':
                                    game.perform_prestige()
                                elif active_dialog == 'new_game':
                                    game.reset_game(hard_reset=False)
                                active_dialog = None
                            elif btn_no.collidepoint(vmx, vmy) or btn_close_d.collidepoint(vmx, vmy):
                                active_dialog = None
                        continue

                    logic_y = VIRTUAL_HEIGHT - vmy

                    if event.button == pygame.BUTTON_LEFT:
                        if game.grab_purchased and game.is_mobile_device:
                            grab_btn_rect = pygame.Rect(game_lang_rect.x - 120, game_btn_margin, 100, game_btn_h)
                            if grab_btn_rect.collidepoint(vmx, vmy):
                                game.grab_mode_active = not game.grab_mode_active
                                continue

                        if game_mute_rect.collidepoint(vmx, vmy):
                            sound_manager.toggle_mute()
                        elif game_lang_rect.collidepoint(vmx, vmy):
                            localization.toggle_language()
                            ui.reload_texts()
                            text_cache.clear()
                        elif vmx > WORLD_WIDTH:
                            ui.on_mouse_press(vmx, vmy)
                            pressed_id = ui.get_pressed_button_id()
                            if pressed_id:
                                if ui.is_button_enabled(pressed_id):
                                    potential_click = True
                                else:
                                    potential_click = False
                                    is_dragging_ui = True
                                    last_drag_y = vmy
                                    ui.cancel_press()
                            else:
                                potential_click = False
                                is_dragging_ui = True
                                last_drag_y = vmy
                        else:
                            game.on_mouse_press(vmx, logic_y, pygame.BUTTON_LEFT)

                    elif event.button == pygame.BUTTON_RIGHT:
                        if vmx <= WORLD_WIDTH:
                            game.on_mouse_press_rmb(vmx, logic_y)

            elif event.type == pygame.MOUSEBUTTONUP:
                if state == STATE_MENU:
                    is_dragging_help = False
                if state == STATE_GAME and not active_dialog:
                    logic_y = VIRTUAL_HEIGHT - vmy
                    if event.button == pygame.BUTTON_RIGHT:
                        game.on_mouse_release_rmb(vmx, logic_y)
                    elif event.button == pygame.BUTTON_LEFT:
                        if game.grab_purchased and game.grab_mode_active:
                            if game.grabbed_coin:
                                game.on_mouse_release_rmb(vmx, logic_y)
                            else:
                                game.on_mouse_press_rmb(vmx, logic_y)
                            continue

                        is_dragging_ui = False
                        if potential_click:
                            potential_click = False
                            if vmx > WORLD_WIDTH:
                                if not (game_mute_rect.collidepoint(vmx, vmy) or game_lang_rect.collidepoint(vmx, vmy)):
                                    upgrade_id = ui.on_mouse_release(vmx, vmy)
                                    if upgrade_id:
                                        if upgrade_id == "prestige":
                                            if game.prestige.can_prestige(): active_dialog = 'prestige'
                                        elif upgrade_id == "new_game":
                                            active_dialog = 'new_game'
                                        elif upgrade_id == "exit_to_menu":
                                            game.save_game()
                                            state = STATE_MENU
                                            has_save = True
                                        elif upgrade_id == "finish_game":
                                            game.save_game()
                                            running = False
                                        elif upgrade_id == "watch_ad":
                                            yandex_helper.show_rewarded_ad()
                                        else:
                                            game.try_buy_upgrade(upgrade_id)

            elif event.type == pygame.MOUSEMOTION:
                if state == STATE_MENU and show_help and is_dragging_help:
                    dy = vmy - help_last_drag_y
                    help_scroll_y -= dy
                    help_last_drag_y = vmy
                    h_keys = ["help_goal", "help_goal_text", "", "help_gameplay", "help_gameplay_text", "",
                              "help_special", "help_special_text", "", "help_entities", "help_entities_text", "",
                              "help_prestige", "help_prestige_text", "", "help_fusion", "help_fusion_text", "",
                              "help_luck"]
                    lines_count = 0
                    for key in h_keys:
                        txt = localization.get_text(key)
                        if txt:
                            lines_count += txt.count("\n") + 1
                        else:
                            lines_count += 1
                    total_text_height = lines_count * 25
                    max_scroll = total_text_height - help_h + 20
                    if max_scroll < 0: max_scroll = 0
                    if help_scroll_y < 0: help_scroll_y = 0
                    if help_scroll_y > max_scroll: help_scroll_y = max_scroll

                if state == STATE_GAME and not active_dialog:
                    logic_y = VIRTUAL_HEIGHT - vmy
                    if is_dragging_ui:
                        dy = vmy - last_drag_y
                        ui.on_mouse_scroll(vmx, vmy, dy * 0.05)
                        last_drag_y = vmy
                    elif potential_click:
                        distance = math.sqrt(event.rel[0] ** 2 + event.rel[1] ** 2)
                        if distance > 5:
                            potential_click = False
                            is_dragging_ui = True
                            last_drag_y = vmy
                            ui.cancel_press()
                    else:
                        dx = int(event.rel[0] * (VIRTUAL_WIDTH / screen_width))
                        dy = int(-event.rel[1] * (VIRTUAL_HEIGHT / screen_height))
                        game.on_mouse_motion(vmx, logic_y, dx, dy)

            elif event.type == pygame.MOUSEWHEEL:
                if state == STATE_MENU and show_help:
                    help_scroll_y -= event.y * 30
                    h_keys = ["help_goal", "help_goal_text", "", "help_gameplay", "help_gameplay_text", "",
                              "help_special", "help_special_text", "", "help_entities", "help_entities_text", "",
                              "help_prestige", "help_prestige_text", "", "help_fusion", "help_fusion_text", "",
                              "help_luck"]
                    lines_count = 0
                    for key in h_keys:
                        txt = localization.get_text(key)
                        if txt:
                            lines_count += txt.count("\n") + 1
                        else:
                            lines_count += 1
                    total_text_height = lines_count * 25
                    max_scroll = total_text_height - help_h + 20
                    if max_scroll < 0: max_scroll = 0
                    if help_scroll_y < 0: help_scroll_y = 0
                    if help_scroll_y > max_scroll: help_scroll_y = max_scroll
                elif state == STATE_GAME and not active_dialog:
                    if vmx > WORLD_WIDTH:
                        ui.on_mouse_scroll(vmx, vmy, event.y)

            elif event.type == pygame.VIDEORESIZE:
                if platform.system() != "Emscripten":
                    screen_width = event.w
                    screen_height = event.h
                    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

        # UPDATE
        if state == STATE_MENU:
            for c in menu_coins:
                c.update(dt, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
            _handle_menu_collisions(menu_coins)
        elif state == STATE_GAME:
            game.update(dt)
            ui.update(game.balance.get(), game.get_coin_counts())
            if yandex_helper.check_and_reset_reward():
                reward_amount = max(1000, int(game.balance.get() * 0.1))
                game.balance.add(reward_amount)
                print(f"Reward granted: +{reward_amount}")
                ui.mark_ad_watched()
            yandex_helper.show_interstitial_ad()

        # DRAW
        canvas.fill((255, 255, 255))

        if state == STATE_MENU:
            sorted_coins = sorted(menu_coins, key=lambda c: c.is_moving)
            for c in sorted_coins:
                c.draw(canvas, VIRTUAL_HEIGHT)

            canvas.blit(menu_overlay, (0, 0))

            if not show_help:
                logo_rect = logo_surf.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT * 0.2))
                canvas.blit(logo_surf, logo_rect)

                buttons = [(btn_play_rect, localization.get_text("btn_play")),
                           (btn_help_rect, localization.get_text("btn_help"))]
                for rect, text in buttons:
                    color = (100, 100, 100) if rect.collidepoint(vmx, vmy) else (50, 50, 50)
                    pygame.draw.rect(canvas, color, rect, border_radius=5)
                    pygame.draw.rect(canvas, (200, 200, 200), rect, 2, border_radius=5)
                    # FIX: Use cached text
                    txt_surf = get_cached_text(text, main_font)
                    txt_rect = txt_surf.get_rect(center=rect.center)
                    canvas.blit(txt_surf, txt_rect)

                lang_key = "lang_" + localization.current_lang
                lang_text = localization.get_text(lang_key)
                sound_state = "ON" if not sound_manager.muted else "OFF"
                sound_text_final = f"SOUND: {sound_state}"
                for rect, text in [(btn_lang_rect, lang_text), (btn_sound_rect, sound_text_final)]:
                    color = (70, 70, 70) if rect.collidepoint(vmx, vmy) else (50, 50, 50)
                    pygame.draw.rect(canvas, color, rect, border_radius=5)
                    pygame.draw.rect(canvas, (150, 150, 150), rect, 2, border_radius=5)
                    txt_surf = get_cached_text(text, main_font)
                    txt_rect = txt_surf.get_rect(center=rect.center)
                    canvas.blit(txt_surf, txt_rect)
            else:
                # Help Menu (rendering text here is fine because it's not animating)
                help_x = (VIRTUAL_WIDTH - help_w) // 2
                help_y = (VIRTUAL_HEIGHT - help_h) // 2
                pygame.draw.rect(canvas, (30, 30, 30), (help_x, help_y, help_w, help_h))
                pygame.draw.rect(canvas, (255, 255, 255), (help_x, help_y, help_w, help_h), 2)
                help_lines = [localization.get_text("help_goal"), localization.get_text("help_goal_text"), "",
                              localization.get_text("help_gameplay"), localization.get_text("help_gameplay_text"), "",
                              localization.get_text("help_special"), localization.get_text("help_special_text"), "",
                              localization.get_text("help_entities"), localization.get_text("help_entities_text"), "",
                              localization.get_text("help_prestige"), localization.get_text("help_prestige_text"), "",
                              localization.get_text("help_fusion"), localization.get_text("help_fusion_text"), "",
                              localization.get_text("help_luck")]
                clip_rect = pygame.Rect(help_x, help_y, help_w, help_h)
                canvas.set_clip(clip_rect)
                text_y = help_y + 20 - help_scroll_y
                for line in help_lines:
                    if "\n" in line:
                        parts = line.split("\n")
                        for part in parts:
                            l_surf = help_font.render(part, True, (200, 200, 200))
                            canvas.blit(l_surf, (help_x + 20, text_y))
                            text_y += 25
                    else:
                        l_surf = help_font.render(line, True, (200, 200, 200))
                        canvas.blit(l_surf, (help_x + 20, text_y))
                    text_y += 25
                canvas.set_clip(None)
                arrow_x = help_x + help_w - 30
                arrow_y = help_y + help_h - 30
                points = [(arrow_x, arrow_y + 12), (arrow_x - 10, arrow_y), (arrow_x + 10, arrow_y)]
                pygame.draw.polygon(canvas, (200, 200, 200), points)
                close_btn_size = 30
                close_rect = pygame.Rect(help_x + help_w - close_btn_size - 10, help_y + 10, close_btn_size,
                                         close_btn_size)
                pygame.draw.rect(canvas, (200, 50, 50), close_rect, border_radius=5)
                x_surf = main_font.render(localization.get_text("btn_close"), True, (255, 255, 255))
                canvas.blit(x_surf, x_surf.get_rect(center=close_rect.center))

        elif state == STATE_GAME:
            game.draw(canvas, VIRTUAL_HEIGHT)
            ui.draw(canvas, VIRTUAL_HEIGHT, game.balance.get())

            lang_key = "lang_" + localization.current_lang
            lang_text = localization.get_text(lang_key)
            lang_color = (80, 80, 80) if game_lang_rect.collidepoint(vmx, vmy) else (60, 60, 60)
            pygame.draw.rect(canvas, lang_color, game_lang_rect, border_radius=5)
            pygame.draw.rect(canvas, (150, 150, 150), game_lang_rect, 2, border_radius=5)
            lang_surf = main_font.render(lang_text, True, (255, 255, 255))
            canvas.blit(lang_surf, lang_surf.get_rect(center=game_lang_rect.center))

            sound_state_key = "sound_on" if not sound_manager.muted else "sound_off"
            sound_text = localization.get_text(sound_state_key)
            sound_color = (80, 80, 80) if game_mute_rect.collidepoint(vmx, vmy) else (60, 60, 60)
            pygame.draw.rect(canvas, sound_color, game_mute_rect, border_radius=5)
            pygame.draw.rect(canvas, (150, 150, 150), game_mute_rect, 2, border_radius=5)
            sound_surf = main_font.render(sound_text, True, (255, 255, 255))
            canvas.blit(sound_surf, sound_surf.get_rect(center=game_mute_rect.center))

            pres_template = localization.get_text("prestige_level_text")
            prestige_text = pres_template.format(game.prestige.points, round(game.prestige.multiplier, 1))
            draw_text_outline(canvas, prestige_text, prestige_font, (255, 255, 255), (0, 0, 0), 20, 15)

            if DEBUG_MODE:
                pass  # Skip debug logic for performance

            if active_dialog:
                overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 38))
                canvas.blit(overlay, (0, 0))

                dialog_w, dialog_h = 500, 250
                dialog_x = (VIRTUAL_WIDTH - dialog_w) // 2
                dialog_y = (VIRTUAL_HEIGHT - dialog_h) // 2
                pygame.draw.rect(canvas, (40, 40, 40), (dialog_x, dialog_y, dialog_w, dialog_h), border_radius=10)
                pygame.draw.rect(canvas, (200, 200, 200), (dialog_x, dialog_y, dialog_w, dialog_h), 2, border_radius=10)
                if active_dialog == 'prestige':
                    title = localization.get_text("dialog_prestige_title")
                    text = localization.get_text("dialog_prestige_text")
                else:
                    title = localization.get_text("dialog_new_game_title")
                    text = localization.get_text("dialog_new_game_text")
                title_surf = dialog_font.render(title, True, (255, 255, 255))
                title_rect = title_surf.get_rect(center=(dialog_x + dialog_w // 2, dialog_y + 40))
                canvas.blit(title_surf, title_rect)
                text_surf = dialog_font.render(text, True, (200, 200, 200))
                text_rect = text_surf.get_rect(center=(dialog_x + dialog_w // 2, dialog_y + 100))
                canvas.blit(text_surf, text_rect)
                btn_w_d, btn_h_d = 120, 50
                btn_yes = pygame.Rect(dialog_x + 50, dialog_y + dialog_h - 70, btn_w_d, btn_h_d)
                btn_no = pygame.Rect(dialog_x + dialog_w - 170, dialog_y + dialog_h - 70, btn_w_d, btn_h_d)
                btn_close_d = pygame.Rect(dialog_x + dialog_w - 40, dialog_y + 10, 30, 30)
                yes_color = (50, 150, 50) if not btn_yes.collidepoint(vmx, vmy) else (70, 200, 70)
                pygame.draw.rect(canvas, yes_color, btn_yes, border_radius=5)
                yes_txt = main_font.render(localization.get_text("dialog_yes"), True, (255, 255, 255))
                canvas.blit(yes_txt, yes_txt.get_rect(center=btn_yes.center))
                no_color = (150, 50, 50) if not btn_no.collidepoint(vmx, vmy) else (200, 70, 70)
                pygame.draw.rect(canvas, no_color, btn_no, border_radius=5)
                no_txt = main_font.render(localization.get_text("dialog_no"), True, (255, 255, 255))
                canvas.blit(no_txt, no_txt.get_rect(center=btn_no.center))
                pygame.draw.rect(canvas, (200, 50, 50), btn_close_d, border_radius=5)
                x_surf = main_font.render("X", True, (255, 255, 255))
                canvas.blit(x_surf, x_surf.get_rect(center=btn_close_d.center))

            if game.grab_purchased and game.is_mobile_device:
                grab_btn_rect = pygame.Rect(game_lang_rect.x - 120, game_btn_margin, 100, game_btn_h)
                grab_color = (0, 150, 0) if game.grab_mode_active else (80, 80, 80)
                pygame.draw.rect(canvas, grab_color, grab_btn_rect, border_radius=5)
                txt = "GRAB: ON" if game.grab_mode_active else "GRAB: OFF"
                grab_txt = main_font.render(txt, True, (255, 255, 255))
                canvas.blit(grab_txt, grab_txt.get_rect(center=grab_btn_rect.center))

        # SCREEN BLIT
        pygame.transform.smoothscale(canvas, (screen_width, screen_height), screen)
        pygame.display.flip()

        await asyncio.sleep(0)


if __name__ == "__main__":
    import platform

    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())