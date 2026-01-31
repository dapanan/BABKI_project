from logic.world.coin import Coin
import random
import arcade
import math


class LuckyCoin(Coin):
    def __init__(self, x: float, y: float, sprites: dict, scale: float = 1.5, scale_factor: float = 1.0) -> None:
        super().__init__(x, y, sprites, value=0, scale=scale, scale_factor=scale_factor)

        self.lifetime = None
        self.is_fading = False
        self.sound_played = False
        self.is_used = False

        # === ФЛАГИ ДЛЯ ЭФФЕКТА ===
        self.is_shimmering = True  # Сначала переливается
        self.shimmer_timer = 0.0
        # =======================

    def hit(self, dx: int, dy: int) -> None:
        if self.is_used:
            return
        super().hit(dx, dy)
        self.shimmer_timer = 0.0

    def update(self, dt: float, width: int, height: int, nearby_coins: list) -> None:
        # Сначала запускаем базовую физику (там есть логика угасания)
        super().update(dt, width, height, nearby_coins)

        # Если монетка переливается — перекрываем логику угасания своими значениями
        if self.is_shimmering:
            self.shimmer_timer += dt * 5.0
            wave = math.sin(self.shimmer_timer)
            # Диапазон от 200 до 255 (не слишком яркий)
            alpha = 227 + int(28 * wave)
            self.sprite.alpha = alpha

            # Принудительно говорим игре, что мы не в режиме угасания
            self.is_fading = False

    def land(self) -> None:
        if self.is_used:
            return
        is_heads = random.random() < 0.5

        if is_heads:
            self.last_outcome_value = 1
            self.sprite.texture = self.sprites.get("heads")
            self.lifetime = 2.0  # Одинаковое время
        else:
            self.last_outcome_value = 0
            self.sprite.texture = self.sprites.get("tails")
            self.lifetime = 2.0  # Одинаковое время (было 0.5)

        self.is_moving = False
        self.anim = []
        self.landed = True
        self.is_used = True
        self.sound_played = False

        self.is_shimmering = False