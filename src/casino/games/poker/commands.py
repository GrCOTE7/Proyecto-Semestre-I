from utils.commands.command import Command
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .poker import Poker


class CallCommand(Command):
    game: Poker

    def execute(self):
        self.game.player_call()


class RaiseCommand(Command):
    game: Poker

    def __init__(self, game: Poker, amount: float):
        super().__init__(game)
        self.raise_amount = amount

    def execute(self):
        # TODO: Implement poker function to raise given value.
        # Only called for user player, so we can directly request the raise amount.
        # CPU players will automatically raise a random amount within their budget.
        if self.game.active_player == self.game.player:
            self.game.player_raise(self.raise_amount)


class FoldCommand(Command):
    game: Poker

    def execute(self):
        self.game.player_fold()


class ResetHandCOmmand(Command):
    game: Poker

    def execute(self):
        self.game.finish_hand(reset=True)


class EndHandCommand(Command):
    game: Poker

    def execute(self):
        self.game.finish_hand(reset=False)
