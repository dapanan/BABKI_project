import random
import math
from logic.world.gold_coin import GoldCoin
from logic.world.bronze_coin import BronzeCoin
from logic.assets.asset_manager import AssetManager
from logic.economy.balance import Balance


class GameController:
    def __init__(self, asset_manager: AssetManager):
        self.assets = asset_manager
        self.balance = Balance()
        self.coins = []
        self.particles = []

        self.gold_crit_level = 0

        # Старт с одной бронзовой монеты
        self.spawn_coin("bronze")

    def spawn_coin(self, coin_type: str):
        w = 1920 - 500
        h = 1080

        x = random.randint(100, w - 100)
        y = random.randint(100, h - 100)

        if coin_type == "bronze":
            coin = BronzeCoin(x, y, self.assets.coin_sprites)
        elif coin_type == "gold":
            crit_chance = 0.1 * self.gold_crit_level
            coin = GoldCoin(x, y, self.assets.coin_sprites, crit_chance)

        self.coins.append(coin)

    def update(self, dt: float) -> None:
        width = 1920 - 500
        height = 1080

        for coin in self.coins:
            coin.update(dt, width, height, self.coins)

            outcome = coin.check_land_event()
            if outcome > 0:
                self.balance.add(outcome)

                # Эффекты крита
                if isinstance(coin, GoldCoin) and coin.is_crit:
                    self.create_particles(coin.sprite.center_x, coin.sprite.center_y)

        # Обновление частиц
        for p in self.particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['life'] -= dt

        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self) -> None:
        for coin in self.coins:
            coin.draw()

        for p in self.particles:
            arcade.draw_circle_filled(p['x'], p['y'], 3, p['color'])

    def on_mouse_press(self, x: int, y: int) -> None:
        for coin in self.coins:
            if not coin.is_moving:
                dx = x - coin.sprite.center_x
                dy = y - coin.sprite.center_y
                if dx * dx + dy * dy < (coin.radius * coin.radius):
                    coin.hit(dx, dy)
                    break

    def create_particles(self, x, y):
        for _ in range(20):
            angle = random.uniform(0, 6.28)
            speed = random.uniform(100, 300)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'color': (255, 215, 0, 255)
            })

    def try_buy_upgrade(self, upgrade_id: str) -> bool:
        cost = 0
        success = False

        if upgrade_id == "buy_bronze_coin":
            cost = 10
            if self.balance.can_spend(cost):
                self.balance.spend(cost)
                self.spawn_coin("bronze")
                success = True

        # НОВАЯ ЛОГИКА: Покупка золотой монеты
        elif upgrade_id == "buy_gold_coin":
            cost = 20
            if self.balance.can_spend(cost):
                self.balance.spend(cost)
                self.spawn_coin("gold")
                success = True

        elif upgrade_id == "gold_crit_upgrade":
            cost = 500 * (self.gold_crit_level + 1)
            if self.balance.can_spend(cost):
                self.balance.spend(cost)
                self.gold_crit_level += 1
                # Больше не спавним монету автоматически, ты покупаешь её отдельной кнопкой
                success = True

        return success