from enum import Enum
import random

class Suit(Enum):
    """
    The suit of a playing card, which can be Hearts, Diamonds, Clubs, or Spades.
    """
    HEARTS = '♥️'
    DIAMONDS = '♦️'
    CLUBS = '♣️'
    SPADES = '♠️'

class Rank(Enum):
    """
    The rank of a playing card, which can be a number (2-10) or a face card (Jack, Queen, King, Ace).
    """
    TWO = '2'
    THREE = '3'
    FOUR = '4'
    FIVE = '5'
    SIX = '6'
    SEVEN = '7'
    EIGHT = '8'
    NINE = '9'
    TEN = '10'
    JACK = 'J'
    QUEEN = 'Q'
    KING = 'K'
    ACE = 'A'

class Card:
    """
    A playing card with a suit and rank.
    """
    suit: Suit
    rank: Rank

    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} {self.suit}"

    def __repr__(self):
        return f"Card('{self.suit}', '{self.rank}')"


class Deck:
    """
    A standard deck of 52 playing cards, consisting of 4 suits (Hearts, Diamonds, Clubs, Spades) and 13 ranks (2-10, Jack, Queen, King, Ace).
    """
    cards: list[Card]

    def __init__(self, shuffle: bool = True):
        """
        intialize the deck with 52 cards and optionally shuffle it.
        """
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]

        if shuffle:
            self.shuffle()

    def remaining_cards(self):
        """Return the number of remaining cards in the deck."""
        return len(self.cards)

    def shuffle(self):
        """Shuffle the deck of cards."""
        random.shuffle(self.cards)

    def deal(self, num_cards: int = 1):
        """
        Deal a specified number of cards from the top of the deck.

        Raises `ValueError` if there are not enough cards in the deck to deal.
        """
        if num_cards > len(self.cards):
            raise ValueError("Not enough cards in the deck to deal.")

        dealt_cards = self.cards[:num_cards]
        self.cards = self.cards[num_cards:]

        return dealt_cards
