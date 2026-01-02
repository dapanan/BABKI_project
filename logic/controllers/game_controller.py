import arcade
import random
import math
from logic.world.gold_coin import GoldCoin
from logic.world.bronze_coin import BronzeCoin
from logic.world.silver_coin import SilverCoin
from logic.assets.asset_manager import AssetManager
from logic.economy.balance import Balance


class GameController:
    def __init__(self, asset_manager: AssetManager, ui_controller):
        self.assets = asset_manager
        self.balance = Balance()
        self.ui = ui_controller
        self.coins = []
        self.particles = []

        self.silver_crit_level = 1

        self.upgrade_prices = {
            "buy_bronze_coin": 50,
            "buy_silver_coin": 200,
            "buy_gold_coin": 1000,
            "silver_crit_upgrade": 500
        }

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

        self.coins.append(coin)

    def update(self, dt: float) -> None:
        width = 1920 - 500
        height = 1080

        for coin in self.coins:
            coin.update(dt, width, height, self.coins)

            outcome = coin.check_land_event()
            if outcome > 0:
                self.balance.add(outcome)

                is_crit_now = False
                if isinstance(coin, SilverCoin) and coin.is_crit:
                    is_crit_now = True
                    coin.is_crit = False

                if is_crit_now:
                    # ПЕРЕДАЕМ РАДИУС МОНЕТКИ В ФУНКЦИЮ
                    self.create_particles(coin.sprite.center_x, coin.sprite.center_y, coin.radius)

        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt

        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self) -> None:
        # Рисуем монеты
        for coin in self.coins:
            if not coin.is_moving:
                coin.draw()

        for coin in self.coins:
            if coin.is_moving:
                coin.draw()

        # Рисуем частицы
        for p in self.particles:
            # Плавное затухание
            alpha = int(255 * (p['life'] / 1.0))
            current_color = (p['color'][0], p['color'][1], p['color'][2], alpha)

            arcade.draw_circle_filled(p['x'], p['y'], p['size'], current_color)

    def on_mouse_press(self, x: int, y: int) -> None:
        for coin in self.coins:
            if not coin.is_moving:
                dx = x - coin.sprite.center_x
                dy = y - coin.sprite.center_y
                if dx * dx + dy * dy < (coin.radius * coin.radius):
                    coin.hit(dx, dy)
                    break

    def create_particles(self, cx, cy, radius):
        """Создает частицы, разлетающиеся с краев монетки"""
        for _ in range(30):
            gray = random.randint(80, 200)
            base_color = (gray, gray, gray)

            angle = random.uniform(0, 6.28)  # Случайный угол разлета
            speed = random.uniform(100, 200)

            # ВЫЧИСЛЯЕМ КООРДИНАТЫ НА КРАЮ МОНЕТКИ
            # spawn_x = центр_х + радиус * косинус_угла
            # spawn_y = центр_y + радиус * синус_угла
            spawn_x = cx + radius * math.cos(angle)
            spawn_y = cy + radius * math.sin(angle)

            size = random.uniform(3, 6)

            self.particles.append({
                'x': spawn_x,  # Стартуем с края
                'y': spawn_y,  # Стартуем с края
                'vx': math.cos(angle) * speed,  # Летим в ту же сторону (наружу)
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

            new_price = math.ceil(cost * 2.718)
            self.upgrade_prices[upgrade_id] = new_price

            if upgrade_id == "silver_crit_upgrade":
                self.ui.update_button(
                    upgrade_id,
                    new_price,
                    level=self.silver_crit_level
                )
            else:
                self.ui.update_button(
                    upgrade_id,
                    new_price
                )

            return True

        return False