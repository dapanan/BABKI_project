import arcade
import random
import math
from logic.world.gold_coin import GoldCoin
from logic.world.bronze_coin import BronzeCoin
from logic.world.silver_coin import SilverCoin
from logic.assets.asset_manager import AssetManager
from logic.assets.sound_manager import SoundManager
from logic.economy.balance import Balance


class GameController:
    def __init__(self, asset_manager: AssetManager, ui_controller, sound_manager: SoundManager):
        self.assets = asset_manager
        self.balance = Balance()
        self.ui = ui_controller
        self.sound_manager = sound_manager
        self.coins = []
        self.particles = []

        self.silver_crit_level = 1

        self.upgrade_prices = {
            "buy_bronze_coin": 50,
            "buy_silver_coin": 200,
            "buy_gold_coin": 1000,
            "silver_crit_upgrade": 500,
            "grab_upgrade": 500
        }

        self.has_gold_coin = False
        self.grab_purchased = False
        self.grabbed_coin = None

        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_dx = 0
        self.mouse_dy = 0

        self.mouse_velocity_history = []
        self.max_history_frames = 8

        self.spawn_coin("bronze")

    def spawn_coin(self, coin_type: str):
        w = 1920 - 500
        h = 1080

        x = random.randint(100, w - 100)
        y = random.randint(100, h - 100)

        if coin_type == "bronze":
            coin = BronzeCoin(x, y, self.assets.coin_sprites)
        elif coin_type == "silver":
            crit_chance = 0.1 * self.silver_crit_level
            coin = SilverCoin(x, y, self.assets.coin_sprites, crit_chance)
        elif coin_type == "gold":
            coin = GoldCoin(x, y, self.assets.coin_sprites)
            self.has_gold_coin = True

        self.coins.append(coin)

    def update(self, dt: float) -> None:
        width = 1920 - 500
        height = 1080

        if self.grabbed_coin:
            self.grabbed_coin.sprite.center_x = self.mouse_x
            self.grabbed_coin.sprite.center_y = self.mouse_y
            self.grabbed_coin.vx = 0
            self.grabbed_coin.vy = 0

        for coin in self.coins:
            if coin is self.grabbed_coin:
                continue

            coin.update(dt, width, height, self.coins)

            # 1. Проверяем деньги
            outcome = coin.check_land_event()
            if outcome > 0:
                self.balance.add(outcome)

                is_crit_now = False
                if isinstance(coin, SilverCoin) and coin.is_crit:
                    is_crit_now = True
                    coin.is_crit = False

                if is_crit_now:
                    self.create_particles(coin.sprite.center_x, coin.sprite.center_y, (192, 192, 192, 255))

            # 2. ПРОВЕРКА ПРИЗЕМЛЕНИЯ (ЗВУК)
            # Играем звук, если флаг установлен, и потом сбрасываем его
            if coin.landed:
                self.sound_manager.play_land(isinstance(coin, GoldCoin))
                coin.landed = False  # Сбрасываем флаг

        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt

        self.particles = [p for p in self.particles if p['life'] > 0]
        self.ui.update_grab_state(self.has_gold_coin, self.grab_purchased)

    def draw(self) -> None:
        for coin in self.coins:
            if not coin.is_moving:
                coin.draw()

        for coin in self.coins:
            if coin.is_moving:
                coin.draw()

        for p in self.particles:
            alpha = int(255 * (p['life'] / 1.0))
            current_color = (p['color'][0], p['color'][1], p['color'][2], alpha)
            arcade.draw_circle_filled(p['x'], p['y'], p['size'], current_color)

    def on_mouse_press(self, x: int, y: int, button: int) -> None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            if x < 1920 - 500:
                for coin in self.coins:
                    if not coin.is_moving and coin is not self.grabbed_coin:
                        dx = x - coin.sprite.center_x
                        dy = y - coin.sprite.center_y
                        if dx * dx + dy * dy < (coin.radius * coin.radius):
                            coin.hit(dx, dy)
                            self.sound_manager.play_toss(isinstance(coin, GoldCoin))
                            break

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        self.mouse_x = x
        self.mouse_y = y
        self.mouse_velocity_history.append((dx, dy))
        if len(self.mouse_velocity_history) > self.max_history_frames:
            self.mouse_velocity_history.pop(0)

    def on_mouse_press_rmb(self, x: int, y: int) -> None:
        if not self.grab_purchased:
            return

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
        if not self.grabbed_coin:
            return

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

    def create_particles(self, x, y, color=(255, 215, 0, 255)):
        for _ in range(30):
            gray = random.randint(80, 200)
            base_color = (gray, gray, gray)
            angle = random.uniform(0, 6.28)
            speed = random.uniform(100, 200)
            size = random.uniform(3, 6)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'color': base_color,
                'size': size
            })

    def try_buy_upgrade(self, upgrade_id: str) -> bool:
        if upgrade_id == "finish_game":
            return True

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
                success = True

            new_price = math.ceil(cost * 2.718)
            self.upgrade_prices[upgrade_id] = new_price

            if upgrade_id == "silver_crit_upgrade":
                self.ui.update_button(
                    upgrade_id,
                    new_price,
                    level=self.silver_crit_level
                )
            elif upgrade_id == "grab_upgrade":
                self.ui.update_grab_state(self.has_gold_coin, True)
            else:
                self.ui.update_button(
                    upgrade_id,
                    new_price
                )

            return True

        return False