from enum import Enum, auto


class PokerEvent(Enum):
    """Enumeration of events that can occur during a poker game."""

    START_HAND = auto()
    """Event triggered at the start of a new hand."""
    END_HAND = auto()
    """Event triggered at the end of a hand."""
    CHOOSE_DEALER = auto()
    """Event triggered when the dealer is chosen. A snapshot of the game is passed as an argument."""
    DEAL_CARDS = auto()
    """Event triggered when cards are dealt."""
    PAID_BLIND = auto()
    """Event triggered when the small and big blind are paid. A snapshot of the game is passed as an argument."""
    CHANGE_PLAYER_TURN = auto()
    """Event triggered when the turn changes to the next player. A snapshot of the game is passed as an argument."""
    PLAYER_CALL = auto()
    """Event triggered when a player calls. A snapshot of the game is passed as an argument."""
    PLAYER_ALL_IN = auto()
    """Event triggered when a player goes all-in. A snapshot of the game is passed as an argument."""
    PLAYER_RAISE = auto()
    """Event triggered when a player raises. A snapshot of the game is passed as an argument."""
    PLAYER_FOLD = auto()
    """Event triggered when a player folds. A snapshot of the game is passed as an argument."""
    FLOP = auto()
    """Event triggered during the flop."""
    TURN = auto()
    """Event triggered during the turn."""
    RIVER = auto()
    """Event triggered during the river."""
    AVAILABLE_COMMANDS = auto()
    """Event triggered to notify the active player of their available commands. A snapshot of the game is passed as an argument."""
    HAND_OVER = auto()
    """Event triggered at the end of a hand, after winners have been determined and chips have been distributed. A snapshot of the game is passed as an argument"""
