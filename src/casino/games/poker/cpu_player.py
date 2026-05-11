from casino.player import CPUController
from typing import TYPE_CHECKING
from .events import PokerEvent

if TYPE_CHECKING:
    from casino.games.poker.poker import Poker


class CPU(CPUController):
    game: Poker

    def __init__(self, name: str, game: Poker):
        super().__init__(name, game)

    def on_game_event(self, event: PokerEvent, *args, **kwargs):
        match event:
            case PokerEvent.CHANGE_PLAYER_TURN:
                if self.game.active_player.player.id == self.id:
                    self.game.active_player.make_decision()
