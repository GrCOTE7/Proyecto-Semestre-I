from . import BlackjackPhase
from casino.games import Game
from casino.player import Player
from utils.cards import Deck, Card, Rank
from dataclasses import dataclass
from utils.commands.game_manager import GameManager
from .commands import HitCommand, StandCommand
from casino.games.generic_events import GenericEvent
from . import BlackjackEvent


class BlackjackManager(GameManager):
    commands: dict[str, HitCommand | StandCommand]

    def __init__(self, game: Blackjack):
        super().__init__(game)
        # Register specific Blackjack commands
        self.register_command("H", HitCommand(game))
        self.register_command("S", StandCommand(game))


@dataclass
class BlackJackPlayer(Player):
    player: Player
    cards: list[Card]

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
    deck: Deck
    dealer = BlackJackPlayer
    player: BlackJackPlayer
    bet: float
    game_phase: BlackjackPhase

    def __init__(self, player: Player):
        super().__init__("Blackjack")
        self.dealer = BlackJackPlayer(Player("Dealer"), [])
        self.player = BlackJackPlayer(player, [])
        self.deck = Deck(True)
        self.game_phase = BlackjackPhase.WAITING_FOR_BET

    @property
    def active_player(self) -> BlackJackPlayer:
        return (
            self.dealer
            if self.game_phase == BlackjackPhase.DEALER_TURN
            else self.player
        )

    def accept_bet(self, amount: float):
        """Accepts a bet from the player and transitions to the next phase."""
        self.active_player.player.withdraw(amount)
        self.bet = amount
        self.start()

    def start(self):
        # Give initial cards to player and dealer
        for _ in range(2):
            self.hit(self.player)
            self.notify(BlackjackEvent.PLAYER_HIT, self.player.cards[-1])

            self.hit(self.dealer)
            self.notify(BlackjackEvent.DEALER_HIT, self.dealer.cards[-1])

        # If the dealer has a blackjack, the round ends immediately
        if self.dealer.is_blackjack:
            self.end_round()

        self.change_phase(BlackjackPhase.PLAYER_TURN)

    def hit(self, player: BlackJackPlayer):
        """Deals a new card to the specified player."""
        new_card = self.deck.deal(1)[0]
        player.cards.append(new_card)

        self.notify(
            (
                BlackjackEvent.PLAYER_HIT
                if self.player == self.active_player
                else BlackjackEvent.DEALER_HIT
            ),
            new_card,
        )

        if player.hand_value > 21:
            self.end_round()

    def dealer_play(self):
        self.change_phase(BlackjackPhase.DEALER_TURN)

        while self.dealer.hand_value < 17:
            self.hit(self.dealer)

        # Finish the round after the dealer has completed their turn
        self.end_round()

    def end_round(self):
        self.change_phase(BlackjackPhase.ROUND_END)

        if self.player.has_busted or (
            not self.dealer.has_busted
            and self.dealer.hand_value > self.player.hand_value
        ):
            self.notify(
                BlackjackEvent.DEALER_WINS, self.player.cards, self.dealer.cards
            )
        elif self.dealer.has_busted or self.player.hand_value > self.dealer.hand_value:

            # Player wins, so we pay out the bet (return the original bet plus winnings)
            if self.player.is_blackjack:
                self.player.player.deposit(self.bet * 2.5)  # Blackjack pays 3:2
            else:
                self.player.player.deposit(self.bet * 2)

            self.notify(
                BlackjackEvent.PLAYER_WINS, self.player.cards, self.dealer.cards
            )
        elif self.player.hand_value == self.dealer.hand_value:
            # It's a tie, so we return the player's original bet
            self.player.player.deposit(self.bet)
            self.notify(BlackjackEvent.TIE, self.player.cards, self.dealer.cards)

        self.notify(GenericEvent.GAME_END)
