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

        self.sprite.texture = sprites["heads"]
        self.sprite.scale = self.scale

        self.radius = 32.0 * self.scale

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

        # Флаг приземления (для звука)
        self.landed = False
        self.fixed_outcome_texture = None

    def update(self, dt: float, width: int, height: int, other_coins: list) -> None:
        if self.is_moving:
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
        else:
            self.vx *= 0.9
            self.vy *= 0.9

            if abs(self.vx) < 0.5: self.vx = 0
            if abs(self.vy) < 0.5: self.vy = 0

            self.sprite.center_x += self.vx * dt
            self.sprite.center_y += self.vy * dt

            for other in other_coins:
                if other is not self and not other.is_moving:
                    dx = self.sprite.center_x - other.sprite.center_x
                    dy = self.sprite.center_y - other.sprite.center_y
                    dist_sq = dx * dx + dy * dy
                    min_dist = self.radius + other.radius

                    if dist_sq < (min_dist * min_dist) and dist_sq > 0:
                        dist = math.sqrt(dist_sq)
                        overlap = min_dist - dist

                        nx = dx / dist
                        ny = dy / dist

                        max_instant_sep = 2.0
                        sep_mag = min(overlap * 0.5, max_instant_sep)

                        move_x = nx * sep_mag
                        move_y = ny * sep_mag

                        self.sprite.center_x += move_x
                        self.sprite.center_y += move_y
                        other.sprite.center_x -= move_x
                        other.sprite.center_y -= move_y

                        stiffness = 4.8
                        push = overlap * stiffness

                        self.vx += nx * push
                        self.vy += ny * push
                        other.vx -= nx * push
                        other.vy -= ny * push

            if self.sprite.left < 0:
                self.sprite.left = 0
                self.vx *= -0.5
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
        self.is_moving = False
        self.anim = []

        # ВАЖНО: Устанавливаем флаг приземления (Звук сыграет всегда)
        self.landed = True

        if self.fixed_outcome_texture:
            self.sprite.texture = self.fixed_outcome_texture

            if self.fixed_outcome_texture == self.sprites["heads"]:
                self.last_outcome_value = self.value
            else:
                self.last_outcome_value = 0

            self.fixed_outcome_texture = None
        else:
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
        self.vx = 0
        self.vy = 0

        # Считаем точное расстояние от клика до центра монетки
        length = math.sqrt(dx * dx + dy * dy)

        # Мертвая зона в виде круга (20% от радиуса монетки)
        dead_zone = self.radius * 0.2

        if length < dead_zone:
            # Если клик попал в центральный круг -> рандомный полет
            angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(angle) * 600
            self.vy = math.sin(angle) * 600
        else:
            # Если клик снаружи круга -> летим в противоположную сторону
            # Защита от деления на ноль (на случай dead_zone = 0)
            if length > 0:
                self.vx = (-dx / length) * 600
                self.vy = (-dy / length) * 600
            else:
                # Резервный вариант
                angle = random.uniform(0, 2 * math.pi)
                self.vx = math.cos(angle) * 600
                self.vy = math.sin(angle) * 600

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