import arcade
import math
import random


class MultiplyZone:
    def __init__(self, width: int, height: int, multiplier: float, color: tuple):
        self.x = width / 2
        self.y = height / 2

        self.size = 75
        self.width = self.size
        self.height = self.size

        self.speed = 100.0
        angle = random.uniform(0, 6.28)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

        self.multiplier = multiplier
        self.color = color

    def update(self, dt: float, screen_width: int, screen_height: int) -> None:
        # Движение
        self.x += self.vx * dt
        self.y += self.vy * dt

        half_w = self.width / 2
        half_h = self.height / 2

        bounced = False
        if self.x - half_w < 0:
            self.x = half_w
            self.vx *= -1
            bounced = True
        elif self.x + half_w > screen_width:
            self.x = screen_width - half_w
            self.vx *= -1
            bounced = True

        if self.y - half_h < 0:
            self.y = half_h
            self.vy *= -1
            bounced = True
        elif self.y + half_h > screen_height:
            self.y = screen_height - half_h
            self.vy *= -1
            bounced = True

        if bounced:
            factor = random.uniform(0.75, 1.25)
            self.speed *= factor

            min_speed = 100.0
            max_speed = 500.0
            if self.speed < min_speed: self.speed = min_speed
            if self.speed > max_speed: self.speed = max_speed

            current_vec_len = math.sqrt(self.vx ** 2 + self.vy ** 2)
            if current_vec_len > 0:
                self.vx = (self.vx / current_vec_len) * self.speed
                self.vy = (self.vy / current_vec_len) * self.speed

    def draw(self) -> None:
        left_x = self.x - self.width / 2
        bottom_y = self.y - self.height / 2

        arcade.draw_lbwh_rectangle_filled(left_x, bottom_y, self.width, self.height, (100, 255, 100, 25))

        border_color = (self.color[0], self.color[1], self.color[2], 50)
        arcade.draw_lbwh_rectangle_outline(left_x, bottom_y, self.width, self.height, border_color, 1)

        arcade.draw_text(f"x{self.multiplier:.2f}", self.x, self.y,
                         (100, 150, 100, 150), 16, anchor_x="center", anchor_y="center", bold=True)

    def check_collision(self, coin) -> bool:
        """Проверяет, находится ли центр монетки внутри зоны"""
        half_w = self.width / 2
        half_h = self.height / 2

        cx = coin.sprite.center_x
        cy = coin.sprite.center_y
        if (self.x - half_w <= cx <= self.x + half_w) and \
                (self.y - half_h <= cy <= self.y + half_h):
            return True
        return False

    def upgrade_size(self, multiplier: float):
        """Увеличивает размер на множитель (как у виспа)"""
        self.size *= multiplier
        self.width = self.size
        self.height = self.size

    def upgrade_multiplier(self, amount: float):
        self.multiplier += amount