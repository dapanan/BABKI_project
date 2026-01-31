import arcade
import math
import random


class Wisp(arcade.Sprite):
    def __init__(self, x, y, sprites_list, speed=100, scale=1.0, scale_factor=1.0):
        super().__init__()

        self.textures = sprites_list
        if self.textures:
            self.texture = self.textures[0]

        self.center_x = x
        self.center_y = y
        self.scale = scale
        self.scale_factor = scale_factor # <--- Сохраняем

        self.speed = speed
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 1.0 / 22.0

        self.hitbox_factor = 0.6

        s_val = self.scale[0] if isinstance(self.scale, tuple) else self.scale
        self.radius = (self.texture.width * s_val * self.hitbox_factor) / 2

    def update(self, dt: float, width: int, height: int, coins: list, grabbed_coin) -> None:
        # 1. Движение
        self.center_x += self.vx * dt
        self.center_y += self.vy * dt

        # 2. Отскок от стенок
        bounced = False
        if self.left < 0:
            self.left = 0
            self.vx *= -1
            bounced = True
        elif self.right > width:
            self.right = width
            self.vx *= -1
            bounced = True

        if self.bottom < 0:
            self.bottom = 0
            self.vy *= -1
            bounced = True
        elif self.top > height:
            self.top = height
            self.vy *= -1
            bounced = True

        if bounced:
            current_speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
            if current_speed > 0:
                self.vx = (self.vx / current_speed) * self.speed
                self.vy = (self.vy / current_speed) * self.speed

        # 3. Анимация
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.anim_index = (self.anim_index + 1) % len(self.textures)
            self.texture = self.textures[self.anim_index]

        # 4. Столкновение с монетками
        self._handle_coin_collisions(coins, grabbed_coin)

    def _handle_coin_collisions(self, coins: list, grabbed_coin) -> None:
        for coin in coins:

            # Игнорируем зажатую монетку
            if coin is grabbed_coin:
                continue

            # Игнорируем монетку с иммунитетом
            if coin.wisp_immunity_timer > 0:
                continue

            dx = coin.sprite.center_x - self.center_x
            dy = coin.sprite.center_y - self.center_y
            dist_sq = dx * dx + dy * dy
            min_dist = self.radius + coin.radius

            if dist_sq < min_dist * min_dist:
                dist = math.sqrt(dist_sq)
                if dist > 0:
                    nx = dx / dist
                    ny = dy / dist
                    coin.hit_by_coin(None, nx, ny)
                    coin.wisp_immunity_timer = 3.0

    def upgrade_speed(self, amount: float):
        # ИСПРАВЛЕНИЕ: Масштабируем добавку скорости
        self.speed += amount * self.scale_factor
        current_speed_vec = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if current_speed_vec > 0:
            self.vx = (self.vx / current_speed_vec) * self.speed
            self.vy = (self.vy / current_speed_vec) * self.speed

    def upgrade_scale(self, amount_percent: float):
        multiplier = 1.0 + amount_percent

        if isinstance(self.scale, tuple):
            sx, sy = self.scale
            self.scale = (sx * multiplier, sy * multiplier)
        else:
            self.scale *= multiplier

        # Пересчитываем радиус на основе новой шкалы
        s_val = self.scale[0] if isinstance(self.scale, tuple) else self.scale
        self.radius = (self.texture.width * s_val * self.hitbox_factor) / 2