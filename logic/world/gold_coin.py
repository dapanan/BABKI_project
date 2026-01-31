from logic.world.coin import Coin
import random


class GoldCoin(Coin):
    def __init__(
            self,
            x: float,
            y: float,
            sprites: dict,
            scale: float = 1.5,
            scale_factor: float = 1.0 # <--- Добавили аргумент
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=5,
            scale=scale,
            scale_factor=scale_factor # <--- Передали в родительский класс
        )
        # Chance здесь 0.0, управляется в game_controller через unlock

    def land(self) -> None:
        # ВАЖНО: Сначала вызываем базовый land()
        # Он очистит список жертв, остановит монетку и запустит логику кубика (переворот)
        super().land()

        # Дополнительная логика для золота после super().land()
        # (например, если бы мы хотели добавить особые эффекты крита для золота)