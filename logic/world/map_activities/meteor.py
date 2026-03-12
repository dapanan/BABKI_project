import pygame
import random
from logic.assets.sprite_pygame import PygameSprite


class Meteor(PygameSprite):
    def __init__(self, start_x: float, start_y: float, target_y: float, textures: list):
        # 1. Определяем начальную текстуру
        start_texture = None
        self.textures = textures

        if self.textures:
            start_texture = self.textures[0]
        else:
            # Создаем заглушку через Pygame (красный квадрат)
            start_texture = pygame.Surface((50, 50), pygame.SRCALPHA)
            start_texture.fill((255, 0, 0))
            self.texture = start_texture

        # 2. Инициализируем родительский класс PygameSprite
        super().__init__(image=start_texture)

        self.center_x = start_x
        self.center_y = start_y
        self.trail_timer = 0.0

        self.target_y = target_y
        self.speed = 1000.0

    def update(self, dt: float) -> bool:
        """Возвращает True если нужно создать дым (по таймеру) или если ударился о землю"""
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

    def draw(self, surface, screen_height) -> None:
        super().draw(surface, screen_height)