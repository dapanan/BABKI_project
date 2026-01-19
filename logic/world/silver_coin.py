from logic.world.coin import Coin
import random


class SilverCoin(Coin):
    def __init__(
            self,
            x: float,
            y: float,
            sprites: dict,
            crit_chance: float = 0.0,
            scale: float = 1.1

    ) -> None:
        super().__init__(
            x=x,
            y=y,
            sprites=sprites,
            value=2,
            scale=scale
        )

        # Заглушка 100% для тестов
        self.crit_chance = 1.0

        self.is_crit = False

    def land(self) -> None:
        # Сначала считаем крит
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

        # Флаг остановки полета
        self.is_moving = False

        # Очищаем анимацию
        self.anim = []

        # УБРАНО self.vx = 0 и self.vy = 0 !!!

        # Меняем спрайт
        if is_heads:
            self.sprite.texture = self.sprites["heads"]
        else:
            self.sprite.texture = self.sprites["tails"]

        # --- ВОТ ЧТО ТЫ ЗАБЫЛ ДОБАВИТЬ ---
        self.landed = True
        # ---------------------------------