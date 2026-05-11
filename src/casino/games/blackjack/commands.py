from utils.commands.command import Command
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .blackjack import Blackjack


class HitCommand(Command):
    """Command to handle the player's decision to hit (take another card)."""

    game: Blackjack

    def __init__(
        self,
        game: Blackjack,
    ):
        super().__init__(game, "Hit (h): Take another card from the deck.")

    def execute(self):
        active_player = self.game.active_player
        self.game.hit(active_player)


class StandCommand(Command):
    """Command to handle the player's decision to stand (keep their current hand)."""

    game: Blackjack

    def __init__(self, game: Blackjack):
        super().__init__(game, "Stand (s): Keep your current hand. Ends your turn.")

    def execute(self):
        self.game.dealer_play()


class RequestBetCommand(Command):
    """Command to handle the player's decision to place a bet before the round starts."""

    game: Blackjack

    def __init__(self, game: Blackjack):
        super().__init__(game, "Place Bet: Place your bet for the round.")

    def execute(self):
        self.game.request_bet()
