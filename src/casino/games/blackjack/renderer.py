from utils.renderer import Renderer
from .blackjack import Blackjack
from . import BlackjackEvent, BlackjackPhase
from utils.cards import Card
from casino.games import GenericEvent
from .blackjack import BlackJackPlayer


class BlackjackTerminalRenderer(Renderer):
    game: Blackjack
    player_cards: list[Card]
    dealer_cards: list[Card]
    winner: BlackJackPlayer
    payout: float

    def __init__(self, game: Blackjack):
        super().__init__(game)

        game.subscribe(GenericEvent.PHASE_CHANGE, self.phase_change)
        game.subscribe(BlackjackEvent.PLAYER_HIT, self.render_hand)
        game.subscribe(BlackjackEvent.DEALER_HIT, self.render_dealer_hand)
        game.subscribe(GenericEvent.GAME_END, self.render_game_end)
        game.subscribe(BlackjackEvent.DEALER_WINS, self.dealer_wins)
        game.subscribe(BlackjackEvent.PLAYER_WINS, self.player_wins)

        self.game = game
        self.player_cards = []
        self.dealer_cards = []
        self.winner = None
        self.payout = 0

    def phase_change(self, new_phase):
        if new_phase == BlackjackPhase.WAITING_FOR_BET:
            while True:
                try:
                    bet_amount = float(input("Place your bet ($): "))
                    if bet_amount <= 0 or bet_amount > self.game.player.player.money:
                        print(
                            f"Bet must be between $0 and ${self.game.player.player.money:.2f}. Please try again."
                        )
                        continue
                    self.game.accept_bet(bet_amount)
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid number for your bet.")

    def render_hand(self, new_card: Card):
        self.player_cards.append(new_card)
        print(
            f"Player Hit. New hand: {', '.join(str(card) for card in self.player_cards)}"
        )

    def render_dealer_hand(self, new_card: Card):
        self.dealer_cards.append(new_card)
        print(
            f"Dealer Hit. New hand: {', '.join(str(card) for card in self.dealer_cards)}"
        )

    def dealer_wins(
        self, winner: BlackJackPlayer, player_hand: list[Card], dealer_hand: list[Card]
    ):
        self.winner = winner
        self.player_cards = player_hand
        self.dealer_cards = dealer_hand
        self.render_game_end()

    def player_wins(
        self,
        winner: BlackJackPlayer,
        payout: float,
        player_hand: list[Card],
        dealer_hand: list[Card],
    ):
        self.winner = winner
        self.player_cards = player_hand
        self.dealer_cards = dealer_hand
        self.payout = payout
        self.render_game_end()

    def render_game_end(self):

        print(f"Winner: {self.winner.player.name}!")
        print(
            f"Final Hands - Player: {', '.join(str(card) for card in self.player_cards)}, "
            f"Dealer: {', '.join(str(card) for card in self.dealer_cards)}"
        )
        if self.payout:
            print(f"Payout: ${self.payout:.2f}!")
