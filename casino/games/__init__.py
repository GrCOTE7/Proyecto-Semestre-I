from casino.player import Player
from utils.terminal import draw_bg, term, BG_COLOR
from dataclasses import dataclass


@dataclass
class Area:
    """
    Represents a rectangular area on the terminal screen, defined by its top-left corner (x, y) and its width and height.
    """

    x: int
    y: int
    width: int
    height: int


class Game:
    """
    A base class for all casino games, providing common functionality and structure.
    """

    header_area: Area
    game_area: Area
    hint_area: Area

    def __init__(self, name):
        self.name = name
        self.header_area = Area(0, 0, term.width, 3)
        self.game_area = Area(0, 3, term.width, term.height - 6)
        self.hint_area = Area(0, term.height - 3, term.width, 3)

    def start(self):
        print(term.clear())
        draw_bg()

        with term.location(self.header_area.x, self.header_area.y):
            print(term.move_down(self.header_area.height - 1), end="")
            print(
                BG_COLOR
                + term.center(
                    term.bold(self.name),
                    self.header_area.width,
                    fillchar=BG_COLOR + "-",
                ),
                end="",
            )

    def run(self):
        raise NotImplementedError("Subclasses must implement the run() method.")

    def end(self): ...

    def show_rules(self):
        raise NotImplementedError("Subclasses must implement the show_rules() method.")

    def show_hint(self, prompt: str):
        with term.location(self.hint_area.x, self.hint_area.y):
            print(BG_COLOR + "-" * self.hint_area.width, end="")
            print(BG_COLOR + term.center(prompt, self.hint_area.width), end="")

    @staticmethod
    def clear_area(area: Area):
        """Clears the specified area on the terminal screen by printing spaces over it."""
        with term.location(area.x, area.y):
            for _ in range(area.height):
                print(BG_COLOR + " " * area.width, end="")
                print(term.move_down, end="")


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
        self.players = [*players]
        self.cpu_players = [Player(f"CPU {i+1}") for i in range(cpu_players)]

    def cpu_choice(self):
        """
        Simulate a CPU player's choice. This method should be overridden by subclasses to implement game-specific logic for CPU decisions.
        """
        raise NotImplementedError("Subclasses must implement the cpu_choice() method.")
