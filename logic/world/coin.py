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
        self.landed = False
        self.fixed_outcome_texture = None

        # Для звуков и эффектов
        self.needs_toss_sound = False
        self.explosion_chance = 0.0
        self.victims_to_flip = []
        self.just_landed = False

        # --- СИСТЕМА ИММУНИТЕТА К ВИСПУ ---
        self.wisp_immunity_timer = 0.0

    def update(self, dt: float, width: int, height: int, other_coins: list) -> None:
        # ИМПОРТ ВНУТРИ МЕТОДА
        from logic.world.gold_coin import GoldCoin

        # Обновляем таймер иммунитета
        if self.wisp_immunity_timer > 0:
            self.wisp_immunity_timer -= dt
            if self.wisp_immunity_timer < 0:
                self.wisp_immunity_timer = 0

        # --- 1. ПОЛЕТ (Сбор жертв) ---
        if self.is_moving:
            self.sprite.center_x += self.vx * dt
            self.sprite.center_y += self.vy * dt

            # Границы экрана
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

            # СБОР ЖЕРТВ ВЗРЫВА (Только для золота)
            if self.explosion_chance > 0:
                for other in other_coins:
                    if other is not self and not other.is_moving:
                        # Золото не взрывает другое золото
                        if isinstance(other, GoldCoin):
                            continue

                        dx = self.sprite.center_x - other.sprite.center_x
                        dy = self.sprite.center_y - other.sprite.center_y
                        dist_sq = dx * dx + dy * dy
                        min_dist = self.radius + other.radius

                        if dist_sq < (min_dist * min_dist) and dist_sq > 0:
                            dist = math.sqrt(dist_sq)
                            # Вектор от монетки К золоту
                            nx = dx / dist
                            ny = dy / dist
                            # Сохраняем с обратным знаком, чтобы улетело ОТ золотой
                            self.victims_to_flip.append({'coin': other, 'nx': -nx, 'ny': -ny})

        # --- 2. НА ЗЕМЛЕ (Физика и Взрыв) ---
        else:
            # Трение
            self.vx *= 0.9
            self.vy *= 0.9

            if abs(self.vx) < 0.5: self.vx = 0
            if abs(self.vy) < 0.5: self.vy = 0

            # Движение
            self.sprite.center_x += self.vx * dt
            self.sprite.center_y += self.vy * dt

            # ЭФФЕКТ ВЗРЫВА ПРИ ПРИЗЕМЛЕНИИ
            if self.just_landed and self.explosion_chance > 0 and isinstance(self, GoldCoin):
                if random.random() < 0.5:
                    for victim_data in self.victims_to_flip:
                        victim_data['coin'].hit_by_coin(self, victim_data['nx'], victim_data['ny'])

                self.victims_to_flip = []

            # Обычная физика столкновений
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

                        # Анти-клип
                        max_instant_sep = 2.0
                        sep_mag = min(overlap * 0.5, max_instant_sep)

                        self.sprite.center_x += sep_mag * nx
                        self.sprite.center_y += sep_mag * ny
                        other.sprite.center_x -= sep_mag * nx
                        other.sprite.center_y -= sep_mag * ny

                        # Отталкивание
                        stiffness = 4.8
                        push = overlap * stiffness

                        self.vx += nx * push
                        self.vy += ny * push
                        other.vx -= nx * push
                        other.vy -= ny * push

            # Границы экрана
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
        self.landed = True
        self.just_landed = True

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

    def hit_by_coin(self, source_coin, nx, ny) -> None:
        """
        Вызывается, когда другая монетка (например, золото) 'ударила' эту.
        """
        self.is_moving = True
        self.vx = nx * 600
        self.vy = ny * 600

        # Выбор анимации (с учетом диагоналей)
        self._select_flying_animation()

        self.anim_index = 0
        if self.anim:
            self.sprite.texture = self.anim[0]

        self.needs_toss_sound = True

    def hit(self, dx: int, dy: int) -> None:
        self.is_moving = True
        self.vx = 0
        self.vy = 0

        length = math.sqrt(dx * dx + dy * dy)
        dead_zone = self.radius * 0.2

        if length < dead_zone:
            # Случайное направление при клике в центр
            angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(angle) * 600
            self.vy = math.sin(angle) * 600
        else:
            # Направление от клика (улетает ОТ курсора)
            if length > 0:
                self.vx = (-dx / length) * 600
                self.vy = (-dy / length) * 600

        # Выбор анимации (с учетом диагоналей)
        self._select_flying_animation()

        self.anim_index = 0
        if self.anim:
            self.sprite.texture = self.anim[0]

        self.needs_toss_sound = True

    def check_land_event(self):
        val = self.last_outcome_value
        self.last_outcome_value = 0
        return val

    def _select_flying_animation(self):
        """
        Вспомогательный метод: выбирает правильный список спрайтов
        в зависимости от вектора скорости vx, vy
        """
        # Коэффициент 1.5 определяет "зону" диагонали.
        # Если скорость по X > 1.5 * скорость по Y -> считаем прямым полетом по X.
        # Если скорости примерно равны -> считаем диагональю.
        if abs(self.vx) > 1.5 * abs(self.vy):
            # Горизонтальный полет (Влево или Вправо)
            self.anim = self.sprites.get("right", []) if self.vx > 0 else self.sprites.get("left", [])
        elif abs(self.vy) > 1.5 * abs(self.vx):
            # Вертикальный полет (Вверх или Вниз)
            self.anim = self.sprites.get("up", []) if self.vy > 0 else self.sprites.get("down", [])
        else:
            # Диагональный полет
            if self.vx > 0 and self.vy > 0:
                self.anim = self.sprites.get("up_right", [])
            elif self.vx > 0 and self.vy < 0:
                self.anim = self.sprites.get("down_right", [])
            elif self.vx < 0 and self.vy > 0:
                self.anim = self.sprites.get("up_left", [])
            else:  # vx < 0, vy < 0
                self.anim = self.sprites.get("down_left", [])