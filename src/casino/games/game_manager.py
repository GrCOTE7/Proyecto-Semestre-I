from abc import ABC
from utils.commands.command import Command
from casino.games import Game
from casino.player import PlayerController, CPUController
from utils.commands.command_manager import CommandManager
from utils.event_listener import EventBus


class GameManager(ABC):
    """The Base Template for all games."""

    def __init__(self, game: Game):
        self.game = game
        self.event_bus = EventBus()
        self.command_manager = CommandManager(game)
        self.players: list[PlayerController] = []
