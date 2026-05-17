from enum import Enum, auto


class GenericEvent(Enum):
    """A generic event type that can be used across different games to represent common events."""

    GAME_START = auto()
    """The game has started."""
    PHASE_CHANGE = auto()
    """Game has changed phase. The new phase and a snapshot of the game state are passed as a tuple argument to the event callback."""
    TURN_START = auto()
    """A new turn has started. The active player's ID is passed as an argument to the event callback."""
    GAME_END = auto()
    """The game has ended. The callback recieves the final payout for the player as an argument."""
