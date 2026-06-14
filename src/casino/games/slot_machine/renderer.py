from utils.renderer import Renderer
from casino.games.generic_events import GenericEvent
from casino.games.slot_machine.events import SlotMachineEvents
from casino.games.slot_machine.slot_machine import SlotMachineSnapshot


class SlotMachineTerminalRenderer(Renderer):
    def __init__(self, event_bus):
        super().__init__(event_bus)

        self.event_bus.subscribe(SlotMachineEvents.SPIN_RESULT, self.render)
        self.event_bus.subscribe(SlotMachineEvents.PLAYER_CHOICE, self.available_commands)

    def render(self, snapshot: SlotMachineSnapshot):
        print(f"{snapshot.reels[0].value} {snapshot.reels[1].value} {snapshot.reels[2].value}")
        if multiplier := snapshot.multiplier > 1:
            print(f"Congratulations! You won with a multiplier of {snapshot.multiplier}x!")
    
        print(f"Player Funds: ${snapshot.active_player.funds:.2f}")

    def available_commands(self, snapshot: SlotMachineSnapshot) -> list[str]:
        for i, command in enumerate(snapshot.available_commands, start=1):
            print(f"{i}. {command.display_name}")
