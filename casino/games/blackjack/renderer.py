from utils.renderer import Renderer
from .blackjack import Blackjack
from . import BlackjackEvent
from utils.cards import Card


class BlackjackTerminalRenderer(Renderer):
    player_cards: list[Card]
    dealer_cards: list[Card]

    def __init__(self, game: Blackjack):
        super().__init__(game)

        game.subscribe(BlackjackEvent.PLAYER_HIT, self.render_hand)
        game.subscribe(BlackjackEvent.DEALER_HIT, self.render_dealer_hand)

        self.player_cards = []
        self.dealer_cards = []

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
