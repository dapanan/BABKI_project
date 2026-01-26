import arcade


class Crater(arcade.Sprite):
    def __init__(self, x: float, y: float, texture: arcade.Texture):
        super().__init__(texture)
        self.center_x = x
        self.center_y = y

        self.multiplier = 20.0

        # Таймеры жизни
        self.life_duration = 10.0  # Живет 10 секунд
        self.fade_duration = 0.5  # Исчезает за 0.5 секунды
        self.timer = 0.0
        self.is_fading = False

    def update(self, dt: float) -> bool:
        """Возвращает False, если объект нужно удалить"""
        self.timer += dt

        if self.is_fading:
            # Плавно меняем прозрачность
            progress = self.timer / self.life_duration  # Будет > 1.0

            # Сколько прошло времени в фазе исчезновения
            fade_time = self.timer - self.life_duration
            alpha_ratio = 1.0 - (fade_time / self.fade_duration)

            if alpha_ratio < 0: alpha_ratio = 0

            r, g, b, _ = self.color
            self.color = (int(r), int(g), int(b), int(255 * alpha_ratio))

            if alpha_ratio <= 0:
                return False  # Умер
        else:
            # Просто тикаем время жизни
            if self.timer >= self.life_duration:
                self.is_fading = True

        return True  # Жив

    def check_collision(self, coin) -> bool:
        """AABB Collision для прямоугольного кратера"""
        cx = coin.sprite.center_x
        cy = coin.sprite.center_y

        half_w = self.width / 2
        half_h = self.height / 2

        # Проверяем попадание центра монетки в прямоугольник
        if (self.center_x - half_w <= cx <= self.center_x + half_w) and \
                (self.center_y - half_h <= cy <= self.center_y + half_h):
            return True
        return False

    def draw(self) -> None:
        arcade.draw_sprite(self)