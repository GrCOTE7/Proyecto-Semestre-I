from utils.event_listener import EventBus
from utils.renderer import Renderer
from . import BlackjackEvent, BlackjackPhase
from .blackjack import BlackjackSnapshot
from utils.cards import CardView
from casino.games import GenericEvent


class BlackjackTerminalRenderer(Renderer):
    player_hand: list[CardView] = []
    dealer_hand: list[CardView] = []

    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self.event_bus.subscribe(BlackjackEvent.PLAYER_HIT, self.player_hit)
        self.event_bus.subscribe(BlackjackEvent.DEALER_HIT, self.dealer_hit)
        self.event_bus.subscribe(BlackjackEvent.DEALER_WINS, self.dealer_wins)
        self.event_bus.subscribe(BlackjackEvent.PLAYER_WINS, self.player_wins)
        self.event_bus.subscribe(GenericEvent.PHASE_CHANGE, self.handle_phase_change)

        self.player_cards = []
        self.dealer_cards = []

    def show_available_commands(self, snapshot: BlackjackSnapshot):
        print("Available Commands:")
        for i, cmd in enumerate(snapshot.available_commands):
            print(f"{i+1} {cmd.display_name}.")

    def player_hit(self, snapshot: BlackjackSnapshot):
        self.player_cards = snapshot.player_cards
        if snapshot.active_player:
            self._render_table(f"{snapshot.active_player.name} Hits")

    def dealer_hit(self, snapshot: BlackjackSnapshot):
        self.dealer_cards = snapshot.dealer_cards
        self._render_table("Dealer Hits")

    def handle_phase_change(self, state: tuple[BlackjackPhase, BlackjackSnapshot]):
        new_phase, snapshot = state
        if new_phase == BlackjackPhase.PLAYER_TURN:
            self.show_available_commands(snapshot)

    def dealer_wins(self, snapshot: BlackjackSnapshot):
        self.dealer_cards = snapshot.dealer_cards
        self.player_cards = snapshot.player_cards
        self._render_table(f"Dealer Wins. You lose your bet (${abs(snapshot.payout)}).")

    def player_wins(self, snapshot: BlackjackSnapshot):
        self.dealer_cards = snapshot.dealer_cards
        self.player_cards = snapshot.player_cards
        self._render_table(
            f"Congratulations {snapshot.active_player.name}, you win! You gain ${snapshot.payout}."
        )

    def _render_table(self, msg: str):
        print(f"--- {msg} ---")
        print(f"Player's Hand: {', '.join(str(card) for card in self.player_cards)}")
        print(f"Dealer's Hand: {', '.join(str(card) for card in self.dealer_cards)}")
