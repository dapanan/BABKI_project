import arcade
import random


class Meteor(arcade.Sprite):
    def __init__(self, start_x: float, start_y: float, target_y: float, textures: list):
        super().__init__()
        # Анимация падения
        self.textures = textures
        if self.textures:
            self.texture = self.textures[0]
        else:
            # Заглушка
            from PIL import Image
            tex = arcade.Texture(image=Image.new("RGBA", (50, 50), (255, 0, 0)))
            self.texture = tex

        self.center_x = start_x
        self.center_y = start_y
        self.trail_timer = 0.0

        self.target_y = target_y
        self.speed = 1000.0

    def update(self, dt: float) -> bool:
        """Возвращает True если долетел до земли"""
        self.center_y -= self.speed * dt

        # Генерация дыма
        self.trail_timer += dt
        if self.trail_timer >= 0.05:
            self.trail_timer = 0
            return True

        if self.center_y <= self.target_y:
            self.center_y = self.target_y
            return True
        return False

    def draw(self) -> None:
        arcade.draw_sprite(self)