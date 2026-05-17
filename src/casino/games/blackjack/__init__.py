from enum import Enum, auto


class BlackjackEvent(Enum):
    """
    Enum to represent the different events that can occur during a Blackjack game,
    which can be used to trigger specific actions or updates in the game state or user interface.
    """

    PLAYER_HIT = auto()
    """Event triggered when the player chooses to hit (take another card). The callback will include the game snapshot."""
    PLAYER_STAND = auto()
    """Event triggered when the player chooses to stand (keep their current hand). The callback will include the game snapshot."""
    DEALER_HIT = auto()
    """Event triggered when the dealer hits (takes another card). The callback will include the game snapshot."""
    PLAYER_WINS = auto()
    """Event triggered when the player wins the round. The callback will include the game snapshot."""
    DEALER_WINS = auto()
    """Event triggered when the dealer wins the round. The callback will include the game snapshot."""
    TIE = auto()
    """Event triggered when the round ends in a tie. The callback will include the game snapshot."""


class BlackjackPhase(Enum):
    """Enum to represent the different phases of a Blackjack game, which can be used to manage game flow and logic."""

    PLAYER_TURN = auto()
    """Phase where the player is taking their turn, deciding whether to hit or stand."""
    DEALER_TURN = auto()
    """Phase where the dealer is taking their turn, following the standard Blackjack rules for hitting and standing."""
    ROUND_END = auto()
    """Phase where the round has ended, and the game is determining the outcome and updating player balances accordingly."""
