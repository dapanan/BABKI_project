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
            scale: float = 1.0,
            scale_factor: float = 1.0  # <--- Добавили аргумент масштаба мира
    ) -> None:
        self.value = value
        self.sprites = sprites
        self.scale = scale
        self.world_scale = scale_factor  # <--- Сохраняем для физики

        self.sprite = arcade.Sprite()
        self.sprite.center_x = x
        self.sprite.center_y = y

        self.sprite.texture = sprites["heads"]
        self.sprite.scale = self.scale

        self.radius = 32.0 * self.scale

        self.lifetime = None  # Время жизни (0 = бесконечно)
        self.fade_duration = 2.0 # Время угасания
        self.is_fading = False


        # === ИСПРАВЛЕНИЕ ДЛЯ SPATIAL HASH ===
        self.sprite.coin = self
        # ===========================================

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

        self.wisp_immunity_timer = 0.0
        self.tornado_hit = False

        self.manual_override = False

        self.MAX_SPEED = 2500.0 * self.world_scale  # <--- Масштабируем макс. скорость

    def update(self, dt: float, width: int, height: int, nearby_coins: list) -> None:

        # === ЛОГИКА УГАСАНИЯ (DISAPPEAR) ===
        # Проверяем, что lifetime существует и это число, больше нуля
        if self.lifetime is not None and self.lifetime > 0:
            self.lifetime -= dt
            # Если начали угасать, уменьшаем альфа
            if self.lifetime <= self.fade_duration:
                self.is_fading = True
                ratio = max(0, self.lifetime / self.fade_duration)
                self.sprite.alpha = int(255 * ratio)

            # Если время вышло, помечаем на удаление (в контроллере)
            if self.lifetime <= 0:
                return  # Не обновляем физику, если "мертв"
        # Список nearby_coins приходит из GameController, он уже оптимизирован через Spatial Hash
        from logic.world.gold_coin import GoldCoin

        if self.wisp_immunity_timer > 0:
            self.wisp_immunity_timer -= dt
            if self.wisp_immunity_timer < 0:
                self.wisp_immunity_timer = 0

        # --- БЛОК 1: ЛЕТАЮЩАЯ МОНЕТКА (is_moving = True) ---
        if self.is_moving:
            self.sprite.center_x += self.vx * dt
            self.sprite.center_y += self.vy * dt

            self._clamp_speed()
            self._handle_wall_bounce(width, height)

            # === ЛОГИКА В ТОРНАДО ===
            if self.tornado_hit:
                # НЕТ СОПРОТИВЛЕНИЯ ВОЗДУХА (1.0)
                self.vx *= 1.0
                self.vy *= 1.0

                # Анимация (меняем спрайт по кругу)
                self.anim_timer += dt
                if self.anim_timer >= self.anim_speed:
                    self.anim_timer = 0
                    if not self.anim or self.anim_index >= len(self.anim) - 1:
                        self._select_flying_animation()

                    if self.anim:
                        self.anim_index = (self.anim_index + 1) % len(self.anim)
                        self.sprite.texture = self.anim[self.anim_index]

            # === ЛОГИКА ВНЕ ТОРНАДО (Обычный полет) ===
            else:
                self.anim_timer += dt
                if self.anim_timer >= self.anim_speed:
                    self.anim_timer = 0
                    self.anim_index += 1

                    if self.anim and self.anim_index < len(self.anim):
                        self.sprite.texture = self.anim[self.anim_index]
                    else:
                        # Анимация кончилась -> Падение
                        self.land()

            # Сбор жертв взрыва
            if self.explosion_chance > 0:
                # Используем nearby_coins для оптимизации
                for other in nearby_coins:
                    if other is not self and not other.is_moving:
                        if isinstance(other, GoldCoin):
                            continue

                        dx = self.sprite.center_x - other.sprite.center_x
                        dy = self.sprite.center_y - other.sprite.center_y
                        dist_sq = dx * dx + dy * dy
                        min_dist = self.radius + other.radius

                        if dist_sq < (min_dist * min_dist) and dist_sq > 0:
                            dist = math.sqrt(dist_sq)
                            nx = dx / dist
                            ny = dy / dist
                            self.victims_to_flip.append({'coin': other, 'nx': -nx, 'ny': -ny})

        # --- БЛОК 2: ЛЕЖАЩАЯ МОНЕТКА (is_moving = False) ---
        else:
            # === В ТОРНАДО (Скользит) ===
            if self.tornado_hit:
                # Трение 0.96
                self.vx *= 0.96
                self.vy *= 0.96
                self._clamp_speed()

                if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
                    self.sprite.center_x += self.vx * dt
                    self.sprite.center_y += self.vy * dt

                self._handle_wall_bounce(width, height)

            # === ОБЫЧНАЯ ЗЕМЛЯ ===
            else:
                self.vx *= 0.9
                self.vy *= 0.9
                if abs(self.vx) < 0.5: self.vx = 0
                if abs(self.vy) < 0.5: self.vy = 0

                self.sprite.center_x += self.vx * dt
                self.sprite.center_y += self.vy * dt

                if self.fixed_outcome_texture:
                    self.sprite.texture = self.fixed_outcome_texture

            # Физика столкновений (теперь с оптимизацией)
            self._handle_collisions(nearby_coins)

            if not self.tornado_hit:
                self._handle_wall_bounce(width, height)

            # Эффект взрыва
            if self.just_landed and self.explosion_chance > 0 and isinstance(self, GoldCoin):
                if random.random() < 0.5:
                    for victim_data in self.victims_to_flip:
                        victim_data['coin'].hit_by_coin(self, victim_data['nx'], victim_data['ny'])
                self.victims_to_flip = []

    def land(self) -> None:
        if self.tornado_hit:
            return

        self.is_moving = False
        self.anim = []
        self.landed = True
        self.just_landed = True

        self.manual_override = False

        self.fixed_outcome_texture = None

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
            arcade.draw_sprite(self.sprite)
            arcade.draw_circle_filled(
                self.sprite.center_x,
                self.sprite.center_y - 10,
                self.radius,
                (0, 0, 0, 50)
            )
        arcade.draw_sprite(self.sprite)

    def hit_by_coin(self, source_coin, nx, ny) -> None:
        self.is_moving = True
        # ИСПРАВЛЕНИЕ: Скорость от столкновения тоже масштабируется
        self.vx = nx * (600 * self.world_scale)
        self.vy = ny * (600 * self.world_scale)
        self._select_flying_animation()
        self.anim_index = 0
        if self.anim:
            self.sprite.texture = self.anim[0]
        self.needs_toss_sound = True

    def hit(self, dx: int, dy: int) -> None:
        self.is_moving = True
        self.vx = 0
        self.vy = 0.0

        length = math.sqrt(dx * dx + dy * dy)
        dead_zone = self.radius * 0.2

        # ИСПРАВЛЕНИЕ: Базовая скорость зависит от масштаба экрана
        base_speed = 600 * self.world_scale

        if length < dead_zone:
            angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(angle) * base_speed
            self.vy = math.sin(angle) * base_speed
        else:
            if length > 0:
                self.vx = (-dx / length) * base_speed
                self.vy = (-dy / length) * base_speed

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
        if abs(self.vx) > 1.5 * abs(self.vy):
            self.anim = self.sprites.get("right", []) if self.vx > 0 else self.sprites.get("left", [])
        elif abs(self.vy) > 1.5 * abs(self.vx):
            self.anim = self.sprites.get("up", []) if self.vy > 0 else self.sprites.get("down", [])
        else:
            if self.vx > 0 and self.vy > 0:
                self.anim = self.sprites.get("up_right", [])
            elif self.vx > 0 and self.vy < 0:
                self.anim = self.sprites.get("down_right", [])
            elif self.vx < 0 and self.vy > 0:
                self.anim = self.sprites.get("up_left", [])
            else:
                self.anim = self.sprites.get("down_left", [])

        if not self.anim:
            if abs(self.vx) > abs(self.vy):
                self.anim = self.sprites.get("right", []) if self.vx > 0 else self.sprites.get("left", [])
            else:
                self.anim = self.sprites.get("up", []) if self.vy > 0 else self.sprites.get("down", [])

        if not self.anim:
            self.anim = [self.sprites.get("heads")]

    def _handle_collisions(self, nearby_coins):
        for other in nearby_coins:
            if other is not self:
                # === ИСПРАВЛЕНИЕ: Летящие монетки не сталкиваются с остальными ===
                if other.is_moving:
                    continue
                # ================================================================

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

                    stiffness = 4.8
                    push = overlap * stiffness
                    self.vx += nx * push
                    self.vy += ny * push
                    other.vx -= nx * push
                    other.vy -= ny * push

    def _handle_wall_bounce(self, width, height):
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

    def _clamp_speed(self):
        current_speed_sq = self.vx * self.vx + self.vy * self.vy
        if current_speed_sq > self.MAX_SPEED ** 2:
            current_speed = math.sqrt(current_speed_sq)
            ratio = self.MAX_SPEED / current_speed
            self.vx *= ratio
            self.vy *= ratio