import pygame
from logic.assets.sprite_pygame import PygameSprite


class Explosion(PygameSprite):
    def __init__(self, x: float, y: float, textures: list):
        # 1. Определяем начальную текстуру
        start_texture = None
        self.frames = textures

        if self.frames:
            start_texture = self.frames[0]
        else:
            # Создаем заглушку через Pygame (оранжевый квадрат)
            start_texture = pygame.Surface((100, 100), pygame.SRCALPHA)
            start_texture.fill((255, 165, 0))

        # 2. Инициализируем родительский класс PygameSprite
        super().__init__(image=start_texture)

        self.center_x = x
        self.center_y = y

        self.frame_index = 0
        self.timer = 0.0
        self.anim_speed = 0.05

        self.alive = True

    def update(self, dt: float) -> bool:
        """Возвращает False если анимация закончилась"""
        self.timer += dt
        if self.timer >= self.anim_speed:
            self.timer = 0
            self.frame_index += 1

            if self.frame_index < len(self.frames):
                # Используем setter свойства texture для обновления изображения
                self.texture = self.frames[self.frame_index]
            else:
                self.alive = False
                return False

        return True

    def draw(self, surface, screen_height) -> None:
        super().draw(surface, screen_height)