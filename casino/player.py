class Player:
    """
    A class representing a player in a casino game.
    """

    name: str
    money: float

    def __init__(self, name, money=1000):
        self.name = name
        self.money = money
