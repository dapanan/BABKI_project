from logic.world.coin import Coin
import random


class SilverCoin(Coin):
    def __init__(
            self,
            x: float,
            y: float,
            sprites: dict,
            crit_chance: float = 0.0  # Этот параметр игнорируем для теста
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=2,
            scale=1.1
        )

        # ЗАГЛУШКА: 100% шанс крита для теста эффектов
        self.crit_chance = 1.0

        self.is_crit = False

    def land(self) -> None:
        is_heads = random.random() < 0.5
        val = 0

        if is_heads:
            # Так как crit_chance = 1.0, крит будет всегда при орле
            if random.random() < self.crit_chance:
                val = self.value * 10
                self.is_crit = True
            else:
                val = self.value
                self.is_crit = False
        else:
            self.is_crit = False

        self.last_outcome_value = val

        self.is_moving = False
        self.vx = 0
        self.vy = 0
        self.anim = []

        if is_heads:
            self.sprite.texture = self.sprites["heads"]
        else:
            self.sprite.texture = self.sprites["tails"]