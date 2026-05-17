from uuid import uuid4

from casino.games import Game
from enum import Enum
from casino.games.generic_events import GenericEvent
from casino.player import PlayerBuyIn

from utils.event_listener import EventBus


class DummyPhase(Enum):
    PHASE_ONE = 1
    PHASE_TWO = 2


class DummyGame(Game):
    def __init__(self):
        super().__init__(
            event_bus=EventBus(),
            buy_in=PlayerBuyIn(player_id=uuid4(), name="Test Player", amount=100),
        )

    @property
    def active_player(self):
        return self.buy_in.player_id


def test_finite_state_machine():
    game = DummyGame()
    game.game_phase = DummyPhase.PHASE_ONE

    assert game.game_phase == DummyPhase.PHASE_ONE

    game.change_phase(DummyPhase.PHASE_TWO)
    assert game.game_phase == DummyPhase.PHASE_TWO


def test_event_notification():
    game = DummyGame()
    events_triggered = []

    def on_phase_change(new_phase):
        events_triggered.append((GenericEvent.PHASE_CHANGE, new_phase))

    game.event_bus.subscribe(GenericEvent.PHASE_CHANGE, on_phase_change)
    game.change_phase(DummyPhase.PHASE_ONE)

    assert len(events_triggered) == 1
    assert events_triggered[0][0] == GenericEvent.PHASE_CHANGE
    assert events_triggered[0][1][0] == DummyPhase.PHASE_ONE


def test_active_player():
    game = DummyGame()
    assert game.active_player == game.buy_in.player_id
