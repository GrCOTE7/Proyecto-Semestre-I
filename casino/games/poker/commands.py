from utils.commands.command import Command
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .poker import Poker


class CallCommand(Command):
    game: Poker

    def __init__(self, game: Poker):
        super().__init__(game)

    def execute(self):
        self.game.player_call(self.game.active_player)


class RaiseCommand(Command):
    game: Poker

    def __init__(self, game: Poker):
        super().__init__(game)

    def execute(self):
        # Only called for user player, so we can directly request the raise amount.
        # CPU players will automatically raise a random amount within their budget.
        if self.game.active_player == self.game.player:
            self.game.request_player_raise()


class FoldCommand(Command):
    game: Poker

    def __init__(self, game: Poker):
        super().__init__(game)

    def execute(self):
        self.game.player_fold(self.game.active_player)
