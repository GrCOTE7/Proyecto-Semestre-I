from casino.games.generic_events import GenericEvent
from casino.games.poker.phases import PokerPhase
from utils.event_listener import EventBus
from utils.renderer import Renderer
from .poker import PokerSnapshot
from .events import PokerEvent


class PokerRenderer(Renderer):
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)

        self.event_bus.subscribe(PokerEvent.DEAL_CARDS, self.render_hands)
        self.event_bus.subscribe(PokerEvent.CHOOSE_DEALER, self.render_dealer)
        self.event_bus.subscribe(PokerEvent.PAID_BLIND, self.render_blinds)
        self.event_bus.subscribe(PokerEvent.PLAYER_CALL, self.render_player_calls)
        self.event_bus.subscribe(PokerEvent.PLAYER_RAISE, self.render_player_raises)
        self.event_bus.subscribe(PokerEvent.PLAYER_FOLD, self.render_player_folds)
        self.event_bus.subscribe(GenericEvent.PHASE_CHANGE, self.render_community_cards)
        self.event_bus.subscribe(PokerEvent.PLAYER_ALL_IN, self.render_all_in)
        self.event_bus.subscribe(
            PokerEvent.AVAILABLE_COMMANDS, self.render_available_commands
        )
        self.event_bus.subscribe(PokerEvent.HAND_OVER, self.render_hand_over)

    def render_hands(self, snapshot: PokerSnapshot):
        """Renders the active player's hand. If hide_hand is True, it will not show the cards during the dealing process."""

        for player in snapshot.active_players:
            print(
                f"{player.name}'s hand: {[str(card) if card.is_face_up else '[Hidden]' for card in player.cards]}"
            )

    def render_dealer(self, snapshot: PokerSnapshot):
        print(f"Dealer is: {snapshot.dealer.name}")

    def render_blinds(self, snapshot: PokerSnapshot):
        print(
            f"Blinds paid: Small blind = ${snapshot.big_blind / 2:.2f}, Big blind = ${snapshot.big_blind:.2f}"
        )

    def render_player_calls(self, snapshot: PokerSnapshot):
        print(f"{snapshot.player.name} calls.")

    def render_player_raises(self, snapshot: PokerSnapshot):
        print(f"{snapshot.player.name} raises to ${snapshot.current_bet:.2f}.")

    def render_player_folds(self, snapshot: PokerSnapshot):
        print(f"{snapshot.player.name} folds.")

    def render_community_cards(self, _, data: tuple[PokerPhase, PokerSnapshot]):
        if data[0] in [PokerPhase.FLOP, PokerPhase.TURN, PokerPhase.RIVER]:
            print(
                f"Community cards: {[str(card) for card in data[1].community_cards]} (Pot: ${data[1].pot:.2f})"
            )

    def render_all_in(self, snapshot: PokerSnapshot):
        print(f"{snapshot.player.name} goes all-in with ${snapshot.current_bet:.2f}.")

    def render_available_commands(self, snapshot: PokerSnapshot):
        print(f"Available commands ({snapshot.player.funds}$ available):")
        for idx, command in enumerate(snapshot.available_commands, start=1):
            print(f"{idx}. {command.display_name}")

    def render_hand_over(self, snapshot: PokerSnapshot):
        if snapshot.winners:
            winners_str = ", ".join([winner.name for winner in snapshot.winners])
            print(f"Hand over! Winner(s): {winners_str} (Pot: ${snapshot.pot:.2f})")
        else:
            print("Hand over! No winners determined.")
