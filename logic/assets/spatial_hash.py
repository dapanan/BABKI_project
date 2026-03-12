class SpatialHash:
    def __init__(self, cell_size: int):
        self.cell_size = cell_size
        self.grid = {}

    def _get_key(self, position):
        x, y = position
        return (int(x / self.cell_size), int(y / self.cell_size))

    def add(self, sprite):
        key = self._get_key((sprite.center_x, sprite.center_y))
        if key not in self.grid:
            self.grid[key] = []
        self.grid[key].append(sprite)

    def get_sprites_near_point(self, position):
        """Возвращает список спрайтов в той же и соседних ячейках"""
        cx, cy = position
        cx_idx = int(cx / self.cell_size)
        cy_idx = int(cy / self.cell_size)

        nearby = []
        # Проверяем 3x3 область вокруг точки
        for x in range(cx_idx - 1, cx_idx + 2):
            for y in range(cy_idx - 1, cy_idx + 2):
                key = (x, y)
                if key in self.grid:
                    nearby.extend(self.grid[key])
        return nearby

    def clear(self):
        self.grid = {}