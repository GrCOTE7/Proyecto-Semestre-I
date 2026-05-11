from casino.games import Game
from utils.terminal import term, BG_COLOR
from utils.cards import Deck, Card, Rank
from casino.player import PlayerController, CPUController
from dataclasses import dataclass
import time
import random
from itertools import combinations
from enum import Enum
from collections import Counter
from casino.games.game_manager import GameManager
from .phases import PokerPhase
from .events import PokerEvent
from . import commands
from utils.commands.command import Command
from uuid import UUID


@dataclass
class PokerPlayer:
    player: PlayerController
    cards: list[Card]


class HandRank(Enum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


class CardRank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class PokerManager(GameManager):
    def __init__(self, game: Poker):
        super().__init__("Poker")
        self.game = game


class Poker(Game):
    # The deck used in the game
    deck: Deck

    # The community cards on the table (the 5 cards that all players can use to make their hand)
    community_cards: list[Card]

    # All the cpus in the game
    cpus: list[PokerPlayer]
    # The human player in the game
    player: PokerPlayer

    # List of all active players in the current hand (those who haven't folded)
    active_players: list[PokerPlayer]

    # The index of the player whose turn it is currently
    # Using an index instead of a direct reference to the player object to make it easier to cycle through players in turn order.
    current_player_idx: int
    # The index of the dealer (the player who is currently the dealer, which rotates each hand)
    # Using an index instead of a direct reference to the player object to make it easier
    # to rotate the dealer each hand and to determine who pays the small and big blinds based on the dealer's position.
    dealer_idx: int

    # The big blind amount (for simplicity, we set it as a percentage of the player's money)
    big_blind: float
    # The total amount of money in the pot for the current hand
    pot: float

    # The current bet amount that players need to call to stay in the hand (starts at big blind and increases with raises)
    current_bet: float

    # A player must raise by at least the amount of the previous bet or raise in that same round.
    last_raise: float

    # The different phases of a poker hand, which determine the flow of the game and when community cards are revealed.
    # The game starts in the PRE_FLOP phase, then moves to FLOP, TURN, and RIVER as community cards
    # are revealed and betting rounds are completed.
    phases: list[PokerPhase] = [
        PokerPhase.PRE_FLOP,
        PokerPhase.FLOP,
        PokerPhase.TURN,
        PokerPhase.RIVER,
    ]
    current_phase_idx: int

    # A counter to track how many players have called in the current betting round, used to determine when to move to the next phase.
    call_count: int

    def __init__(self, player: PlayerController):
        super().__init__("Poker")

        self.player = PokerPlayer(player, [])
        self.cpus = [
            PokerPlayer(CPUController(f"CPU {i+1}", self), []) for i in range(5)
        ]
        self.active_players = self.all_players

        self.deck = Deck()
        self.community_cards = []

        self.big_blind = player.money * 0.05
        self.pot = 0

        self.current_bet = self.big_blind
        self.last_raise = self.big_blind

        self.current_phase_idx = 0
        self.call_count = 0

    @property
    def all_players(self):
        """Returns a list of all players in the game, with the human player first followed by the CPUs."""
        return [self.player] + self.cpus

    @property
    def dealer(self) -> PokerPlayer:
        """Returns the current dealer."""
        return self.all_players[self.dealer_idx]

    @property
    def active_player(self) -> PokerPlayer:
        """Returns the current player."""
        return self.all_players[self.current_player_idx]

    @property
    def current_phase(self) -> PokerPhase:
        """Returns the current phase of the game."""
        return self.phases[self.current_phase_idx]

    @property
    def min_raise(self) -> float:
        """Returns the minimum raise amount based on the last raise."""
        return self.last_raise

    def get_player_by_uuid(self, player_id: UUID) -> PokerPlayer | None:
        """Returns the PokerPlayer object corresponding to the given player UUID, or None if not found."""
        for player in self.all_players:
            if player.player.id == player_id:
                return player
        return None

    def start(self):
        # Reset all game state for the new hand
        self.deck = Deck()
        self.community_cards = []
        self.active_players = self.all_players
        self.pot = 0
        self.last_raise = 0
        self.big_blind = self.player.player.money * 0.05
        self.current_bet = self.big_blind
        self.current_phase_idx = 0
        self.call_count = 0

        self.change_phase(PokerPhase.CHOOSING_DEALER)
        self.choose_dealer()
        self.change_phase(PokerPhase.DEALING_CARDS)
        self.deal_cards()
        self.pay_blinds()
        self.change_phase(PokerPhase.PRE_FLOP)

    def end(self):
        with term.cbreak():
            while True:
                key = term.inkey().lower()
                if key == "n":
                    self.__init__(
                        self.player.player
                    )  # Reset the game with the same player

                    self.dealer_idx = (self.dealer_idx + 1) % len(
                        self.all_players
                    )  # Rotate dealer for next hand
                    self.run()
                    break
                elif key == "q":
                    self.show_hint("Thanks for playing! Press any key to exit.")
                    term.inkey()
                    break

    def choose_dealer(self):
        """Randomly selects a dealer from all players (including the human player)."""

        self.change_phase(PokerPhase.CHOOSING_DEALER)
        self.dealer_idx = random.randint(0, len(self.all_players) - 1)
        self.current_player_idx = (self.dealer_idx + 3) % len(
            self.all_players
        )  # The player to the left of the big blind starts first, which is three positions to the left of the dealer.

        self.notify(PokerEvent.CHOOSE_DEALER)

    def deal_cards(self):
        """Deals 2 cards to each player from the deck."""

        self.change_phase(PokerPhase.DEALING_CARDS)

        for player in self.all_players:
            player.cards = self.deck.deal(2)

        self.notify(PokerEvent.DEAL_CARDS)

    def pay_blinds(self):
        """Handles the payment of the small and big blinds at the start of each hand."""
        small_blind_idx = (self.dealer_idx + 1) % len(self.all_players)
        big_blind_idx = (self.dealer_idx + 2) % len(self.all_players)

        small_blind_amount = self.big_blind / 2
        big_blind_amount = self.big_blind

        # Small blind payment
        self.all_players[small_blind_idx].player.money -= small_blind_amount
        self.pot += small_blind_amount

        # Big blind payment
        self.all_players[big_blind_idx].player.money -= big_blind_amount
        self.pot += big_blind_amount

        self.notify(PokerEvent.PAID_BLIND)

    def advance_turn(self):
        """Advances the turn to the next player."""
        if (
            self.call_count >= len(self.active_players)
            or all(player.player.money == 0 for player in self.active_players)
            or len(self.active_players) == 1
        ):
            # Move to the next stage of the hand after everyone has called, everyone is all-in, or only one player remains
            self.next_phase()

        self.current_player_idx = (self.current_player_idx + 1) % len(self.all_players)
        self.notify(PokerEvent.CHANGE_PLAYER_TURN)

    def next_phase(self):
        """Advances the game to the next phase (e.g., from pre-flop to flop, etc.) and resets the current bet and call count for the new betting round."""
        # End the hand if we're on the river, or if only one player remains, or if all remaining players are all-in
        if (
            self.current_phase == PokerPhase.RIVER
            or len(self.active_players) == 1
            or all(player.player.money == 0 for player in self.active_players)
        ):
            self.end_hand()
        else:
            self.current_phase_idx += 1
            self.call_count = 0

            # Deal the corresponding community cards of each phase
            match self.current_phase:
                case PokerPhase.FLOP:
                    self.community_cards += self.deck.deal(3)
                case PokerPhase.TURN | PokerPhase.RIVER:
                    self.community_cards += self.deck.deal(1)

        self.change_phase(self.current_phase)

    def player_call(self, player: PokerPlayer):
        """Handles a player calling the current bet, including updating the pot and the player's money."""
        payment = min(self.current_bet, player.player.money)

        self.pot += payment
        player.player.money -= payment

        # Only count as a call if the player is actually calling the current bet,
        # and not just going all-in with a smaller amount
        if payment == self.current_bet:
            self.call_count += 1
            self.notify(PokerEvent.PLAYER_CALL)
        else:
            self.notify(PokerEvent.PLAYER_ALL_IN)

    def request_player_raise(self):
        """Prompts the player to input a raise amount, ensuring that it meets the minimum raise requirement and is a valid number."""
        self.notify(PokerEvent.PLAYER_RAISE)

    def player_raise(self, player: PokerPlayer, new_bet: float):
        """
        Raises the bet to new_bet
        """

        # 1. Calculate how much the player must pay
        # (new_bet is the total)
        amount_to_add = new_bet - player.player.money

        # 2. Does the player have enough money?
        if amount_to_add > player.player.money:
            raise ValueError("No tienes suficientes fichas para esa apuesta.")

        # 3. Requerimiento de Monto Mínimo:
        # La subida (raise) es la parte que excede a la apuesta actual (current_bet).
        raise_amount = new_bet - self.current_bet

        # Si no es un All-in, debe cumplir con el raise mínimo
        is_all_in = amount_to_add == player.stack

        if not is_all_in:
            if new_bet < self.current_bet + self.min_raise:
                raise ValueError(
                    f"La subida mínima es a {self.current_bet + self.min_raise}"
                )

        # 4. Ejecución de la jugada
        player.stack -= amount_to_add
        player.current_contribution = new_bet
        self.pot += amount_to_add

        # Actualizar la apuesta actual de la mesa y el nuevo raise mínimo
        # (El nuevo min_raise es la diferencia de esta subida)
        if raise_amount > self.min_raise:
            self.min_raise = raise_amount

        self.current_bet = new_bet

    def raise_bet(self, new_bet: float):
        """
        Raises the game's bet to the new bet amount, and updates the last raise amount accordingly.
        This method should be called whenever a player raises, to ensure that the minimum raise amount is correctly calculated for
        subsequent raises.
        """
        self.last_raise = new_bet - self.current_bet
        self.current_bet = new_bet

    def player_fold(self, player: PokerPlayer):
        """Handles a player folding, which removes them from the active players in the current hand."""
        self.active_players.remove(player)
        self.notify(PokerEvent.PLAYER_FOLD)

    def end_hand(self):
        """Handles the end of a hand, including determining the winner and distributing the pot."""
        # This method will be called when the hand is over (e.g., after the river betting round is complete, or if only one player remains).
        # It should evaluate the hands of all active players, determine the winner(s), and distribute the pot accordingly.
        pass

    @staticmethod
    def evaluate_hand(hand: list[Card]) -> tuple[HandRank, list[CardRank]]:
        """
        Evaluates a 5-card poker hand and returns a tuple containing the hand rank (e.g., pair, flush, straight)
        and a list of card ranks for tie-breaking purposes.
        The returned hand is comparable, meaning that a higher hand rank will always beat a lower one,
        and if two hands have the same rank, the tie-breaker list can be compared in order to determine the winner
        (e.g., for two pairs, the tie-breaker list would contain the ranks of the pairs and then the kicker).
        """
        # Sort ranks in descending order for easier evaluation of straights and high cards, and extract suits
        ranks = sorted([CardRank[c.rank.name] for c in hand], reverse=True)
        # The suits of all cards in the hand, used to check for flushes
        suits = [c.suit for c in hand]

        # Count the frequency of each rank in the hand, which is essential for identifying pairs, three of a kind, and four of a kind.
        counts = Counter(ranks)

        # Build a normalized 5-card comparison vector where duplicated ranks come first.
        # Examples:
        # - Pair: [pair, pair, kicker1, kicker2, kicker3]
        # - Two pair: [high_pair, high_pair, low_pair, low_pair, kicker]
        # - Trips: [trips, trips, trips, kicker1, kicker2]
        grouped_ranks = sorted(
            counts.items(), key=lambda item: (item[1], item[0]), reverse=True
        )
        score_sort = [rank for rank, freq in grouped_ranks for _ in range(freq)]

        is_flush = len(set(suits)) == 1
        is_straight = len(set(ranks)) == 5 and (max(ranks) - min(ranks) == 4)

        # Wheel Straight (A-5)
        if set(ranks) == {
            CardRank.ACE,
            CardRank.TWO,
            CardRank.THREE,
            CardRank.FOUR,
            CardRank.FIVE,
        }:
            is_straight = True
            score_sort = [
                CardRank.FIVE,
                CardRank.FOUR,
                CardRank.THREE,
                CardRank.TWO,
                CardRank.ACE,
            ]  # Ace is low in this straight

        # Return (HandRank, Tie-breaker-list)
        if is_straight and is_flush:
            return (
                (
                    HandRank.ROYAL_FLUSH
                    if score_sort[0] == CardRank.ACE
                    else HandRank.STRAIGHT_FLUSH
                ),
                score_sort,
            )

        hand_type = HandRank.HIGH_CARD

        if 4 in counts.values():
            hand_type = HandRank.FOUR_OF_A_KIND
        elif 3 in counts.values() and 2 in counts.values():
            hand_type = HandRank.FULL_HOUSE
        elif is_flush:
            hand_type = HandRank.FLUSH
        elif is_straight:
            hand_type = HandRank.STRAIGHT
        elif 3 in counts.values():
            hand_type = HandRank.THREE_OF_A_KIND
        elif list(counts.values()).count(2) == 2:
            hand_type = HandRank.TWO_PAIR
        elif 2 in counts.values():
            hand_type = HandRank.PAIR

        return (hand_type, score_sort)

    @staticmethod
    def best_hand(
        player_cards: list[Card], community_cards: list[Card]
    ) -> tuple[HandRank, list[CardRank]]:
        """
        Returns the best 5-card hand that can be made from 2 player cards and 5 community cards.

        The returned tuple is:
        - hand_score: (HandRank, tie_breaker_vector i.e. best hand) as produced by evaluate_hand
        """
        if len(player_cards) != 2:
            raise ValueError("best_hand expects exactly 2 player cards")
        if len(community_cards) != 5:
            raise ValueError("best_hand expects exactly 5 community cards")

        seven_cards = player_cards + community_cards

        best_five: list[Card] | None = None
        best_score: tuple[HandRank, list[CardRank]] | None = None

        for five_cards_tuple in combinations(seven_cards, 5):
            five_cards = list(five_cards_tuple)
            score = Poker.evaluate_hand(five_cards)

            if best_score is None or score > best_score:
                best_score = score
                best_five = five_cards

        # Guaranteed by combinations(7, 5), kept explicit for type-safety.
        if best_five is None or best_score is None:
            raise ValueError("Could not evaluate best hand")

        return best_score
