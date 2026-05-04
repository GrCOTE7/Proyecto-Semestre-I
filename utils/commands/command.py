from abc import ABC, abstractmethod
from casino.games import Game


class Command(ABC):
    """The Command interface declares a method for executing a command."""

    def __init__(self, game: Game, description: str = ""):
        self.game = game
        self.description = description

    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    def undo(self, *args, **kwargs):
        pass
