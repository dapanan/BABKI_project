from logic.world.coin import Coin

class BronzeCoin(Coin):
        def __init__(
            self,
            x: float,
            y: float,
            sprites: dict,
            scale: float = 0.8,
            scale_factor: float = 1.0  # <--- Добавили аргумент
        ) -> None:
            super().__init__(
                x=x,
                y=y,
                sprites=sprites,
                value=4463789067453564798,
                scale=scale,
                scale_factor=scale_factor  # <--- Передали в родительский класс
            )