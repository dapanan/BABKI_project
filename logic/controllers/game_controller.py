import arcade
import random
import math
import json
import os
from logic.world.gold_coin import GoldCoin
from logic.world.bronze_coin import BronzeCoin
from logic.world.silver_coin import SilverCoin
from logic.world.map_activities.wisp import Wisp
from logic.world.map_activities.multiply_zone import MultiplyZone
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
from logic.economy.balance import Balance
from logic.world.map_activities.beetle import Beetle
from logic.world.map_activities.crater import Crater
from logic.world.map_activities.meteor import Meteor
from logic.world.map_activities.explosion import Explosion
from logic.world.map_activities.tornado import Tornado
from logic.world.lucky_coin import LuckyCoin
from logic.world.cursed_coin import CursedCoin


class GameController:
    def __init__(self, asset_manager: AssetManager, ui_controller, sound_manager: SoundManager,
                 world_width: int, world_height: int, scale_factor: float):
        self.assets = asset_manager
        self.balance = Balance()
        self.ui = ui_controller
        self.sound_manager = sound_manager
        self.coins = []
        self.particles = []

        # --- ТОРНАДО ---
        self.tornado = None
        self.tornado_respawn_timer = 0.0
        self.tornado_next_spawn_time = 0.0
        self.tornado_unlocked = False
        self.tornado_cooldown_level = 0
        self.tornado_base_cooldown = 60.0
        self.width = world_width
        self.height = world_height
        self.scale_factor = scale_factor
        self.tornado_list = arcade.SpriteList()

        # --- МЕТЕОРИТ ---
        self.meteor = None
        self.crater = None
        self.explosions = arcade.SpriteList()

        self.meteor_respawn_timer = 0.0
        self.meteor_next_spawn_time = 0.0
        self.meteor_next_spawn_time = random.uniform(10.0, 60.0)

        # --- НАСТРОЙКИ МЕТЕОРИТА ---
        self.meteor_blast_radius = 400.0
        self.meteor_volume = 0.4
        self.meteor_trail_timer = 0.0
        self.meteor_unlocked = False
        self.meteor_cooldown_level = 0

        self.width = world_width
        self.height = world_height
        self.scale_factor = scale_factor

        self.bronze_coin_level = 1
        self.silver_coin_level = 0
        self.gold_coin_level = 0

        self.silver_crit_level = 1
        self.auto_flip_level = 0
        self.auto_flip_timer = 0.0

        self.bronze_value_level = 0
        self.silver_value_level = 0
        self.gold_value_level = 0
        self.wisp_speed_level = 0
        self.wisp_size_level = 0
        self.zone_2_size_level = 0
        self.zone_2_mult_level = 0
        self.zone_5_size_level = 0
        self.zone_5_mult_level = 0

        self.upgrade_prices = {
            "buy_bronze_coin": 50,
            "silver_crit_upgrade": 500,
            "grab_upgrade": 500,
            "gold_explosion_upgrade": 2000,
            "wisp_spawn": 5000,
            "wisp_speed": 1000,
            "wisp_size": 1000,
            "spawn_zone_2": 10000,
            "spawn_zone_5": 50000,
            "upgrade_zone_2_size": 2000,
            "upgrade_zone_5_size": 5000,
            "upgrade_zone_2_mult": 3000,
            "upgrade_zone_5_mult": 7000,
            "spawn_tornado": 15000,
            "tornado_cooldown_upgrade": 2000,
            "auto_flip_upgrade": 500,
            "bronze_value_upgrade": 2000,
            "silver_value_upgrade": 5000,
            "gold_value_upgrade": 10000,
            "spawn_meteor": 15000,
            "meteor_cooldown_upgrade": 2000,
            # === ДОБАВЛЯЕМ КНОПКИ СЛИЯНИЯ В ИНИЦИАЛИЗАЦИЮ ===
            "fuse_to_silver": 0,
            "fuse_to_gold": 0,
        }

        self.has_gold_coin = False
        self.grab_purchased = False
        self.gold_explosion_unlocked = False
        self.grabbed_coin = None

        self.wisp: Wisp | None = None
        self.wisp_list = arcade.SpriteList()

        self.zones: list[MultiplyZone] = []
        self.zone_2: MultiplyZone | None = None
        self.zone_5: MultiplyZone | None = None

        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_dx = 0
        self.mouse_dy = 0
        self.mouse_velocity_history = []
        self.max_history_frames = 8

        self.spawn_special_coin_timer = 0.0  # Таймер спавна специальных монет
        self.spawn_special_coin_interval = 1.0  # Проверяем каждую секунду

        self.start_coin_x = world_width * 0.25
        self.start_coin_y = world_height * 0.5

        self.beetle = None
        self.beetle_respawn_timer = 0.0
        self.beetle_respawn_interval = 0.0
        self.spawn_beetle_initial()

        if not self.load_game():
            self.spawn_coin("bronze")

        # Инициализация Spatial Hash для оптимизации коллизий
        self.spatial_hash = arcade.SpatialHash(cell_size=150)

    def spawn_coin(self, coin_type: str, x: float = None, y: float = None):
        if x is None or y is None:
            w = self.width
            h = self.height
            margin = 100 * self.scale_factor
            x = random.randint(int(margin), int(w - margin))
            y = random.randint(int(margin), int(h - margin))

        if coin_type == "bronze":
            coin = BronzeCoin(x, y, self.assets.bronze_coin_sprites, scale=0.8 * self.scale_factor,
                              scale_factor=self.scale_factor)
            coin.explosion_chance = 0
        elif coin_type == "silver":
            crit_chance = 0.1 * self.silver_crit_level
            coin = SilverCoin(x, y, self.assets.silver_coin_sprites, crit_chance, scale=1.1 * self.scale_factor,
                              scale_factor=self.scale_factor)
            coin.explosion_chance = 0
        elif coin_type == "gold":
            coin = GoldCoin(x, y, self.assets.gold_coin_sprites, scale=1.5 * self.scale_factor,
                            scale_factor=self.scale_factor)
            self.has_gold_coin = True
            if self.gold_explosion_unlocked:
                coin.explosion_chance = 0.5
            else:
                coin.explosion_chance = 0

        elif coin_type == "lucky":
            coin = LuckyCoin(x, y, self.assets.lucky_coin_sprites, scale=1.2 * self.scale_factor, scale_factor=self.scale_factor)
            coin.explosion_chance = 0
        elif coin_type == "cursed":
            coin = CursedCoin(x, y, self.assets.cursed_coin_sprites, scale=1.2 * self.scale_factor, scale_factor=self.scale_factor)
            coin.explosion_chance = 0

        self.coins.append(coin)

    def _get_coin_type_string(self, coin) -> str:
        if isinstance(coin, GoldCoin):
            return "gold"
        elif isinstance(coin, SilverCoin):
            return "silver"
        else:
            return "bronze"

    def update(self, dt: float) -> None:
        width = self.width
        height = self.height

        self.coins = [c for c in self.coins if not (hasattr(c, 'lifetime') and c.lifetime is not None and c.lifetime <= 0)]
        # === ЛОГИКА АВТО-ПЕРЕВОРОТА ===
        if self.auto_flip_level >= 1:
            self.auto_flip_timer += dt
            flip_interval = 5.0 - (self.auto_flip_level - 1) * 0.2
            if flip_interval < 0.5: flip_interval = 0.5

            if self.auto_flip_timer >= flip_interval:
                self.auto_flip_timer = 0

                # === ИСПРАВЛЕНИЕ: Исключаем спец-монетки из переворота ===
                standing_coins = [c for c in self.coins
                                  if not c.is_moving
                                  and not isinstance(c, (LuckyCoin, CursedCoin))]
                # ======================================================

                if standing_coins:
                    coin_to_flip = random.choice(standing_coins)
                    dx = random.randint(-50, 50)
                    dy = random.randint(-50, 50)
                    coin_to_flip.hit(dx, dy)

                    c_type = self._get_coin_type_string(coin_to_flip)
                    self.sound_manager.play_toss(c_type)

        # === ЛОГИКА ТОРНАДО ===
        if self.tornado_unlocked:
            if self.tornado:
                is_alive = self.tornado.update(dt)

                # === ВАЖНО: ТОРНАДО ПРИМЕНЯЕТСЯ ДО ОБНОВЛЕНИЯ МОНЕТОК ===
                # Это нужно для мгновенной реакции и корректной обработки выхода
                for coin in self.coins:
                    self.tornado.affect_coin(coin, dt)
                # ==========================================================

                if not is_alive:
                    self.tornado = None
                    self.tornado_list.clear()

                    for coin in self.coins:
                        coin.tornado_hit = False
                        # Если монетка летела - она должна уже упасть в affect_coin
                        # Но на всякий случай проверяем
                        if coin.is_moving:
                            coin.land()

                    cd = self.tornado_base_cooldown - (self.tornado_cooldown_level * 5.0)
                    if cd < 10.0: cd = 10.0
                    self.tornado_respawn_timer = 0.0
                    self.tornado_next_spawn_time = cd
            else:
                self.tornado_respawn_timer += dt
                if self.tornado_respawn_timer >= self.tornado_next_spawn_time:
                    self.spawn_tornado()
                    self.tornado_respawn_timer = 0.0
        # =======================

        # === ЛОГИКА ЖУКА ===
        if self.beetle:
            is_alive = self.beetle.update(dt, width, height)
            if is_alive is False:
                self.beetle = None
                self.beetle_respawn_interval = random.uniform(180.0, 300.0)
                self.beetle_respawn_timer = 0.0
        else:
            self.beetle_respawn_timer += dt
            if self.beetle_respawn_timer >= self.beetle_respawn_interval:
                self.spawn_beetle()
        # ===========================================

        # === ЛОГИКА СПАВНА СПЕЦИАЛЬНЫХ МОНЕТ ===
        self.spawn_special_coin_timer += dt
        if self.spawn_special_coin_timer >= self.spawn_special_coin_interval:
            self.spawn_special_coin_timer = 0

            # Шанс 0.1% для Lucky (0.001)
            if random.random() < 0.001:
                print("DEBUG: Spawning Lucky Coin!")
                self.spawn_coin("lucky")

            # Шанс 0.01% для Cursed (0.0001)
            elif random.random() < 0.0001:
                self.spawn_coin("cursed")
        # ==========================================

        # === ЛОГИКА МЕТЕОРИТА ===
        if self.meteor_unlocked:

            spawn_smoke = False
            if self.meteor:
                is_trail = self.meteor.update(dt)
                if is_trail and self.meteor.center_y > self.meteor.target_y:
                    spawn_smoke = True

                hit_ground = self.meteor.center_y <= self.meteor.target_y

                if hit_ground:
                    impact_x = self.meteor.center_x
                    impact_y = self.meteor.center_y

                    if self.sound_manager.boom_sound:
                        arcade.play_sound(self.sound_manager.boom_sound, volume=self.meteor_volume)

                    if self.assets.explosion_textures:
                        expl = Explosion(impact_x, impact_y, self.assets.explosion_textures)
                        self.explosions.append(expl)

                    self.create_explosion_particles(impact_x, impact_y)

                    self.crater = Crater(impact_x, impact_y, self.assets.crater_texture)
                    self.crater.multiplier = 10.0
                    self.crater.scale = 1.5

                    for coin in self.coins:
                        dx = impact_x - coin.sprite.center_x
                        dy = impact_y - coin.sprite.center_y
                        dist_sq = dx * dx + dy * dy
                        if dist_sq < (self.meteor_blast_radius * self.meteor_blast_radius):
                            coin.hit(dx, dy)

                    self.meteor = None

            if self.crater:
                is_alive = self.crater.update(dt)
                if not is_alive:
                    self.crater = None
                    max_cd = 2 - (self.meteor_cooldown_level * 30.0)
                    self.meteor_respawn_timer = 0.0
                    self.meteor_next_spawn_time = random.uniform(1, max_cd)
            else:
                self.meteor_respawn_timer += dt
                if self.meteor_respawn_timer >= self.meteor_next_spawn_time:
                    self.spawn_meteor()
                    self.meteor_respawn_timer = 0.0

            if spawn_smoke and self.meteor:
                self.create_particles(self.meteor.center_x, self.meteor.center_y, (100, 100, 100, 150))

            for expl in self.explosions:
                expl.update(dt)
            self.explosions = [e for e in self.explosions if e.alive]
        # ========================================

        if self.grabbed_coin:
            self.grabbed_coin.sprite.center_x = self.mouse_x
            self.grabbed_coin.sprite.center_y = self.mouse_y
            self.grabbed_coin.vx = 0
            self.grabbed_coin.vy = 0

        # === ОПТИМИЗАЦИЯ: Spatial Hash ===
        # Пересоздаем хеш каждый кадр (так как монеты двигаются)
        self.spatial_hash = arcade.SpatialHash(cell_size=150)
        for coin in self.coins:
            self.spatial_hash.add(coin.sprite)

        # Обновление монеток (физика, анимации)
        for coin in self.coins:
            # Проверка на смерть монеты
            if coin.lifetime is not None and coin.lifetime <= 0:
                continue  # Пропускаем удаленные монеты

            if coin is self.grabbed_coin: continue

        # === ОБНОВЛЕНИЕ МОНЕТОК И СОБЫТИЙ ===
        for coin in self.coins:
            if coin is self.grabbed_coin: continue

            # Получаем соседей через Spatial Hash
            nearby_sprites = self.spatial_hash.get_sprites_near_point((coin.sprite.center_x, coin.sprite.center_y))
            nearby_coins = []
            for spr in nearby_sprites:
                if hasattr(spr, 'coin') and spr.coin is not coin:
                    nearby_coins.append(spr.coin)

            # Обновляем физику монетки
            coin.update(dt, width, height, nearby_coins)

            # === ПРОВЕРКА ПРИЗЕМЛЕНИЯ И ВЫДАЧА НАГРАДЫ ===
            outcome = coin.check_land_event()
            if outcome > 0:
                total_multiplier = 1.0
                # (Здесь может быть логика зон, если она у тебя есть)
                final_value = int(outcome * total_multiplier)
                self.balance.add(final_value)

                # Критический эффект серебра
                is_crit_now = False
                if isinstance(coin, SilverCoin) and coin.is_crit:
                    is_crit_now = True
                    coin.is_crit = False

                if is_crit_now:
                    self.create_particles(coin.sprite.center_x, coin.sprite.center_y, (192, 192, 192, 255), coin)
            # === ЛОГИКА СПЕЦ МОНЕТ ===

            # Lucky Coin
            if isinstance(coin, LuckyCoin):
                # === ИСПРАВЛЕНИЕ: Обрабатываем только если монетка УЖЕ ПРИЗЕМЛИЛАСЬ ===
                if coin.landed:
                    if outcome > 0 and not coin.sound_played:
                        current_balance = self.balance.get()
                        new_balance = current_balance * 5
                        self.balance.set(new_balance)
                        if self.sound_manager.lucky_success:
                            arcade.play_sound(self.sound_manager.lucky_success, volume=0.3)
                        coin.sound_played = True

                    elif outcome == 0 and not coin.sound_played:
                        # === ИСПРАВЛЕНИЕ: Звук падения золотой монетки ===
                        c_type = "gold"
                        self.sound_manager.play_land(c_type)
                        # ==================================================
                        coin.sound_played = True

            # Cursed Coin
            elif isinstance(coin, CursedCoin):

                # УСПЕХ (Орел)
                if outcome > 0 and not coin.sound_played:
                    current_balance = self.balance.get()
                    new_balance = current_balance * 100
                    self.balance.set(new_balance)
                    if self.sound_manager.cursed_success:
                        arcade.play_sound(self.sound_manager.cursed_success, volume=0.3)
                    coin.sound_played = True

                # ПРОВАЛ (Решка)
                if coin.bankruptcy_triggered:
                    if self.sound_manager.cursed_fail:
                        arcade.play_sound(self.sound_manager.cursed_fail, volume=0.3)

                    cx, cy = coin.sprite.center_x, coin.sprite.center_y

                    self.balance.set(0)
                    print("DEBUG: CURSED COIN TOOK ALL MONEY!")

                    self.create_explosion_particles(cx, cy)

                    for c in self.coins:
                        if c is not coin:
                            dx = c.sprite.center_x - cx
                            dy = c.sprite.center_y - cy
                            dist_sq = dx * dx + dy * dy
                            if dist_sq > 0:
                                dist = math.sqrt(dist_sq)
                                force = 2000.0 * (1.0 - min(dist / 1000.0, 0.5))
                                nx = dx / dist
                                ny = dy / dist
                                c.vx += nx * force
                                c.vy += ny * force
                                c.is_moving = True
                                c._select_flying_animation()

                    coin.bankruptcy_triggered = False
                    coin.sound_played = True

            # === ОБЫЧНЫЕ ЗВУКИ ПЕРЕБРАСЫВАНИЯ ===
            if coin.needs_toss_sound:
                c_type = self._get_coin_type_string(coin)
                self.sound_manager.play_toss(c_type)
                coin.needs_toss_sound = False

            if coin.landed:
                c_type = self._get_coin_type_string(coin)
                self.sound_manager.play_land(c_type)
                coin.landed = False
        # ==========================================

        if self.wisp:
            self.wisp.update(dt, width, height, self.coins, self.grabbed_coin)

        for zone in self.zones:
            zone.update(dt, width, height)

        for expl in self.explosions:
            expl.update(dt)

        self.explosions = [e for e in self.explosions if e.alive]

        for p in self.particles:
            decay_speed = p.get('decay_speed', 1.0)
            p['life'] -= dt * decay_speed
            if 'linked_coin' in p and p['linked_coin'] is not None:
                p['offset_x'] += p['vx'] * dt
                p['offset_y'] += p['vy'] * dt
                p['x'] = p['linked_coin'].sprite.center_x + p['offset_x']
                p['y'] = p['linked_coin'].sprite.center_y + p['offset_y']
            else:
                p['x'] += p['vx'] * dt
                p['y'] += p['vy'] * dt

        self.particles = [p for p in self.particles if p['life'] > 0]
        self.ui.update_grab_state(self.has_gold_coin, self.grab_purchased)
        self.ui.update_explosion_state(self.gold_explosion_unlocked)
        self.ui.update_wisp_state(self.wisp is not None)
        self.ui.update_zone_state(
            has_zone_2=(self.zone_2 is not None),
            has_zone_5=(self.zone_5 is not None)
        )
        self.ui.update(self.balance.get(), self.get_coin_counts())

    def draw(self) -> None:
        for zone in self.zones:
            zone.draw()

        if self.beetle:
            self.beetle.draw()

        if self.crater:
            self.crater.draw()

        for coin in self.coins:
            if not coin.is_moving: coin.draw()
        for coin in self.coins:
            if coin.is_moving: coin.draw()

        self.wisp_list.draw()

        for expl in self.explosions:
            expl.draw()

        self.tornado_list.draw()

        if self.meteor:
            self.meteor.draw()

        for p in self.particles:
            alpha = int(255 * (p['life'] / 1.0))
            current_color = (p['color'][0], p['color'][1], p['color'][2], alpha)
            arcade.draw_circle_filled(p['x'], p['y'], p['size'], current_color)

    def on_mouse_press(self, x: int, y: int, button: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            if x < self.width:
                clicked_coin = False
                for coin in self.coins:
                    # === ИСПРАВЛЕНИЕ: НЕЛЬЗЯ НАЖАТЬ НА ЛЕТЯЩИЕ ===
                    if not coin.is_moving and coin is not self.grabbed_coin:
                        # ========================================================
                        dx = x - coin.sprite.center_x
                        dy = y - coin.sprite.center_y
                        if dx * dx + dy * dy < (coin.radius * coin.radius):
                            # Проверяем, не была ли уже использована спец-монетка
                            is_special_used = isinstance(coin, (LuckyCoin, CursedCoin)) and getattr(coin, 'is_used',
                                                                                                    False)

                            if not is_special_used:
                                coin.hit(dx, dy)
                                c_type = self._get_coin_type_string(coin)
                                self.sound_manager.play_toss(c_type)
                                clicked_coin = True
                                break

                if not clicked_coin and self.beetle and self.beetle.can_be_clicked:
                    dx = x - self.beetle.center_x
                    dy = y - self.beetle.center_y
                    hit_radius = self.beetle.width / 2
                    if dx * dx + dy * dy < (hit_radius * hit_radius):
                        self.kill_beetle()

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.mouse_x = x
        self.mouse_y = y
        self.mouse_velocity_history.append((dx, dy))
        if len(self.mouse_velocity_history) > self.max_history_frames:
            self.mouse_velocity_history.pop(0)

    def on_mouse_press_rmb(self, x: int, y: int) -> None:
        if not self.grab_purchased: return
        for coin in self.coins:
            if isinstance(coin, GoldCoin) and not coin.is_moving:
                dx = x - coin.sprite.center_x
                dy = y - coin.sprite.center_y
                if dx * dx + dy * dy < (coin.radius * coin.radius):
                    self.grabbed_coin = coin
                    coin.is_moving = True
                    coin.vx = 0
                    coin.vy = 0
                    coin.anim = []
                    coin.fixed_outcome_texture = coin.sprite.texture
                    # УБРАНО manual_override
                    self.mouse_x = x
                    self.mouse_y = y
                    self.mouse_velocity_history = []
                    break

    def on_mouse_release_rmb(self, x: int, y: int) -> None:
        if not self.grabbed_coin: return
        coin = self.grabbed_coin
        self.grabbed_coin = None
        avg_dx = 0
        avg_dy = 0
        count = len(self.mouse_velocity_history)
        if count > 0:
            total_dx = sum(d[0] for d in self.mouse_velocity_history)
            total_dy = sum(d[1] for d in self.mouse_velocity_history)
            avg_dx = total_dx / count
            avg_dy = total_dy / count
        move_threshold = 2.0

        if abs(avg_dx) < move_threshold and abs(avg_dy) < move_threshold:
            coin.vx = 0
            coin.vy = 0
            coin.anim = []
        else:
            # ИСПРАВЛЕНИЕ: Бросок зависит от масштаба экрана
            throw_multiplier = 175.0 * self.scale_factor

            coin.vx = avg_dx * throw_multiplier
            coin.vy = avg_dy * throw_multiplier

            coin._select_flying_animation()
            coin.anim_index = 0
            if coin.anim:
                coin.sprite.texture = self.anim[0]

    def create_particles(self, cx, cy, color=(255, 215, 0, 255), coin=None):
        for _ in range(30):
            gray = random.randint(80, 200)
            base_color = (gray, gray, gray)
            angle = random.uniform(0, 6.28)
            speed = random.uniform(100, 200)
            size = random.uniform(3, 6)
            particle_data = {
                'x': cx, 'y': cy,
                'vx': math.cos(angle) * speed, 'vy': math.sin(angle) * speed,
                'life': 1.0, 'color': base_color, 'size': size
            }
            if coin is not None:
                particle_data['linked_coin'] = coin
                particle_data['decay_speed'] = 3.0
                p_radius = coin.radius
                particle_data['offset_x'] = math.cos(angle) * (p_radius * 0.9)
                particle_data['offset_y'] = math.sin(angle) * (p_radius * 0.9)
            else:
                particle_data['decay_speed'] = 1.0
            self.particles.append(particle_data)

    def try_buy_upgrade(self, upgrade_id: str) -> bool:
        if upgrade_id == "finish_game":
            self.save_game()
            arcade.close_window()
            return True

        if upgrade_id == "new_game":
            self.reset_game()
            return True

        cost = self.upgrade_prices.get(upgrade_id, 0)
        if self.balance.can_spend(cost):
            self.balance.spend(cost)
            success = True

            if upgrade_id == "buy_bronze_coin":
                self.spawn_coin("bronze")
                self.bronze_coin_level += 1
                new_price = math.ceil(cost * 1.5)
                self.upgrade_prices[upgrade_id] = new_price
                self.ui.update_button(upgrade_id, new_price, level=self.bronze_coin_level)

                # === СЛИЯНИЕ В СЕРЕБРО ===
            elif upgrade_id == "fuse_to_silver":
                bronze_coins = [c for c in self.coins if isinstance(c, BronzeCoin)]
                if len(bronze_coins) >= 5:
                    # Берем координаты первой монеты для спавна новой
                    target_x = bronze_coins[0].sprite.center_x
                    target_y = bronze_coins[0].sprite.center_y

                    # Удаляем 5 штук
                    for i in range(5):
                        c = bronze_coins[i]
                        self.coins.remove(c)
                        # УБРАЛИ: self.create_particles(...) — старый эффект удаления

                    # ДОБАВИЛИ: Эффект слияния
                    self.create_fusion_flash(target_x, target_y, "silver")

                    # Спавним одну серебряную
                    self.spawn_coin("silver", x=target_x, y=target_y)
                    if self.sound_manager.merge_sound:
                        arcade.play_sound(self.sound_manager.merge_sound)
                else:
                    success = False
            # =========================

            # === СЛИЯНИЕ В ЗОЛОТО ===
            elif upgrade_id == "fuse_to_gold":
                silver_coins = [c for c in self.coins if isinstance(c, SilverCoin)]
                if len(silver_coins) >= 3:
                    target_x = silver_coins[0].sprite.center_x
                    target_y = silver_coins[0].sprite.center_y

                    for i in range(3):
                        c = silver_coins[i]
                        self.coins.remove(c)
                        # УБРАЛИ: self.create_particles(...) — старый эффект (крит)

                    # ДОБАВИЛИ: Эффект слияния
                    self.create_fusion_flash(target_x, target_y, "gold")

                    self.spawn_coin("gold", x=target_x, y=target_y)

                    if self.sound_manager.merge_sound:
                        arcade.play_sound(self.sound_manager.merge_sound)
                else:
                    success = False
            # =======================

            elif upgrade_id == "silver_crit_upgrade":
                self.silver_crit_level += 1
                new_price = math.ceil(cost * 2.718)
                self.upgrade_prices[upgrade_id] = new_price
                self.ui.update_button(upgrade_id, new_price, level=self.silver_crit_level)

            elif upgrade_id == "grab_upgrade":
                self.grab_purchased = True
                self.ui.mark_purchased(upgrade_id)

            elif upgrade_id == "gold_explosion_upgrade":
                self.gold_explosion_unlocked = True
                for coin in self.coins:
                    if isinstance(coin, GoldCoin): coin.explosion_chance = 0.5
                self.ui.mark_purchased(upgrade_id)

            elif upgrade_id == "wisp_spawn":
                if not self.wisp:
                    self.wisp = Wisp(self.width / 2, self.height / 2, self.assets.wisp_sprites,
                                     speed=100 * self.scale_factor, scale=0.33, scale_factor=self.scale_factor)
                    self.wisp_list.append(self.wisp)
                    self.ui.mark_purchased(upgrade_id)
                else:
                    success = False

            elif upgrade_id == "wisp_speed":
                if self.wisp:
                    self.wisp.upgrade_speed(50)
                    self.wisp_speed_level += 1
                    new_price = math.ceil(cost * 2.718)
                    self.upgrade_prices[upgrade_id] = new_price
                    self.ui.update_button(upgrade_id, new_price, level=self.wisp_speed_level)
                else:
                    success = False

            elif upgrade_id == "wisp_size":
                if self.wisp:
                    self.wisp.upgrade_scale(0.05)
                    self.wisp_size_level += 1
                    new_price = math.ceil(cost * 2.718)
                    self.upgrade_prices[upgrade_id] = new_price
                    self.ui.update_button(upgrade_id, new_price, level=self.wisp_size_level)
                else:
                    success = False

            elif upgrade_id == "auto_flip_upgrade":
                self.auto_flip_level += 1
                new_price = math.ceil(cost * 2.718)
                self.upgrade_prices[upgrade_id] = new_price
                self.ui.update_button(upgrade_id, new_price, level=self.auto_flip_level, name="Авто-переворот")

            elif upgrade_id == "bronze_value_upgrade":
                self.bronze_value_level += 1
                new_price = math.ceil(cost * 2.718)
                self.upgrade_prices[upgrade_id] = new_price
                for coin in self.coins:
                    if isinstance(coin, BronzeCoin):
                        coin.value *= 2
                self.ui.update_button(upgrade_id, new_price, level=self.bronze_value_level)

            elif upgrade_id == "silver_value_upgrade":
                self.silver_value_level += 1
                new_price = math.ceil(cost * 2.718)
                self.upgrade_prices[upgrade_id] = new_price
                for coin in self.coins:
                    if isinstance(coin, SilverCoin):
                        coin.value *= 2
                self.ui.update_button(upgrade_id, new_price, level=self.silver_value_level)

            elif upgrade_id == "gold_value_upgrade":
                self.gold_value_level += 1
                new_price = math.ceil(cost * 2.718)
                self.upgrade_prices[upgrade_id] = new_price
                for coin in self.coins:
                    if isinstance(coin, GoldCoin):
                        coin.value *= 2
                self.ui.update_button(upgrade_id, new_price, level=self.gold_value_level)

            elif upgrade_id == "spawn_zone_2":
                if self.zone_2 is None:
                    z2 = MultiplyZone(self.width, self.height, 2.0, (100, 255, 100, 100))
                    self.zones.append(z2)
                    self.zone_2 = z2
                    self.ui.mark_purchased(upgrade_id)
                    self.ui.update_zone_state(has_zone_2=True)
                else:
                    success = False

            elif upgrade_id == "spawn_zone_5":
                if self.zone_5 is None:
                    z5 = MultiplyZone(self.width, self.height, 5.0, (160, 32, 240, 100))
                    self.zones.append(z5)
                    self.zone_5 = z5
                    self.ui.mark_purchased(upgrade_id)
                    self.ui.update_zone_state(has_zone_5=True)
                else:
                    success = False

            elif upgrade_id == "upgrade_zone_2_size":
                if self.zone_2:
                    self.zone_2.upgrade_size(1.05)
                    self.zone_2_size_level += 1
                    new_price = math.ceil(cost * 2.718)
                    self.upgrade_prices[upgrade_id] = new_price
                    self.ui.update_button(upgrade_id, new_price, level=self.zone_2_size_level)
                else:
                    success = False

            elif upgrade_id == "upgrade_zone_5_size":
                if self.zone_5:
                    self.zone_5.upgrade_size(1.05)
                    self.zone_5_size_level += 1
                    new_price = math.ceil(cost * 2.718)
                    self.upgrade_prices[upgrade_id] = new_price
                    self.ui.update_button(upgrade_id, new_price, level=self.zone_5_size_level)
                else:
                    success = False

            elif upgrade_id == "upgrade_zone_2_mult":
                if self.zone_2:
                    self.zone_2.upgrade_multiplier(0.05)
                    self.zone_2_mult_level += 1
                    new_price = math.ceil(cost * 2.718)
                    self.upgrade_prices[upgrade_id] = new_price
                    self.ui.update_button(upgrade_id, new_price, level=self.zone_2_mult_level)
                else:
                    success = False

            elif upgrade_id == "upgrade_zone_5_mult":
                if self.zone_5:
                    self.zone_5.upgrade_multiplier(0.05)
                    self.zone_5_mult_level += 1
                    new_price = math.ceil(cost * 2.718)
                    self.upgrade_prices[upgrade_id] = new_price
                    self.ui.update_button(upgrade_id, new_price, level=self.zone_5_mult_level)
                else:
                    success = False

            elif upgrade_id == "spawn_tornado":
                if not self.tornado_unlocked:
                    self.tornado_unlocked = True
                    self.ui.update_tornado_state(True)
                else:
                    success = False

            elif upgrade_id == "tornado_cooldown_upgrade":
                self.tornado_cooldown_level += 1
                new_price = math.ceil(cost * 2.718)
                self.upgrade_prices[upgrade_id] = new_price
                self.ui.update_button(upgrade_id, new_price, level=self.tornado_cooldown_level)

            elif upgrade_id == "spawn_meteor":
                if not self.meteor_unlocked:
                    self.meteor_unlocked = True
                    self.ui.update_meteor_state(True)  # <--- ИСПРАВЛЕНИЕ: Обновляем состояние UI
                    self.ui.mark_purchased(upgrade_id)
                else:
                    success = False

            elif upgrade_id == "meteor_cooldown_upgrade":
                self.meteor_cooldown_level += 1
                new_price = math.ceil(cost * 2.718)
                self.upgrade_prices[upgrade_id] = new_price
                self.ui.update_button(upgrade_id, new_price, level=self.meteor_cooldown_level)

                # === ЛОГИКА DEBUG КНОПОК ===
            elif upgrade_id == "debug_spawn_lucky":
                self.spawn_coin("lucky")
                return True  # Возвращаем успех, но деньги не списываем (цена 0)
            elif upgrade_id == "debug_spawn_cursed":
                self.spawn_coin("cursed")
                return True
            # ===============================

            if success:
                return True
            else:
                self.balance.add(cost)
                return False


        return False

    def get_save_path(self):
        return os.path.join(os.getcwd(), "save.json")

    def save_game(self) -> None:
        data = {
            "balance": self.balance.get(),
            "upgrade_prices": self.upgrade_prices,
            "silver_crit_level": self.silver_crit_level,
            "auto_flip_level": self.auto_flip_level,
            "flags": {
                "has_gold_coin": self.has_gold_coin,
                "grab_purchased": self.grab_purchased,
                "gold_explosion_unlocked": self.gold_explosion_unlocked
            },
            "wisp": None,
            "zones": [],
            "coins": [],
            "levels": {
                "bronze_coin": self.bronze_coin_level,
                "silver_coin": self.silver_coin_level,
                "gold_coin": self.gold_coin_level,
                "bronze_value": self.bronze_value_level,
                "silver_value": self.silver_value_level,
                "gold_value": self.gold_value_level,
                "wisp_speed": self.wisp_speed_level,
                "wisp_size": self.wisp_size_level,
                "zone_2_size": self.zone_2_size_level,
                "zone_2_mult": self.zone_2_mult_level,
                "zone_5_size": self.zone_5_size_level,
                "zone_5_mult": self.zone_5_mult_level,
            },
            "meteor_unlocked": self.meteor_unlocked,
            "meteor_cooldown_level": self.meteor_cooldown_level,
            "tornado_unlocked": self.tornado_unlocked,
            "tornado_cooldown_level": self.tornado_cooldown_level
        }

        if self.wisp:
            data["wisp"] = {
                "speed": self.wisp.speed,
                "scale": self.wisp.scale,
                "x": self.wisp.center_x,
                "y": self.wisp.center_y,
                "vx": self.wisp.vx,
                "vy": self.wisp.vy
            }

        for z in self.zones:
            z_type = "unknown"
            if z is self.zone_2:
                z_type = "zone_2"
            elif z is self.zone_5:
                z_type = "zone_5"

            data["zones"].append({
                "type": z_type,
                "multiplier": z.multiplier,
                "size": z.size,
                "x": z.x,
                "y": z.y,
                "vx": z.vx,
                "vy": z.vy
            })

        for coin in self.coins:
            coin_type = "bronze"
            if isinstance(coin, SilverCoin):
                coin_type = "silver"
            elif isinstance(coin, GoldCoin):
                coin_type = "gold"
            elif isinstance(coin, LuckyCoin):
                coin_type = "lucky"
            elif isinstance(coin, CursedCoin):
                coin_type = "cursed"

            data["coins"].append({
                "type": coin_type,
                "x": coin.sprite.center_x,
                "y": coin.sprite.center_y,
                "vx": coin.vx,
                "vy": coin.vy,
                "scale": coin.scale,
                "is_moving": coin.is_moving
            })

        try:
            with open(self.get_save_path(), "w") as f:
                json.dump(data, f, ensure_ascii=True)
            print("DEBUG: Game Saved.")
        except Exception as e:
            print(f"DEBUG: Error saving game: {e}")

    def load_game(self) -> bool:
        path = self.get_save_path()
        if not os.path.exists(path):
            print("DEBUG: No save file found.")
            return False

        try:
            with open(path, "r") as f:
                data = json.load(f)

            if data is None:
                print("DEBUG: Save file is empty.")
                return False

            self.balance._value = data["balance"]
            self.upgrade_prices = data["upgrade_prices"]
            self.silver_crit_level = data["silver_crit_level"]
            self.auto_flip_level = data.get("auto_flip_level", 0)

            flags = data["flags"]
            self.has_gold_coin = flags["has_gold_coin"]
            self.grab_purchased = flags["grab_purchased"]
            self.gold_explosion_unlocked = flags["gold_explosion_unlocked"]

            levels_data = data.get("levels", {})
            self.bronze_coin_level = levels_data.get("bronze_coin", 1)
            self.silver_coin_level = levels_data.get("silver_coin", 0)
            self.gold_coin_level = levels_data.get("gold_coin", 0)
            self.bronze_value_level = levels_data.get("bronze_value", 0)
            self.silver_value_level = levels_data.get("silver_value", 0)
            self.gold_value_level = levels_data.get("gold_value", 0)
            self.wisp_speed_level = levels_data.get("wisp_speed", 0)
            self.wisp_size_level = levels_data.get("wisp_size", 0)
            self.zone_2_size_level = levels_data.get("zone_2_size", 0)
            self.zone_2_mult_level = levels_data.get("zone_2_mult", 0)
            self.zone_5_size_level = levels_data.get("zone_5_size", 0)
            self.zone_5_mult_level = levels_data.get("zone_5_mult", 0)

            self.meteor_unlocked = data.get("meteor_unlocked", False)
            self.meteor_cooldown_level = data.get("meteor_cooldown_level", 0)

            self.tornado_unlocked = data.get("tornado_unlocked", False)
            self.tornado_cooldown_level = data.get("tornado_cooldown_level", 0)

            if self.tornado_unlocked:
                self.ui.mark_purchased("spawn_tornado")
                self.ui.update_tornado_state(True)

            self.ui.update_button("tornado_cooldown_upgrade", self.upgrade_prices["tornado_cooldown_upgrade"],
                                  level=self.tornado_cooldown_level)

            # 5. Загрузка Виспа
            wisp_data = data.get("wisp")
            if wisp_data:
                self.wisp_list.clear()  # <--- ИСПРАВЛЕНИЕ: Чистим список перед загрузкой виспа
                self.wisp = Wisp(self.width / 2, self.height / 2, self.assets.wisp_sprites, scale=wisp_data["scale"])
                self.wisp.speed = wisp_data["speed"]
                self.wisp.center_x = wisp_data["x"]
                self.wisp.center_y = wisp_data["y"]
                self.wisp.vx = wisp_data["vx"]
                self.wisp.vy = wisp_data["vy"]
                self.wisp_list.append(self.wisp)

            # 6. Загрузка Зон
            self.zones.clear()
            self.zone_2 = None
            self.zone_5 = None

            for z_data in data["zones"]:
                z_type = z_data.get("type", "unknown")

                if z_type == "zone_2":
                    z = MultiplyZone(self.width, self.height, z_data["multiplier"], (100, 255, 100, 100))
                    self.zone_2 = z
                elif z_type == "zone_5":
                    z = MultiplyZone(self.width, self.height, z_data["multiplier"], (160, 32, 240, 100))
                    self.zone_5 = z
                else:
                    z = MultiplyZone(self.width, self.height, z_data["multiplier"], (0, 0, 0, 0))

                z.size = z_data["size"]
                z.width = z.size
                z.height = z.size
                z.x = z_data["x"]
                z.y = z_data["y"]
                z.vx = z_data["vx"]
                z.vy = z_data["vy"]
                self.zones.append(z)

            # 7. Загрузка Монет
            self.coins.clear()
            for c_data in data["coins"]:
                c_type = c_data["type"]

                if c_type == "bronze":
                    c = BronzeCoin(c_data["x"], c_data["y"], self.assets.bronze_coin_sprites, scale=c_data["scale"],
                                   scale_factor=self.scale_factor)
                elif c_type == "silver":
                    crit_chance = 0.1 * self.silver_crit_level
                    c = SilverCoin(c_data["x"], c_data["y"], self.assets.silver_coin_sprites, crit_chance,
                                   scale=c_data["scale"], scale_factor=self.scale_factor)
                elif c_type == "gold":
                    c = GoldCoin(c_data["x"], c_data["y"], self.assets.gold_coin_sprites, scale=c_data["scale"],
                                 scale_factor=self.scale_factor)
                elif c_type == "lucky":
                    c = LuckyCoin(c_data["x"], c_data["y"], self.assets.lucky_coin_sprites,
                                  scale=c_data["scale"], scale_factor=self.scale_factor)
                elif c_type == "cursed":
                    c = CursedCoin(c_data["x"], c_data["y"], self.assets.cursed_coin_sprites,
                                   scale=c_data["scale"], scale_factor=self.scale_factor)

                c.vx = c_data["vx"]
                c.vy = c_data["vy"]
                c.is_moving = c_data["is_moving"]

                if c.is_moving:
                    c._select_flying_animation()
                    c.anim_index = 0
                else:
                    c.land()
                    c.landed = False
                self.coins.append(c)

            if self.grab_purchased: self.ui.mark_purchased("grab_upgrade")
            if self.gold_explosion_unlocked: self.ui.mark_purchased("gold_explosion_upgrade")
            if self.wisp: self.ui.mark_purchased("wisp_spawn")
            if self.zone_2: self.ui.mark_purchased("spawn_zone_2")
            if self.zone_5: self.ui.mark_purchased("spawn_zone_5")
            if self.meteor_unlocked: self.ui.mark_purchased("spawn_meteor")

            self.ui.update_button("silver_crit_upgrade", self.upgrade_prices["silver_crit_upgrade"],
                                  level=self.silver_crit_level)
            self.ui.update_button("auto_flip_upgrade", self.upgrade_prices["auto_flip_upgrade"],
                                  level=self.auto_flip_level)

            self.ui.update_button("buy_bronze_coin", self.upgrade_prices["buy_bronze_coin"],
                                  level=self.bronze_coin_level)

            self.ui.update_button("bronze_value_upgrade", self.upgrade_prices["bronze_value_upgrade"],
                                  level=self.bronze_value_level)
            self.ui.update_button("silver_value_upgrade", self.upgrade_prices["silver_value_upgrade"],
                                  level=self.silver_value_level)
            self.ui.update_button("gold_value_upgrade", self.upgrade_prices["gold_value_upgrade"],
                                  level=self.gold_value_level)

            self.ui.update_button("wisp_speed", self.upgrade_prices["wisp_speed"], level=self.wisp_speed_level)
            self.ui.update_button("wisp_size", self.upgrade_prices["wisp_size"], level=self.wisp_size_level)

            self.ui.update_button("upgrade_zone_2_size", self.upgrade_prices["upgrade_zone_2_size"],
                                  level=self.zone_2_size_level)
            self.ui.update_button("upgrade_zone_2_mult", self.upgrade_prices["upgrade_zone_2_mult"],
                                  level=self.zone_2_mult_level)
            self.ui.update_button("upgrade_zone_5_size", self.upgrade_prices["upgrade_zone_5_size"],
                                  level=self.zone_5_size_level)
            self.ui.update_button("upgrade_zone_5_mult", self.upgrade_prices["upgrade_zone_5_mult"],
                                  level=self.zone_5_mult_level)

            self.ui.update_button("meteor_cooldown_upgrade", self.upgrade_prices["meteor_cooldown_upgrade"],
                                  level=self.meteor_cooldown_level)

            self.ui.update_grab_state(self.has_gold_coin, self.grab_purchased)
            self.ui.update_explosion_state(self.gold_explosion_unlocked)
            self.ui.update_wisp_state(self.wisp is not None)
            self.ui.update_meteor_state(self.meteor_unlocked)
            self.ui.update_zone_state(
                has_zone_2=(self.zone_2 is not None),
                has_zone_5=(self.zone_5 is not None)
            )

            print("DEBUG: Game Loaded Successfully.")
            return True

        except json.JSONDecodeError:
            print("DEBUG: Save file is corrupted or empty. Starting new game.")
            return False
        except Exception as e:
            print(f"DEBUG: Error loading game: {e}")
            return False

    def reset_game(self) -> bool:
        if os.path.exists(self.get_save_path()):
            os.remove(self.get_save_path())

        self.coins.clear()
        self.particles.clear()
        self.zones.clear()
        self.zone_2 = None
        self.zone_5 = None

        self.beetle = None
        self.wisp = None
        self.wisp_list.clear()
        self.crater = None
        self.meteor = None
        self.explosions = arcade.SpriteList()

        self.meteor_unlocked = False
        self.meteor_cooldown_level = 0

        self.balance._value = 0
        self.silver_crit_level = 1
        self.auto_flip_level = 0
        self.bronze_coin_level = 1
        self.silver_coin_level = 0
        self.gold_coin_level = 0

        self.bronze_value_level = 0
        self.silver_value_level = 0
        self.gold_value_level = 0
        self.wisp_speed_level = 0
        self.wisp_size_level = 0
        self.zone_2_size_level = 0
        self.zone_2_mult_level = 0
        self.zone_5_size_level = 0
        self.zone_5_mult_level = 0

        self.has_gold_coin = False
        self.grab_purchased = False
        self.gold_explosion_unlocked = False

        self.tornado = None
        self.tornado_unlocked = False
        self.tornado_cooldown_level = 0
        self.tornado_respawn_timer = 0.0
        self.tornado_list.clear()

        for tab_groups in self.ui.tab_content.values():
            for grp in tab_groups:
                for b in grp.buttons:
                    b.is_purchased = False
                    self.ui._enabled[b.upgrade_id] = True

        self.ui.update_meteor_state(False)
        self.ui.update_button("spawn_meteor", 15000, level=0)
        self.ui.update_button("meteor_cooldown_upgrade", 2000, level=0)

        self.ui.update_tornado_state(False)
        self.ui.update_button("spawn_tornado", 15000, level=0)
        self.ui.update_button("tornado_cooldown_upgrade", 2000, level=0)

        self.upgrade_prices = {
            "buy_bronze_coin": 50,
            "silver_crit_upgrade": 500,
            "grab_upgrade": 500,
            "gold_explosion_upgrade": 2000,
            "wisp_spawn": 5000,
            "wisp_speed": 1000,
            "wisp_size": 1000,
            "spawn_zone_2": 10000,
            "spawn_zone_5": 50000,
            "upgrade_zone_2_size": 2000,
            "upgrade_zone_5_size": 5000,
            "upgrade_zone_2_mult": 3000,
            "upgrade_zone_5_mult": 7000,
            "auto_flip_upgrade": 500,
            "bronze_value_upgrade": 2000,
            "silver_value_upgrade": 5000,
            "gold_value_upgrade": 10000,
            "spawn_meteor": 15000,
            "meteor_cooldown_upgrade": 2000,
            "spawn_tornado": 15000,
            "tornado_cooldown_upgrade": 2000,
            "fuse_to_silver": 0,
            "fuse_to_gold": 0,
        }

        self.ui.update_button("buy_bronze_coin", 50, level=1)

        self.ui.update_button("silver_crit_upgrade", 500, level=1)
        self.ui.update_button("wisp_spawn", 5000, level=0)
        self.ui.update_button("spawn_zone_2", 10000, level=0)
        self.ui.update_button("spawn_zone_5", 50000, level=0)
        self.ui.update_button("grab_upgrade", 500, level=0)
        self.ui.update_button("gold_explosion_upgrade", 2000, level=0)

        self.ui.update_button("auto_flip_upgrade", 500, level=0)

        self.ui.update_button("bronze_value_upgrade", 2000, level=0)
        self.ui.update_button("silver_value_upgrade", 5000, level=0)
        self.ui.update_button("gold_value_upgrade", 10000, level=0)

        self.ui.update_button("wisp_speed", 1000, level=0)
        self.ui.update_button("wisp_size", 1000, level=0)

        self.ui.update_button("upgrade_zone_2_size", 2000, level=0)
        self.ui.update_button("upgrade_zone_2_mult", 3000, level=0)
        self.ui.update_button("upgrade_zone_5_size", 5000, level=0)
        self.ui.update_button("upgrade_zone_5_mult", 7000, level=0)

        self.ui.update_grab_state(False, False)
        self.ui.update_explosion_state(False)
        self.ui.update_wisp_state(False)
        self.ui.update_zone_state(False, False)

        self.spawn_coin("bronze", x=self.start_coin_x, y=self.start_coin_y)

        print("DEBUG: Game Reset.")
        return True

    def spawn_beetle(self) -> None:
        margin = 50
        x = random.randint(margin, int(self.width - margin))
        y = random.randint(margin, int(self.height - margin))

        # ИСПРАВЛЕНИЕ: Передаем scale_factor
        self.beetle = Beetle(x, y, self.assets.beetle_sprites, scale_factor=self.scale_factor)
        print("DEBUG: Beetle spawned!")

    def kill_beetle(self) -> None:
        if not self.beetle: return

        if self.sound_manager.beetle_dead_sound:
            arcade.play_sound(self.sound_manager.beetle_dead_sound)

        current_balance = self.balance.get()
        new_balance = int(current_balance * 1.2)

        self.balance._value = new_balance
        print(f"DEBUG: Beetle killed! Balance {current_balance} -> {new_balance}")

        self.beetle.start_death()

    def spawn_beetle_initial(self):
        self.beetle_respawn_interval = random.uniform(10.0, 60.0)
        self.beetle_respawn_timer = 0.0

    def spawn_meteor(self) -> None:
        crater_w = self.assets.crater_texture.width
        crater_h = self.assets.crater_texture.height

        half_w = crater_w / 2
        half_h = crater_h / 2

        margin = 50
        min_x = max(margin, half_w)
        max_x = min(self.width - margin, self.width - half_w)

        target_x = random.uniform(min_x, max_x)

        min_y = self.height * 0.4
        max_y = self.height * 0.8
        max_y = min(max_y, self.height - half_h)

        target_y = random.uniform(min_y, max_y)

        start_y = self.height + 100

        self.meteor = Meteor(target_x, start_y, target_y, self.assets.meteor_textures)

        print(f"DEBUG: Meteor spawned at {target_x:.0f}, {target_y:.0f}")

    def create_explosion_particles(self, cx: float, cy: float) -> None:
        for _ in range(50):
            red = 255
            green = random.randint(0, 200)
            color = (red, green, 0, 255)

            angle = random.uniform(0, 6.28)
            speed = random.uniform(100, 400)
            size = random.uniform(2, 5)

            particle_data = {
                'x': cx, 'y': cy,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'color': color,
                'size': size,
                'decay_speed': 2.0
            }
            self.particles.append(particle_data)

    def spawn_tornado(self) -> None:
        margin = self.width / 4

        min_x = margin
        max_x = self.width - margin

        min_y = margin
        max_y = self.height - margin

        target_x = random.uniform(min_x, max_x)
        target_y = random.uniform(min_y, max_y)

        self.tornado = Tornado(
            target_x,
            target_y,
            self.assets.tornado_textures,
            self.sound_manager.tornado_sound,
            scale=2.0 * self.scale_factor,  # Визуальный размер
            world_scale=self.scale_factor,  # Физический масштаб
            world_width=self.width
        )

        self.tornado_list.clear()
        self.tornado_list.append(self.tornado)

        print(f"DEBUG: Tornado spawned at {target_x:.0f}, {target_y:.0f}")

    def get_coin_counts(self) -> dict:
        """Подсчитывает количество монет каждого типа на поле"""
        counts = {"bronze": 0, "silver": 0, "gold": 0}
        for coin in self.coins:
            if isinstance(coin, BronzeCoin):
                counts["bronze"] += 1
            elif isinstance(coin, SilverCoin):
                counts["silver"] += 1
            elif isinstance(coin, GoldCoin):
                counts["gold"] += 1
        return counts

