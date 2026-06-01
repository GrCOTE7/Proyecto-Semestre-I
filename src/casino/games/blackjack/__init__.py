from enum import Enum, auto


class BlackjackEvent(Enum):
    """
    Enum to represent the different events that can occur during a Blackjack game,
    which can be used to trigger specific actions or updates in the game state or user interface.
    Most events will receive a snapshot of the game state as an argument to the event callback unless specified otherwise.
    """

    PLAYER_HIT = auto()
    """Event triggered when the player chooses to hit (take another card)."""
    PLAYER_STAND = auto()
    """Event triggered when the player chooses to stand (keep their current hand)."""
    DEALER_HIT = auto()
    """Event triggered when the dealer hits (takes another card)."""
    PLAYER_WINS = auto()
    """Event triggered when the player wins the round."""
    DEALER_WINS = auto()
    """Event triggered when the dealer wins the round."""
    TIE = auto()
    """Event triggered when the round ends in a tie."""


class BlackjackPhase(Enum):
    """Enum to represent the different phases of a Blackjack game, which can be used to manage game flow and logic."""

    PLAYER_TURN = auto()
    """Phase where the player is taking their turn, deciding whether to hit or stand."""
    DEALER_TURN = auto()
    """Phase where the dealer is taking their turn, following the standard Blackjack rules for hitting and standing."""
    ROUND_END = auto()
    """Phase where the round has ended, and the game is determining the outcome and updating player balances accordingly."""
