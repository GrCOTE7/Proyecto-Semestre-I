from enum import Enum


class GenericEvent(Enum):
    """A generic event type that can be used across different games to represent common events."""

    PHASE_CHANGE = 0
    """Game has changed phase. The new phase is passed as an argument to the event callback."""
    GAME_END = 1
    """The game has ended."""
