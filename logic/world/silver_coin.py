from logic.world.coin import Coin
import random


class SilverCoin(Coin):
    def __init__(
            self,
            x: float,
            y: float,
            sprites: dict,
            crit_chance: float = 0.0,
            value: int = 10,  # <--- ДОБАВЛЯЕМ АРГУМЕНТ value
            scale: float = 1.1,
            scale_factor: float = 1.0
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=value,  # <--- ПЕРЕДАЕМ value ВМЕСТО 10
            scale=scale,
            scale_factor=scale_factor
        )
        self.crit_chance = 0.05
        self.is_crit = False

    def land(self) -> None:
        is_heads = random.random() < 0.5
        val = 0

        if is_heads:
            if random.random() < self.crit_chance:
                val = self.value * 5
                self.is_crit = True
            else:
                val = self.value
                self.is_crit = False
        else:
            self.is_crit = False

        self.last_outcome_value = val
        self.is_moving = False
        self.anim = []

        if is_heads:
            self.sprite.texture = self.sprites["heads"]
        else:
            self.sprite.texture = self.sprites["tails"]

        self.landed = True