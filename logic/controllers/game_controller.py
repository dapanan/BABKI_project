import arcade
import random
import math
from logic.world.gold_coin import GoldCoin
from logic.world.bronze_coin import BronzeCoin
from logic.world.silver_coin import SilverCoin
from logic.world.map_activities.wisp import Wisp
from logic.world.map_activities.multiply_zone import MultiplyZone
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
from logic.economy.balance import Balance


class GameController:
    def __init__(self, asset_manager: AssetManager, ui_controller, sound_manager: SoundManager,
                 world_width: int, world_height: int, scale_factor: float):
        self.assets = asset_manager
        self.balance = Balance()
        self.ui = ui_controller
        self.sound_manager = sound_manager
        self.coins = []
        self.particles = []

        # Адаптация под монитор
        self.width = world_width
        self.height = world_height
        self.scale_factor = scale_factor

        self.silver_crit_level = 1

        self.upgrade_prices = {
            "buy_bronze_coin": 50,
            "buy_silver_coin": 200,
            "buy_gold_coin": 1000,
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
            "upgrade_zone_5_mult": 7000
        }

        self.has_gold_coin = False
        self.grab_purchased = False
        self.gold_explosion_unlocked = False
        self.grabbed_coin = None

        self.wisp: Wisp | None = None
        self.wisp_list = arcade.SpriteList()

        self.zones: list[MultiplyZone] = []

        # Сохраняем прямые ссылки на зоны, чтобы не искать их по числам
        self.zone_2: MultiplyZone | None = None
        self.zone_5: MultiplyZone | None = None

        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_dx = 0
        self.mouse_dy = 0
        self.mouse_velocity_history = []
        self.max_history_frames = 8

        self.spawn_coin("bronze")

    def spawn_coin(self, coin_type: str):
        w = self.width
        h = self.height
        margin = 100 * self.scale_factor
        x = random.randint(int(margin), int(w - margin))
        y = random.randint(int(margin), int(h - margin))

        if coin_type == "bronze":
            coin = BronzeCoin(x, y, self.assets.bronze_coin_sprites, scale=0.8 * self.scale_factor)
            coin.explosion_chance = 0
        elif coin_type == "silver":
            crit_chance = 0.1 * self.silver_crit_level
            coin = SilverCoin(x, y, self.assets.silver_coin_sprites, crit_chance, scale=1.1 * self.scale_factor)
            coin.explosion_chance = 0
        elif coin_type == "gold":
            coin = GoldCoin(x, y, self.assets.gold_coin_sprites, scale=1.5 * self.scale_factor)
            self.has_gold_coin = True
            if self.gold_explosion_unlocked:
                coin.explosion_chance = 0.5
            else:
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

        if self.grabbed_coin:
            self.grabbed_coin.sprite.center_x = self.mouse_x
            self.grabbed_coin.sprite.center_y = self.mouse_y
            self.grabbed_coin.vx = 0
            self.grabbed_coin.vy = 0

        for coin in self.coins:
            if coin is self.grabbed_coin: continue

            coin.update(dt, width, height, self.coins)

            outcome = coin.check_land_event()
            if outcome > 0:
                # === ЛОГИКА ЗОН МНОЖИТЕЛЯ ===
                total_multiplier = 1.0
                for zone in self.zones:
                    if zone.check_collision(coin):
                        total_multiplier *= zone.multiplier

                final_value = int(outcome * total_multiplier)
                self.balance.add(final_value)
                # =================================

                is_crit_now = False
                if isinstance(coin, SilverCoin) and coin.is_crit:
                    is_crit_now = True
                    coin.is_crit = False
                if is_crit_now:
                    self.create_particles(coin.sprite.center_x, coin.sprite.center_y, (192, 192, 192, 255), coin)

            if coin.needs_toss_sound:
                c_type = self._get_coin_type_string(coin)
                self.sound_manager.play_toss(c_type)
                coin.needs_toss_sound = False

            if coin.landed:
                c_type = self._get_coin_type_string(coin)
                self.sound_manager.play_land(c_type)
                coin.landed = False

        if self.wisp:
            self.wisp.update(dt, width, height, self.coins, self.grabbed_coin)

        # === ОБНОВЛЕНИЕ ЗОН ===
        for zone in self.zones:
            zone.update(dt, width, height)
        # =======================

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

    def draw(self) -> None:
        # 1. Рисуем зоны (под всем)
        for zone in self.zones:
            zone.draw()

        # 2. Рисуем монетки
        for coin in self.coins:
            if not coin.is_moving: coin.draw()
        for coin in self.coins:
            if coin.is_moving: coin.draw()

        # 3. Рисуем виспа
        self.wisp_list.draw()

        # 4. Частицы
        for p in self.particles:
            alpha = int(255 * (p['life'] / 1.0))
            current_color = (p['color'][0], p['color'][1], p['color'][2], alpha)
            arcade.draw_circle_filled(p['x'], p['y'], p['size'], current_color)

    def on_mouse_press(self, x: int, y: int, button: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            if x < self.width:
                for coin in self.coins:
                    if not coin.is_moving and coin is not self.grabbed_coin:
                        dx = x - coin.sprite.center_x
                        dy = y - coin.sprite.center_y
                        if dx * dx + dy * dy < (coin.radius * coin.radius):
                            coin.hit(dx, dy)
                            c_type = self._get_coin_type_string(coin)
                            self.sound_manager.play_toss(c_type)
                            break

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.mouse_x = x
        self.mouse_y = y
        self.mouse_velocity_history.append((dx, dy))
        if len(self.mouse_velocity_history) > self.max_history_frames: self.mouse_velocity_history.pop(0)

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
            throw_multiplier = 175.0
            coin.vx = avg_dx * throw_multiplier
            coin.vy = avg_dy * throw_multiplier

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
        if upgrade_id == "finish_game": return True

        cost = self.upgrade_prices.get(upgrade_id, 0)
        if self.balance.can_spend(cost):
            self.balance.spend(cost)
            success = True

            if upgrade_id == "buy_bronze_coin":
                self.spawn_coin("bronze")
            elif upgrade_id == "buy_silver_coin":
                self.spawn_coin("silver")
            elif upgrade_id == "buy_gold_coin":
                self.spawn_coin("gold")
            elif upgrade_id == "silver_crit_upgrade":
                self.silver_crit_level += 1
            elif upgrade_id == "grab_upgrade":
                self.grab_purchased = True
            elif upgrade_id == "gold_explosion_upgrade":
                self.gold_explosion_unlocked = True
                for coin in self.coins:
                    if isinstance(coin, GoldCoin): coin.explosion_chance = 0.5

            elif upgrade_id == "wisp_spawn":
                if not self.wisp:
                    self.wisp = Wisp(self.width / 2, self.height / 2, self.assets.wisp_sprites, scale=0.33)
                    self.wisp_list.append(self.wisp)
                    success = True
                else:
                    success = False

            elif upgrade_id == "wisp_speed":
                if self.wisp:
                    self.wisp.upgrade_speed(50)
                    success = True
                else:
                    success = False

            elif upgrade_id == "wisp_size":
                if self.wisp:
                    self.wisp.upgrade_scale(0.05)
                    success = True
                else:
                    success = False

            # === АПГРЕЙДЫ ЗОН (Исправленная логика через ссылки) ===
            elif upgrade_id == "spawn_zone_2":
                if self.zone_2 is None:
                    z2 = MultiplyZone(self.width, self.height, 2.0, (100, 255, 100, 50))
                    self.zones.append(z2)
                    self.zone_2 = z2  # Сохраняем ссылку
                    self.ui.set_button_disabled("spawn_zone_2", "Зона x2 (Куплено)")
                    self.ui.update_zone_state(has_zone_2=True)
                    success = True
                else:
                    success = False

            elif upgrade_id == "spawn_zone_5":
                if self.zone_5 is None:
                    z5 = MultiplyZone(self.width, self.height, 5.0, (160, 32, 240, 50))
                    self.zones.append(z5)
                    self.zone_5 = z5  # Сохраняем ссылку
                    self.ui.set_button_disabled("spawn_zone_5", "Зона x5 (Куплено)")
                    self.ui.update_zone_state(has_zone_5=True)
                    success = True
                else:
                    success = False

            elif upgrade_id == "upgrade_zone_2_size":
                if self.zone_2:
                    self.zone_2.upgrade_size(1.05)
                    success = True
                else:
                    success = False

            elif upgrade_id == "upgrade_zone_5_size":
                if self.zone_5:
                    self.zone_5.upgrade_size(1.05)
                    success = True
                else:
                    success = False

            elif upgrade_id == "upgrade_zone_2_mult":
                if self.zone_2:
                    self.zone_2.upgrade_multiplier(0.05)
                    success = True
                else:
                    success = False

            elif upgrade_id == "upgrade_zone_5_mult":
                if self.zone_5:
                    self.zone_5.upgrade_multiplier(0.05)
                    success = True
                else:
                    success = False

            # === ОБРАБОТКА РЕЗУЛЬТАТА ===
            if success:
                # Покупка удалась - обновляем цены
                new_price = math.ceil(cost * 2.718)
                self.upgrade_prices[upgrade_id] = new_price

                if upgrade_id == "silver_crit_upgrade":
                    self.ui.update_button(upgrade_id, new_price, level=self.silver_crit_level)
                elif upgrade_id == "grab_upgrade":
                    self.ui.update_grab_state(self.has_gold_coin, True)
                elif upgrade_id == "gold_explosion_upgrade":
                    self.ui.set_button_disabled("gold_explosion_upgrade", "Золотой взрыв (Куплено)")
                elif upgrade_id == "wisp_spawn":
                    self.ui.update_wisp_state(True)
                else:
                    self.ui.update_button(upgrade_id, new_price)

                return True
            else:
                # Покупка не удалась (например, зона уже есть) - возвращаем деньги
                self.balance.add(cost)
                return False

        return False