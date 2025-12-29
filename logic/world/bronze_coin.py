from logic.world.coin import Coin

class BronzeCoin(Coin):
    def __init__(
        self,
        x: float,
        y: float,
        sprites: dict,
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=1000,
            scale=0.8
        )