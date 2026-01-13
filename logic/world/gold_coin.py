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
            value=5,
            scale=1.5
        )
        # Chance здесь 0.0, управляется в game_controller через unlock

    def land(self) -> None:
        # ВАЖНО: Сначала вызываем базовый land()
        # Он очистит список жертв, остановит монетку и запустит логику кубика (переворот)
        super().land()

        # Дополнительная логика для золота после super().land()
        # (например, если бы мы хотели добавить особые эффекты крита для золота)