from casino.player import Player
from utils.terminal import draw_bg, term


class Game:
    """
    A base class for all casino games, providing common functionality and structure.
    """

    def start(self):
        print(term.clear())
        draw_bg()

    def run(self):
        raise NotImplementedError("Subclasses must implement the run() method.")

    def end(self): ...

    def show_rules(self):
        raise NotImplementedError("Subclasses must implement the show_rules() method.")


class MultiplayerGame(Game):
    """
    A base class for multiplayer casino games, which can have multiple players and CPU opponents.
    """

    players: list[Player]
    cpu_players: list[Player]

    def __init__(self, name, cpu_players: int, *players: Player):
        """
        Initialize the multiplayer game with a name, a list of human players, and a specified number of CPU opponents.
        """
        super().__init__(name)
        self.players = players
        self.cpu_players = [Player(f"CPU {i+1}") for i in range(cpu_players)]

    def cpu_choice(self):
        """
        Simulate a CPU player's choice. This method should be overridden by subclasses to implement game-specific logic for CPU decisions.
        """
        raise NotImplementedError("Subclasses must implement the cpu_choice() method.")
