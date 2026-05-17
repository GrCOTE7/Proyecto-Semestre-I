from utils.commands.command import Command
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .blackjack import Blackjack


class HitCommand(Command):
    """Command to handle the player's decision to hit (take another card)."""

    game: Blackjack

    def execute(self):
        player_id = self.game.active_player
        # If the active player is None, it means it's the dealer's turn, so we use the dealer as the active player for hitting.
        active_player = self.game.get_player_by_id(player_id) or self.game.dealer
        self.game.hit(active_player)


class StandCommand(Command):
    """Command to handle the player's decision to stand (keep their current hand)."""

    game: Blackjack

    def execute(self):
        self.game.dealer_play()
