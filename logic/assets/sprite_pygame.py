import pygame


class PygameSprite:
    """
    Обертка вокруг pygame.Surface.
    Работает с RAW (сырыми) текстурами и применяет масштаб динамически.
    """

    def __init__(self, image=None, scale: float = 1.0):
        self._raw_image = image  # Текущая "сырая" текстура (кадр анимации)
        self._image = None  # Отмасштабированная текстура (что рисуем)
        self._scale = scale  # Текущий коэффициент масштаба

        self.center_x = 0.0
        self.center_y = 0.0
        self.angle = 0.0
        self.alpha = 255
        self.color = (255, 255, 255, 255)
        self.coin = None

        # Кэшированные размеры
        self._width_cache = 0
        self._height_cache = 0

        # Первичная инициализация (применяем масштаб к стартовой картинке)
        self._apply_scale()

    def _apply_scale(self):
        """Вспомогательный метод: берет _raw_image и масштабирует её в _image с учетом self._scale"""
        if self._raw_image:
            w = int(self._raw_image.get_width() * self._scale)
            h = int(self._raw_image.get_height() * self.scale)
            self._image = pygame.transform.smoothscale(self._raw_image, (w, h))

            self._width_cache = self._image.get_width()
            self._height_cache = self._image.get_height()
        else:
            # Заглушка
            self._image = pygame.Surface((32, 32), pygame.SRCALPHA)
            self._image.fill((0, 0, 0, 0))
            self._width_cache = 32
            self._height_cache = 32

    @property
    def texture(self):
        return self._image

    @texture.setter
    def texture(self, value):
        # При смене текстуры (анимация) сохраняем её как новую "сырую"
        self._raw_image = value
        # Сразу пересчитываем размер с текущим масштабом
        self._apply_scale()

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        # При смене масштаба пересчитываем размер текущей текстуры
        self._apply_scale()

    # --- Геттеры координат ---
    @property
    def left(self):
        return self.center_x - self.width / 2

    @left.setter
    def left(self, value):
        self.center_x = value + self.width / 2

    @property
    def right(self):
        return self.center_x + self.width / 2

    @right.setter
    def right(self, value):
        self.center_x = value - self.width / 2

    @property
    def top(self):
        return self.center_y + self.height / 2

    @top.setter
    def top(self, value):
        self.center_y = value - self.height / 2

    @property
    def bottom(self):
        return self.center_y - self.height / 2

    @bottom.setter
    def bottom(self, value):
        self.center_y = value + self.height / 2

    # --- Размеры ---
    @property
    def width(self):
        return self._width_cache

    @property
    def height(self):
        return self._height_cache

    def draw(self, surface: pygame.Surface, screen_height: int) -> None:
        if not self._image:
            return

        if self.alpha < 255:
            self._image.set_alpha(self.alpha)

        draw_x = int(self.center_x - self.width / 2)
        draw_y = int(screen_height - (self.center_y + self.height / 2))

        surface.blit(self._image, (draw_x, draw_y))