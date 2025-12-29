from logic.world.coin import Coin
import random


class GoldCoin(Coin):
    def __init__(
            self,
            x: float,
            y: float,
            sprites: dict,
            crit_chance: float = 0.0
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=5,
            scale=1.2
        )
        self.crit_chance = crit_chance
        self.is_crit = False

    def land(self) -> None:
        # Сначала определяем результат
        is_heads = random.random() < 0.5
        val = 0

        if is_heads:
            if random.random() < self.crit_chance:
                val = self.value * 10
                self.is_crit = True
            else:
                val = self.value
                self.is_crit = False
        else:
            self.is_crit = False

        self.last_outcome_value = val

        # ВАЖНО: Теперь вызываем логику остановки и смены текстуры из родительского класса
        # Но нам нужно изменить текстуру в зависимости от is_heads, поэтому дублируем логику остановки:

        self.is_moving = False  # Останавливаем монетку (ИСПРАВЛЕНИЕ ВЫЛЕТА)
        self.vx = 0
        self.vy = 0
        self.anim = []

        if is_heads:
            self.sprite.texture = self.sprites["heads"]
        else:
            self.sprite.texture = self.sprites["tails"]

        # Не вызываем super().land(), чтобы не пересчитывать heads/tails дважды,
        # но мы скопировали оттуда важные строки (is_moving = False и т.д.)