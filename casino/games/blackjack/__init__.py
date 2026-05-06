from enum import Enum


class BlackjackEvent(Enum):
    """
    Enum to represent the different events that can occur during a Blackjack game,
    which can be used to trigger specific actions or updates in the game state or user interface.
    """

    PLAYER_HIT = 0
    """Event triggered when the player chooses to hit (take another card). The callback will include the new card dealt to the player."""
    PLAYER_STAND = 1
    """Event triggered when the player chooses to stand (keep their current hand). The callback will include the player's final hand."""
    DEALER_HIT = 2
    """Event triggered when the dealer hits (takes another card). The callback will include the dealer's cards."""
    PLAYER_WINS = 3
    """Event triggered when the player wins the round. The callback will include the winner object, the payout amount, the player's hand and the dealer's hand."""
    DEALER_WINS = 4
    """Event triggered when the dealer wins the round. The callback will include the winner object, the player's hand and the dealer's hand."""
    TIE = 5
    """Event triggered when the round ends in a tie. The callback will include the player's hand and the dealer's hand."""
    PLAYER_BETS = 6
    """Event triggered when the player places a bet. The callback will include the bet amount."""


class BlackjackPhase(Enum):
    """Enum to represent the different phases of a Blackjack game, which can be used to manage game flow and logic."""

    WAITING_FOR_BET = 0
    """Phase where the game is waiting for the player to place their bet."""
    PLAYER_TURN = 1
    """Phase where the player is taking their turn, deciding whether to hit or stand."""
    DEALER_TURN = 2
    """Phase where the dealer is taking their turn, following the standard Blackjack rules for hitting and standing."""
    ROUND_END = 3
    """Phase where the round has ended, and the game is determining the outcome and updating player balances accordingly."""
