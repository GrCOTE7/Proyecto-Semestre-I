from abc import ABC
from .command import Command
from casino.games import Game


class GameManager(ABC):
    """The Base Template for all games."""

    commands: dict[str, Command]

    def __init__(self, game: Game):
        self.game = game
        self.commands = {}

    def register_command(self, key: str, command: Command):
        """Registers a command with a specific enum value."""
        self.commands[key] = command

    def handle_input(self, user_input: str):
        """Handles user input by looking up the corresponding command and executing it."""
        cmd = self.commands.get(user_input.upper())
        if cmd:
            cmd.execute()

    def get_available_commands(self) -> dict[str, Command]:
        """Returns the available commands for the current game state."""
        return self.commands
