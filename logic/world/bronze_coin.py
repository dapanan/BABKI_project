from logic.world.coin import Coin

class BronzeCoin(Coin):
    def __init__(
        self,
        x: float,
        y: float,
        sprites: dict,
        scale: float = 0.8  # <--- ДОБАВИТЬ ЭТО
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=4463789067453564798,
            scale=scale  # <--- ИЗМЕНИТЬ ЗДЕСЬ (было 0.8)
        )