from abc import ABC, abstractmethod
from casino.games import Game


class Renderer(ABC):
    """
    A class responsible for rendering the game. This is just a default implementation,
    and specific games must override this with their own rendering logic.

    Any class inheriting from Renderer must subscribe to game events in the __init__ method and implement the render method to update the game display based on the current game state.
    """

    game: Game

    @abstractmethod
    def __init__(self, game: Game):
        """Initializes the renderer and subscribes to relevant game events."""
        self.game = game
