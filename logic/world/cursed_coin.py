from logic.world.coin import Coin
import random
import arcade


class CursedCoin(Coin):
    def __init__(self, x: float, y: float, sprites: dict, scale: float = 1.5, scale_factor: float = 1.0) -> None:
        super().__init__(x, y, sprites, value=0, scale=scale, scale_factor=scale_factor)

        self.bankruptcy_triggered = False
        self.sound_played = False
        self.is_used = False
        self.lifetime = None
        self.particle_timer = 0.0
    def hit(self, dx: int, dy: int) -> None:
        if self.is_used:
            return
        super().hit(dx, dy)

    def land(self) -> None:
        if self.is_used:
            return

        is_heads = random.random() < 0.5

        if is_heads:
            # === УСПЕХ (Орел) ===
            # 2 означает "Успех: x100"
            self.last_outcome_value = 2
            self.sprite.texture = self.sprites.get("heads")

            self.lifetime = 2.0 # Даем время полюбоваться х100
            self.bankruptcy_triggered = False

        else:
            # === ПРОВАЛ (Решка) ===
            self.last_outcome_value = 0
            self.sprite.texture = self.sprites.get("tails")

            # Взрывается и забирает баланс
            self.bankruptcy_triggered = True
            self.lifetime = 0.5 # Чуть дольше, чтобы увидели взрыв

        self.is_moving = False
        self.anim = []
        self.landed = True
        self.is_used = True