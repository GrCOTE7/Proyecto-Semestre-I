from typing import Optional
from uuid import UUID

from utils.commands.command import CommandSchema
from utils.event_listener import EventBus

from . import BlackjackPhase
from casino.games import Game
from casino.player import PlayerBuyIn, PlayerController
from utils.cards import CardView, Deck, Card, Rank
from dataclasses import dataclass, field
from casino.games.game_manager import GameManager
from .commands import HitCommand, StandCommand
from casino.games.generic_events import GenericEvent
from . import BlackjackEvent
from casino.games import Snapshot

from . import commands


@dataclass(frozen=True)
class BlackjackSnapshot(Snapshot):
    """
    A snapshot of the current state of the Blackjack game, used for rendering and game logic.
    It includes information about the player's hand, the dealer's hand, the current bet, and the game phase.
    """

    player_cards: list[CardView]
    """A list of CardView objects representing the player's current hand of cards. This can be used to display the player's hand in the UI."""
    dealer_cards: list[CardView]
    """A list of CardView objects representing the dealer's current hand of cards. This can be used to display the dealer's hand in the UI."""
    bet: float
    """The current bet amount placed by the player. This can be used to display the bet in the UI and calculate payouts."""
    game_phase: BlackjackPhase
    """
    The current phase of the game (e.g., WAITING_FOR_BET, PLAYER_TURN, DEALER_TURN, ROUND_END). 
    This can be used to determine which actions are available to the player and how to render the game state.
    """
    available_commands: set[CommandSchema] = field(default_factory=set)
    """A set of CommandSchema objects representing the commands available to the player in the current game state."""
    payout: float = None
    """The amount won or lost (positive for win, negative for loss, zero for tie)"""


@dataclass
class BlackJackPlayer:
    """
    Represents a player in the Blackjack game, holding their hand of cards and providing
    methods to calculate hand value and check for blackjack or bust conditions.
    """

    player_id: UUID
    balance: int
    cards: list[Card] = field(default_factory=list)

    @property
    def hand_value(self) -> int:
        """Calculate the total value of the player's hand, accounting for Aces."""
        value = 0
        aces = 0

        for card in self.cards:
            if card.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
                value += 10
            elif card.rank == Rank.ACE:
                aces += 1
                value += 11
            else:
                value += int(card.rank.value)

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    @property
    def is_blackjack(self) -> bool:
        """Check if the player's hand is a blackjack (an Ace and a 10-value card)."""
        return len(self.cards) == 2 and self.hand_value == 21

    @property
    def has_busted(self) -> bool:
        """Check if the player's hand value exceeds 21 (busted)."""
        return self.hand_value > 21


class Blackjack(Game):
    """
    Represents the Blackjack game, managing the flow of the game and handling player actions.
        The game progresses through several phases:
        - WAITING_FOR_BET: The game is waiting for the player to place a bet.
        - PLAYER_TURN: The player can choose to hit or stand.
        - DEALER_TURN: The dealer plays according to standard Blackjack rules.
        - ROUND_END: The round has ended, and the outcome is determined.

        Events are emitted at key points in the game, such as when a player hits, when the dealer hits,
        and when the game ends, allowing for flexible rendering and interaction.
    """

    deck: Deck
    dealer: BlackJackPlayer
    player: BlackJackPlayer
    bet: float
    game_phase: BlackjackPhase

    def __init__(self, event_bus: EventBus, buyin: PlayerBuyIn):
        super().__init__(event_bus, buyin)
        self.dealer = BlackJackPlayer(None, 0, [])
        self.player = BlackJackPlayer(buyin.player_id, buyin.amount, [])
        self.deck = Deck(True)
        self.bet = buyin.amount
        self.game_phase = BlackjackPhase.PLAYER_TURN

    @property
    def active_player(self) -> Optional[UUID]:
        """
        Returns the ID of the currently active player. During the player's turn, it returns the player's ID.
        During the dealer's turn, it returns None since the dealer is not a player in the traditional sense and does not have a player ID.
        """
        return (
            None
            if self.game_phase == BlackjackPhase.DEALER_TURN
            else self.buy_in.player_id
        )

    def get_player_by_id(self, player_id: UUID) -> Optional[BlackJackPlayer]:
        """Returns the player object corresponding to the given player ID, or None if not found."""
        if self.player.player_id == player_id:
            return self.player
        return None

    def start(self):
        # Give initial cards to player and dealer
        for _ in range(2):
            self.hit(self.player)
            self.hit(self.dealer)

        # If the dealer has a blackjack, the round ends immediately
        if self.dealer.is_blackjack:
            self.end_round()

        self.event_bus.notify(GenericEvent.TURN_START, self.buy_in.player_id)
        self.change_phase(BlackjackPhase.PLAYER_TURN, self.get_snapshot())

    def hit(self, player: BlackJackPlayer):
        """Deals a new card to the specified player."""
        new_card = self.deck.deal(1)[0]
        player.cards.append(new_card)

        player_turn = self.player == player

        self.event_bus.notify(
            (BlackjackEvent.PLAYER_HIT if player_turn else BlackjackEvent.DEALER_HIT),
            self.get_snapshot(),
        )

        if player.hand_value > 21 or player.is_blackjack:
            self.end_round()
        else:
            self.change_phase(
                (
                    BlackjackPhase.PLAYER_TURN
                    if player_turn
                    else BlackjackPhase.DEALER_TURN
                ),
                self.get_snapshot(),
            )

    def dealer_play(self):
        self.change_phase(BlackjackPhase.DEALER_TURN, self.get_snapshot())

        while self.dealer.hand_value < 17:
            self.hit(self.dealer)

        # Finish the round after the dealer has completed their turn
        self.end_round()

    def end_round(self):
        self.change_phase(BlackjackPhase.ROUND_END, self.get_snapshot())

        payout = 0
        event = None

        if self.player.has_busted or (
            not self.dealer.has_busted
            and self.dealer.hand_value > self.player.hand_value
        ):
            event = BlackjackEvent.DEALER_WINS
            # Player loses, so we return a negative payout to indicate loss
            payout = -self.bet
        elif self.dealer.has_busted or self.player.hand_value > self.dealer.hand_value:
            event = BlackjackEvent.PLAYER_WINS

            # Player wins, so we pay out the bet (return the original bet plus winnings)
            if self.player.is_blackjack:
                payout = self.bet * 2.5  # Blackjack pays 3:2
            else:
                payout = self.bet * 2  # Regular win pays 1:1
        else:
            # It's a tie, so we return the player's original bet
            event = BlackjackEvent.TIE
            payout = self.bet

        final_snapshot = self.get_snapshot(True, payout=payout)

        self.event_bus.notify(event, final_snapshot)
        self.event_bus.notify(GenericEvent.GAME_END, payout)

    def get_available_commands(self) -> list[CommandSchema]:
        return [
            CommandSchema("Hit", commands.HitCommand),
            CommandSchema("Stand", commands.StandCommand),
        ]

    def get_snapshot(
        self, show_dealer_cards: bool = False, **kwargs
    ) -> BlackjackSnapshot:
        """Returns a snapshot of the current game state for rendering and logic purposes."""
        return BlackjackSnapshot(
            (
                self.buy_in.player_id
                if self.game_phase == BlackjackPhase.PLAYER_TURN
                else None
            ),
            self.buy_in.name if self.buy_in.name else "Dealer",
            [CardView.from_card(card) for card in self.player.cards],
            [
                CardView.from_card(card, face_up=i == 0 or show_dealer_cards)
                for i, card in enumerate(self.dealer.cards)
            ],
            self.bet,
            self.game_phase,
            self.get_available_commands(),
            **kwargs
        )
