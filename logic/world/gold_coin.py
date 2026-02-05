from logic.world.coin import Coin
import random


class GoldCoin(Coin):
    def __init__(
            self,
            x: float,
            y: float,
            sprites: dict,
            value: int = 100,  # <--- ДОБАВЛЯЕМ АРГУМЕНТ value
            scale: float = 1.5,
            scale_factor: float = 1.0
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=value,  # <--- ПЕРЕДАЕМ value ВМЕСТО 100
            scale=scale,
            scale_factor=scale_factor
        )

    def land(self) -> None:
        super().land()