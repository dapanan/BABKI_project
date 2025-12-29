import arcade
import random
import math


class Coin:
    SIZE = 100
    RADIUS = SIZE / 2

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

        # Физика
        self.vx = 0.0
        self.vy = 0.0
        self.radius = self.RADIUS * self.scale

        # Анимация полета
        self.anim = []
        self.anim_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.05

        # Состояние
        self.is_moving = False
        self.last_outcome_value = 0

    def update(self, dt: float, width: int, height: int, other_coins: list) -> None:
        # Если монетка летит
        if self.is_moving:
            # Двигаем монетку
            self.sprite.center_x += self.vx * dt
            self.sprite.center_y += self.vy * dt

            if self.sprite.left < 0:
                self.sprite.left = 0
            elif self.sprite.right > width:
                self.sprite.right = width

            if self.sprite.bottom < 0:
                self.sprite.bottom = 0
            elif self.sprite.top > height:
                self.sprite.top = height

            # Логика анимации вращения
            if self.anim:
                self.anim_timer += dt
                if self.anim_timer >= self.anim_speed:
                    self.anim_timer = 0
                    self.anim_index += 1
                    if self.anim_index < len(self.anim):
                        self.sprite.texture = self.anim[self.anim_index]
                    else:
                        # Анимация закончилась -> теперь падаем
                        self.land()
            else:
                # Если картинок для анимации нет, сразу падаем
                self.land()

        # Физика на земле (когда монетка стоит)
        else:
            # Столкновения с другими монетами (расталкивание)
            for other in other_coins:
                if other is not self and not other.is_moving:
                    dx = self.sprite.center_x - other.sprite.center_x
                    dy = self.sprite.center_y - other.sprite.center_y
                    dist = math.sqrt(dx * dx + dy * dy)
                    min_dist = self.radius + other.radius

                    if dist < min_dist and dist > 0:
                        overlap = min_dist - dist
                        nx = dx / dist
                        ny = dy / dist
                        move_x = nx * overlap * 0.5
                        move_y = ny * overlap * 0.5

                        self.sprite.center_x += move_x
                        self.sprite.center_y += move_y
                        other.sprite.center_x -= move_x
                        other.sprite.center_y -= move_y

            # Границы экрана (для стоячей монетки)
            if self.sprite.left < 0:
                self.sprite.left = 0
            elif self.sprite.right > width:
                self.sprite.right = width

            if self.sprite.bottom < 0:
                self.sprite.bottom = 0
            elif self.sprite.top > height:
                self.sprite.top = height

    def land(self) -> None:
        self.is_moving = False
        self.vx = 0
        self.vy = 0
        self.anim = []

        # Результат: Орел или Решка
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