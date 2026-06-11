from enum import Enum, auto

class RouletteEvents(Enum):
    """An enumeration of events that can occur in the Roulette game, used to notify listeners of changes in the game state."""

    PLAYER_TURN_START = auto()
    """The player's turn has started, allowing them to place bets."""
    INVALID_BET = auto()
    """An invalid bet was attempted, such as placing a bet with insufficient funds or on an invalid bet type."""
    BET_PLACED = auto()
    """A bet has been placed by the player."""
    BET_REMOVED = auto()
    """A bet has been removed by the player."""
    SPIN_STARTED = auto()
    """The roulette wheel has started spinning."""
    SPIN_RESULT = auto()
    """The result of the spin has been determined, including the winning number and any payouts."""
