import pygame
import math
import random

class MultiplyZone:
    """
    Зона умножения. Не наследуется от PygameSprite, чтобы избежать конфликтов свойств.
    Имеет свои координаты и размеры.
    """
    def __init__(self, width: int, height: int, multiplier: float, color: tuple):
        # Позиция центра
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

        # Шрифт для отрисовки
        self.font = pygame.font.SysFont("arial", 16, bold=True)

    def update(self, dt: float, screen_width: int, screen_height: int) -> None:
        # Движение
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Столкновения со стенами
        bounced = False
        if self.left < 0:
            self.left = 0
            self.vx *= -1
            bounced = True
        elif self.right > screen_width:
            self.right = screen_width
            self.vx *= -1
            bounced = True

        if self.bottom < 0:
            self.bottom = 0
            self.vy *= -1
            bounced = True
        elif self.top > screen_height:
            self.top = screen_height
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

    def draw(self, surface, screen_height) -> None:
        # Координаты для рисования (Левый верхний угол)
        draw_x = self.x - self.width / 2
        draw_y = screen_height - (self.y + self.height / 2)

        # Создаем временную поверхность для прозрачности
        temp_surface = pygame.Surface((int(self.width), int(self.height)), pygame.SRCALPHA)

        # Заполняем цветом (прозрачность 25/255)
        fill_color = (self.color[0], self.color[1], self.color[2], 25)
        temp_surface.fill(fill_color)

        # Рисуем рамку (прозрачность 50/255)
        border_color = (self.color[0], self.color[1], self.color[2], 50)
        pygame.draw.rect(temp_surface, border_color, temp_surface.get_rect(), 1)

        # Рисуем текст
        text_surf = self.font.render(f"x{self.multiplier:.2f}", True, (100, 150, 100, 150))
        text_rect = text_surf.get_rect(center=(self.width / 2, self.height / 2))
        temp_surface.blit(text_surf, text_rect)

        # Рисуем временную поверхность на главном экране
        surface.blit(temp_surface, (draw_x, draw_y))

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
        """Увеличивает размер на множитель"""
        self.size *= multiplier
        self.width = self.size
        self.height = self.size

    def upgrade_multiplier(self, amount: float):
        self.multiplier += amount

    # --- Свойства границ (нужны для физики/столкновений) ---
    @property
    def left(self):
        return self.x - self.width / 2

    @left.setter
    def left(self, value):
        self.x = value + self.width / 2

    @property
    def right(self):
        return self.x + self.width / 2

    @right.setter
    def right(self, value):
        self.x = value - self.width / 2

    @property
    def top(self):
        return self.y + self.height / 2

    @top.setter
    def top(self, value):
        self.y = value - self.height / 2

    @property
    def bottom(self):
        return self.y - self.height / 2

    @bottom.setter
    def bottom(self, value):
        self.y = value + self.height / 2