from enum import Enum, auto


class GenericEvent(Enum):
    """
    A generic event type that can be used across different games to represent common events. Most events will recieve
    a snapshot of the game state as an argument to the event callback unless specified otherwise.
    """

    GAME_START = auto()
    """The game has started."""
    PHASE_CHANGE = auto()
    """Game has changed phase. The new phase and a snapshot of the game state are passed as a tuple argument to the event callback."""
    TURN_START = auto()
    """A new turn has started."""
    GAME_END = auto()
    """The game has ended. The payout is passed as an argument to the event callback."""
