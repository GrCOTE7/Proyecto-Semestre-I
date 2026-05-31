from casino.player import CPUController
from .events import PokerEvent

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .poker import PokerSnapshot


class PokerCPU(CPUController):
    def __init__(self, name, command_manager, event_bus, player_id):
        super().__init__(name, command_manager, event_bus, player_id)
        self.event_bus.subscribe(PokerEvent.CHANGE_PLAYER_TURN, self.on_player_action)

    def on_player_action(self, snapshot: PokerSnapshot):
        if self.player_id == snapshot.player.id:
            commands = snapshot.available_commands

            # For simplicity, the CPU will always call if it has enough funds, otherwise it will fold.
            if snapshot.current_bet <= snapshot.player.funds:
                self.command_manager.execute_command(
                    list(filter(lambda c: c.display_name == "Call", commands))[0]
                )
            else:
                self.command_manager.execute_command(
                    self.command_manager.execute_command(
                        list(filter(lambda c: c.display_name == "Fold", commands))[0]
                    )
                )
