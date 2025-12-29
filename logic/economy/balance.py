class Balance:
    def __init__(self) -> None:
        self._value = 0

    def add(self, amount: int) -> None:
        self._value += max(0, amount)

    def can_spend(self, amount: int) -> bool:
        return self._value >= amount

    def spend(self, amount: int) -> bool:
        if amount <= 0:
            return True
        if not self.can_spend(amount):
            return False
        self._value -= amount
        return True

    def get(self) -> int:
        return self._value
