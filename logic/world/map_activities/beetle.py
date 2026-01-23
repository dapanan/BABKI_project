import arcade
import random


class Beetle(arcade.Sprite):
    def __init__(self, x, y, sprites_dict):
        super().__init__()

        # Загрузка текстур
        self.frames = sprites_dict

        self.current_anim_frames = []
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.2

        # Установка текстуры
        if self.frames.get("down") and len(self.frames["down"]) > 0:
            self.texture = self.frames["down"][0]
            self.current_anim_frames = self.frames["down"]
        else:
            # Заглушка (если не загрузились текстуры)
            from PIL import Image
            pil_image = Image.new("RGBA", (64, 64), arcade.color.PURPLE)
            self.texture = arcade.Texture(image=pil_image)
            self.current_anim_frames = [self.texture]

        self.center_x = x
        self.center_y = y

        # ПАРАМЕТРЫ ЖУКА
        self.scale = 0.3  # Размер (0.3 - в 3+ раза меньше монет)
        self.speed = 80.0  # Скорость (медленная)

        # Логика движения
        self.state = "IDLE"
        self.move_duration = 2.0
        self.idle_duration = 5.0
        self.move_timer = 0.0
        self.idle_timer = 0.0

        self.vx = 0
        self.vy = 0

        self.directions = {
            "up": (0, 1), "down": (0, -1), "left": (-1, 0), "right": (1, 0)
        }
        self.last_hit_walls = []

        # Логика смерти
        self.can_be_clicked = True
        self.is_dying = False
        self.fade_duration = 1.8
        self.fade_timer = 0.0

    def set_direction(self, direction_name):
        """Переключает спрайты направления"""
        if direction_name in self.frames and len(self.frames[direction_name]) > 0:
            self.current_anim_frames = self.frames[direction_name]
        elif "down" in self.frames and len(self.frames["down"]) > 0:
            self.current_anim_frames = self.frames["down"]

        self.frame_index = 0
        if self.current_anim_frames:
            self.texture = self.current_anim_frames[0]

    def start_death(self):
        """Начало смерти (клик)"""
        self.is_dying = True
        self.can_be_clicked = False
        self.fade_timer = 0.0
        self.vx = 0
        self.vy = 0

    def update(self, dt: float, screen_width: int, screen_height: int) -> bool:
        """
        Обновление жука.
        Возвращает True если жив, False если умер.
        """

        # 1. ЛОГИКА СМЕРТИ
        if self.is_dying:
            # ЗАЩИТА ОТ ЛАГОВ: Ограничиваем dt, чтобы анимация не проскочила
            safe_dt = min(dt, 0.1)

            self.fade_timer += safe_dt
            alpha = 255 * (1.0 - (self.fade_timer / self.fade_duration))
            if alpha < 0: alpha = 0

            # Меняем прозрачность
            r, g, b, _ = self.color
            self.color = (int(r), int(g), int(b), int(alpha))

            if self.fade_timer >= self.fade_duration:
                return False  # СМЕРТЬ

            return True  # Умирает, но еще на экране

        # 2. АНИМАЦИЯ (если идет)
        if self.state == "MOVING" and len(self.current_anim_frames) > 1:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.current_anim_frames)
                self.texture = self.current_anim_frames[self.frame_index]

        # 3. ЛОГИКА СОСТОЯНИЙ
        if self.state == "IDLE":
            self.idle_timer += dt
            if self.idle_timer >= self.idle_duration:
                self.start_moving()
                self.idle_timer = 0.0

        elif self.state == "MOVING":
            self.move_timer += dt
            if self.move_timer >= self.move_duration:
                self.stop_moving()
                self.move_timer = 0.0

        # 4. ДВИЖЕНИЕ
        self.center_x += self.vx * dt
        self.center_y += self.vy * dt

        # 5. СТЕНЫ
        self._handle_walls(screen_width, screen_height)

        # Если мы не умерли в начале функции, мы точно живы
        return True

    def start_moving(self):
        self.state = "MOVING"
        self.choose_direction()

    def stop_moving(self):
        self.state = "IDLE"
        self.vx = 0
        self.vy = 0
        self.last_hit_walls = []
        if self.current_anim_frames:
            self.frame_index = 0
            self.texture = self.current_anim_frames[0]

    def choose_direction(self):
        valid_dirs = []
        for name, vec in self.directions.items():
            dx, dy = vec
            is_bad = False
            if dx > 0 and "RIGHT" in self.last_hit_walls: is_bad = True
            if dx < 0 and "LEFT" in self.last_hit_walls: is_bad = True
            if dy > 0 and "UP" in self.last_hit_walls: is_bad = True
            if dy < 0 and "DOWN" in self.last_hit_walls: is_bad = True
            if not is_bad:
                valid_dirs.append(name)

        if not valid_dirs:
            valid_dirs = list(self.directions.keys())

        chosen_name = random.choice(valid_dirs)
        vec = self.directions[chosen_name]

        self.vx = vec[0] * self.speed
        self.vy = vec[1] * self.speed
        self.last_hit_walls = []

        self.set_direction(chosen_name)

    def _handle_walls(self, screen_width, screen_height):
        half_size = self.width / 2
        hit_something = False

        if self.right > screen_width:
            self.right = screen_width
            self.last_hit_walls.append("RIGHT")
            self.vx *= -1
            hit_something = True
        elif self.left < 0:
            self.left = 0
            self.last_hit_walls.append("LEFT")
            self.vx *= -1
            hit_something = True

        if self.top > screen_height:
            self.top = screen_height
            self.last_hit_walls.append("UP")
            self.vy *= -1
            hit_something = True
        elif self.bottom < 0:
            self.bottom = 0
            self.last_hit_walls.append("DOWN")
            self.vy *= -1
            hit_something = True

        if hit_something and self.state == "MOVING":
            self.choose_direction()

    def draw(self) -> None:
        # Рисуем только если видимы (альфа > 0)
        if self.is_dying and self.color[3] <= 0:
            return
        arcade.draw_sprite(self)