from logic.world.coin import Coin
import random

class GoldCoin(Coin):
    def __init__(
        self,
        x: float,
        y: float,
        sprites: dict
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=5,         # Просто дорогая монета
            scale=1.5
        )
        # Критов больше нет

    # Метод land можно не переопределять, он будет использовать стандартный из Coin.py
    # (50% орел = 5 монет, 50% решка = 0)