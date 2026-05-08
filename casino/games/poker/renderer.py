from utils.renderer import Renderer
from .poker import Poker
from .events import PokerEvent


class PokerRenderer(Renderer):
    game: Poker

    def __init__(self, game: Poker):
        super().__init__(game)

        game.subscribe(PokerEvent.DEAL_CARDS, self.render_hands)
        game.subscribe(PokerEvent.CHOOSE_DEALER, self.render_dealer)
        game.subscribe(PokerEvent.PAID_BLIND, self.render_blinds)
        game.subscribe(PokerEvent.PLAYER_CALL, self.render_player_action)
        game.subscribe(PokerEvent.PLAYER_RAISE, self.render_player_action)
        game.subscribe(PokerEvent.PLAYER_FOLD, self.render_player_action)

    def render_hands(self):
        """Renders the active player's hand. If hide_hand is True, it will not show the cards during the dealing process."""

        # Only render the active player's hand when they have 2 cards, to avoid showing the hand during the dealing process.
        for i, player in enumerate(self.game.all_players):
            label = (
                " (D)"
                if i == self.game.dealer_idx
                else (
                    " (SB)"
                    if i == (self.game.dealer_idx + 1) % len(self.game.all_players)
                    else (
                        " (BB)"
                        if i == (self.game.dealer_idx + 2) % len(self.game.all_players)
                        else ""
                    )
                )
            )

            if player != self.game.player:
                print(
                    f"{player.player.name}'s hand{label}: [??] ({player.player.money:.2f} chips)"
                )
            else:
                print(
                    f"{player.player.name}'s hand{label}: {[str(card) for card in player.cards]} ({player.player.money:.2f} chips)"
                )

    def render_dealer(self):
        print(f"Dealer is: {self.game.dealer.player.name}")

    def render_blinds(self):
        print(
            f"Blinds paid: Small blind = ${self.game.big_blind / 2:.2f}, Big blind = ${self.game.big_blind:.2f}"
        )

    def render_player_action(self):
        print(f"{self.game.active_player.player.name} calls.")

    def render_player_action(self):
        print(
            f"{self.game.active_player.player.name} raises to ${self.game.current_bet:.2f}."
        )

    def render_player_action(self):
        print(f"{self.game.active_player.player.name} folds.")
