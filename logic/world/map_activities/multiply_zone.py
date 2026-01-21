import arcade
import math
import random


class MultiplyZone:
    def __init__(self, width: int, height: int, multiplier: float, color: tuple):
        # Начальная позиция (центр экрана)
        self.x = width / 2
        self.y = height / 2

        # Размеры зоны (квадрат)
        self.size = 75
        self.width = self.size
        self.height = self.size

        # Скорость
        self.speed = 100.0
        angle = random.uniform(0, 6.28)
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

        # Свойства зоны
        self.multiplier = multiplier
        self.color = color  # (R, G, B, Alpha)

    def update(self, dt: float, screen_width: int, screen_height: int) -> None:
        # Движение
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Отскок от стен (учитываем половину ширины/высоты)
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

        # Если был отскок - меняем скорость рандомно
        if bounced:
            # Выбираем множитель от 0.75 до 1.25 (то есть +/- 25%)
            factor = random.uniform(0.75, 1.25)
            self.speed *= factor

            # Пересчитываем вектора vx, vy под новую скорость
            current_vec_len = math.sqrt(self.vx ** 2 + self.vy ** 2)
            if current_vec_len > 0:
                self.vx = (self.vx / current_vec_len) * self.speed
                self.vy = (self.vy / current_vec_len) * self.speed

    def draw(self) -> None:
        # Вычисляем координаты левого нижнего угла
        left_x = self.x - self.width / 2
        bottom_y = self.y - self.height / 2

        # Рисуем ЗАЛИВКУ
        arcade.draw_lbwh_rectangle_filled(left_x, bottom_y, self.width, self.height, self.color)

        # Рисуем ОБВОДКУ
        border_color = (self.color[0], self.color[1], self.color[2], 100)
        arcade.draw_lbwh_rectangle_outline(left_x, bottom_y, self.width, self.height, border_color, 2)

        # Рисуем текст с множителем
        arcade.draw_text(f"x{self.multiplier:.2f}", self.x, self.y,
                         (255, 255, 255, 255), 16, anchor_x="center", anchor_y="center", bold=True)

    def check_collision(self, coin) -> bool:
        """Проверяет, находится ли центр монетки внутри зоны"""
        half_w = self.width / 2
        half_h = self.height / 2

        cx = coin.sprite.center_x
        cy = coin.sprite.center_y

        # AABB Collision (Point inside Rectangle)
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