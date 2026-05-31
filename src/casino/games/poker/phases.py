from enum import Enum, auto


class PokerPhase(Enum):
    DEALING_CARDS = auto()
    """Phase where players are dealt their hole cards."""
    CHOOSING_DEALER = auto()
    """Phase where the dealer is chosen."""
    PRE_FLOP = auto()
    """Phase for the pre-flop betting round."""
    FLOP = auto()
    """Phase for the flop betting round."""
    TURN = auto()
    """Phase for the turn betting round."""
    RIVER = auto()
    """Phase for the river betting round."""
    SHOWDOWN = auto()
    """Phase where remaining players reveal their hands and the winner is determined."""
