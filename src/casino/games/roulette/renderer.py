from utils.renderer import Renderer
from utils.event_listener import EventBus
from casino.games.roulette.roulette import RouletteSnapshot, RouletteCell, Color
from casino.games.roulette.bets import RouletteBet
from casino.games.roulette.events import RouletteEvents
from casino.games.generic_events import GenericEvent

class RouletteRenderer(Renderer):
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self.event_bus.subscribe(RouletteEvents.BET_PLACED, self.on_bet) 
        self.event_bus.subscribe(RouletteEvents.BET_REMOVED, self.on_bet)
        self.event_bus.subscribe(RouletteEvents.SPIN_RESULT, self.on_spin_result)
        self.event_bus.subscribe(RouletteEvents.PLAYER_TURN_START, self.show_commands)

    def on_bet(self, snapshot: RouletteSnapshot):
        print(f"Bets: {list(snapshot.bets.values())}")

    def on_spin_result(self, snapshot: RouletteSnapshot):
        print(f"Spin result: {snapshot.landing_cell}")
        if snapshot.payouts:
            print("Winning bets:")
            for bet in snapshot.payouts:
                print(f" Winning: - {bet}")

            total_earnings = sum(bet.earnings() for bet in snapshot.payouts)
            print(f"Total earnings: ${total_earnings}")
        else:
            print("No winning bets this round.")

    def show_commands(self, snapshot: RouletteSnapshot):
        print("Available commands:")
        for i, command in enumerate(snapshot.available_commands):
            print(f" - {i + 1}. {command.display_name}")
