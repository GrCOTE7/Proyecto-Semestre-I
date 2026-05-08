from enum import Enum, auto


class PokerEvent(Enum):
    """Enumeration of events that can occur during a poker game."""

    START_HAND = auto()
    """Event triggered at the start of a new hand."""
    END_HAND = auto()
    """Event triggered at the end of a hand."""
    CHOOSE_DEALER = auto()
    """Event triggered when the dealer is chosen."""
    DEAL_CARDS = auto()
    """Event triggered when cards are dealt."""
    PAID_BLIND = auto()
    """Event triggered when the small and big blind are paid."""
    CHANGE_PLAYER_TURN = auto()
    """Event triggered when the turn changes to the next player."""
    PLAYER_CALL = auto()
    """Event triggered when a player calls."""
    PLAYER_ALL_IN = auto()
    """Event triggered when a player goes all-in."""
    PLAYER_RAISE = auto()
    """Event triggered when a player raises."""
    PLAYER_FOLD = auto()
    """Event triggered when a player folds."""
    FLOP = auto()
    """Event triggered during the flop."""
    TURN = auto()
    """Event triggered during the turn."""
    RIVER = auto()
    """Event triggered during the river."""
