import arcade


class Explosion(arcade.Sprite):
    def __init__(self, x: float, y: float, textures: list):
        super().__init__()

        self.frames = textures
        if self.frames:
            self.texture = self.frames[0]
        else:
            from PIL import Image
            self.texture = arcade.Texture(image=Image.new("RGBA", (100, 100), (255, 165, 0)))

        self.center_x = x
        self.center_y = y

        self.frame_index = 0
        self.timer = 0.0
        self.anim_speed = 0.05  # Скорость кадров (0.05 сек)

        self.alive = True  # Флаг: жива ли анимация

    def update(self, dt: float) -> bool:
        """Возвращает False если анимация закончилась"""
        self.timer += dt
        if self.timer >= self.anim_speed:
            self.timer = 0
            self.frame_index += 1

            if self.frame_index < len(self.frames):
                self.texture = self.frames[self.frame_index]
            else:
                # Анимация кончилась -> убиваем объект
                self.alive = False
                return False

        return True

    def draw(self) -> None:
        arcade.draw_sprite(self)