class Player:
    """
    A class representing a player in a casino game.
    """

    name: str
    money: float

    def __init__(self, name: str, money: float = 1000):
        self.name = name
        self.money = money

    def deposit(self, amount: float):
        """Add money to the player's balance."""
        self.money += amount

    def withdraw(self, amount: float):
        """
        Remove money from the player's balance.

        Raises:
            TypeError: If the amount is negative.
            ValueError: If the amount exceeds the player's available money.
        """

        if amount < 0:
            raise TypeError("Amount must be positive")
        if amount > self.money:
            raise ValueError("Insufficient funds")
        self.money -= amount
