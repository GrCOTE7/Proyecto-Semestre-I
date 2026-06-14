from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Any

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from casino.games import Game


class Command(ABC):
    """The Command interface declares a method for executing a command."""

    game: Game
    """
    Reference to the game instance that the command will operate on. 
    This allows the command to interact with the game state and perform actions based on the current game context.
    """
    kwargs: dict
    """
    A dictionary to hold any additional parameters needed for the command execution. 
    This allows for flexibility in passing various arguments to the execute method without changing the method signature.
    """

    def __init__(self, game: Game, **kwargs):
        self.game = game
        self.kwargs = kwargs

    @abstractmethod
    def execute(self):
        pass

    def undo(self, *args, **kwargs):
        pass


@dataclass
class CommandParameter:
    """
    Defines a parameter required for executing a command,
    including its kwargs name, the prompt text for user input, and a parser function to convert the input string into the appropriate type.

    # Example:
    ```
    CommandParameter(
    name="amount",
    prompt_text="How much would you like to raise?",
    parser=int
    )
    ```
    """

    name: str
    """The kwarg name that will be used in the Command class (e.g., 'amount')"""
    prompt_text: str
    """What the UI should ask (e.g., 'How much? ')"""
    parser: Callable
    """A function to convert the string (e.g., int)"""
    value: Any = None
    """The resulting value after parsing the user input."""

    def set_value(self, user_input: str):
        """Parses the user input and sets the value."""
        self.value = self.parser(user_input)


@dataclass
class CommandSchema:
    """
    Defines the schema for a command, including its display name, the class to instantiate, and any parameters required for execution.

    # Example:

    ```
    CommandSchema(
        display_name="Raise Bet",
        command_class=RaiseCommand,
        parameters=[
            CommandParameter(
                name="amount",
                prompt_text="How much would you like to raise?",
                parser=int
            )
        ]
    )
    ```
    """

    display_name: str
    """What shows in the menu (e.g., 'Raise Bet')"""
    command_class: type[Command]
    """The actual class to instantiate (e.g., RaiseCommand)"""
    parameters: list[CommandParameter] = field(default_factory=list)
    """
    A list of CommandParameter objects that define the parameters required for executing the command. 
    This allows the UI to dynamically prompt the user for the necessary inputs based on the command's requirements.
    """
