import arcade
import random
import math


class Coin:
    def __init__(
            self,
            x: float,
            y: float,
            sprites: dict,
            value: int,
            scale: float = 1.0
    ) -> None:
        self.value = value
        self.sprites = sprites
        self.scale = scale

        self.sprite = arcade.Sprite()
        self.sprite.center_x = x
        self.sprite.center_y = y
        self.sprite.scale = self.scale
        self.sprite.texture = sprites["heads"]
        # ВАЖНО: Радиус теперь вычисляется ТОЧНО по ширине спрайта
        # Это гарантирует, что физический круг совпадает с картинкой 1 в 1
        # (self.sprite.width это текущая ширина картинки с учетом scale)
        self.radius = self.sprite.width / 2

        # Физика
        self.vx = 0.0
        self.vy = 0.0

        # Анимация полета
        self.anim = []
        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.05

        # Состояние
        self.is_moving = False
        self.last_outcome_value = 0

    def update(self, dt: float, width: int, height: int, other_coins: list) -> None:
        # 1. ЛОГИКА ПОЛЕТА (is_moving = True)
        if self.is_moving:
            self.sprite.center_x += self.vx * dt
            self.sprite.center_y += self.vy * dt

            # Границы экрана (Ограничение, но не посадка)
            if self.sprite.left < 0:
                self.sprite.left = 0
            elif self.sprite.right > width:
                self.sprite.right = width

            if self.sprite.bottom < 0:
                self.sprite.bottom = 0
            elif self.sprite.top > height:
                self.sprite.top = height

            # Анимация
            if self.anim:
                self.anim_timer += dt
                if self.anim_timer >= self.anim_speed:
                    self.anim_timer = 0
                    self.anim_index += 1
                    if self.anim_index < len(self.anim):
                        self.sprite.texture = self.anim[self.anim_index]
                    else:
                        self.land()
            else:
                self.land()

        # 2. ЛОГИКА НА ЗЕМЛЕ (is_moving = False) - ОПТИМИЗИРОВАННАЯ ФИЗИКА
        else:
            # Применяем трение, чтобы монетки останавливались после столкновений
            # Это делает движение реалистичнее и предотвращает дрожание
            self.vx *= 0.90
            self.vy *= 0.90

            # Если скорость очень маленькая, зануляем её полностью (оптимизация CPU)
            if abs(self.vx) < 0.5: self.vx = 0
            if abs(self.vy) < 0.5: self.vy = 0

            # Двигаем монетку (инерция)
            self.sprite.center_x += self.vx * dt
            self.sprite.center_y += self.vy * dt

            # Оптимизированная проверка столкновений с другими монетками
            # Мы проверяем только те монетки, которые тоже не летят
            for other in other_coins:
                if other is not self and not other.is_moving:

                    # Вектор разницы позиций
                    dx = self.sprite.center_x - other.sprite.center_x
                    dy = self.sprite.center_y - other.sprite.center_y

                    # Считаем квадрат расстояния (быстро)
                    dist_sq = dx * dx + dy * dy

                    # Сумма радиусов
                    min_dist = self.radius + other.radius

                    # Если квадрат расстояния меньше квадрата радиуса -> есть столкновение
                    # Мы избегаем math.sqrt, пока это не нужно
                    if dist_sq < (min_dist * min_dist) and dist_sq > 0:
                        # Вот здесь точно есть столкновение, считаем точную дистанцию
                        dist = math.sqrt(dist_sq)
                        overlap = min_dist - dist

                        # Нормаль вектора (направление отталкивания)
                        nx = dx / dist
                        ny = dy / dist

                        # Раздвигаем монетки в разные стороны (каждую на половину перекрытия)
                        move_x = nx * overlap * 0.5
                        move_y = ny * overlap * 0.5

                        self.sprite.center_x += move_x
                        self.sprite.center_y += move_y
                        other.sprite.center_x -= move_x
                        other.sprite.center_y -= move_y

                        # Передаем немного импульса (чтобы они отскакивали)
                        # Это небольшой коэффициент отталкивания
                        bounce = 20.0
                        self.vx += nx * bounce
                        self.vy += ny * bounce
                        other.vx -= nx * bounce
                        other.vy -= ny * bounce

            # Границы экрана для стоячей монетки
            if self.sprite.left < 0:
                self.sprite.left = 0
                self.vx *= -0.5  # Отскок от стены с потерей энергии
            elif self.sprite.right > width:
                self.sprite.right = width
                self.vx *= -0.5

            if self.sprite.bottom < 0:
                self.sprite.bottom = 0
                self.vy *= -0.5
            elif self.sprite.top > height:
                self.sprite.top = height
                self.vy *= -0.5

    def land(self) -> None:
        """Вызывается, когда монетка заканчивает полет"""
        self.is_moving = False
        self.vx = 0
        self.vy = 0
        self.anim = []

        is_heads = random.random() < 0.5

        if is_heads:
            self.sprite.texture = self.sprites["heads"]
            self.last_outcome_value = self.value
        else:
            self.sprite.texture = self.sprites["tails"]
            self.last_outcome_value = 0

    def draw(self) -> None:
        if self.is_moving:
            arcade.draw_circle_filled(
                self.sprite.center_x,
                self.sprite.center_y - 10,
                self.radius,
                (0, 0, 0, 50)
            )

        arcade.draw_sprite(self.sprite)

    def hit(self, dx: int, dy: int) -> None:
        self.is_moving = True

        # Убираем старую скорость, чтобы не суммировалась с новой
        self.vx = 0
        self.vy = 0

        if abs(dx) < 20 and abs(dy) < 20:
            angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(angle) * 600
            self.vy = math.sin(angle) * 600
        else:
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                self.vx = (-dx / length) * 600
                self.vy = (-dy / length) * 600

        # Выбор анимации
        if abs(self.vx) > abs(self.vy):
            self.anim = self.sprites.get("right", []) if self.vx > 0 else self.sprites.get("left", [])
        else:
            self.anim = self.sprites.get("up", []) if self.vy > 0 else self.sprites.get("down", [])

        self.anim_index = 0
        if self.anim:
            self.sprite.texture = self.anim[0]

    def check_land_event(self):
        val = self.last_outcome_value
        self.last_outcome_value = 0
        return val