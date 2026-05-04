from casino.games import Game, Player
from enum import Enum
from casino.games.generic_events import GenericEvent


class DummyPhase(Enum):
    PHASE_ONE = 1
    PHASE_TWO = 2


class DummyGame(Game):
    def __init__(self, player: Player):
        super().__init__("Dummy Game")
        self._active_player = player

    @property
    def active_player(self) -> Player:
        return self._active_player


def test_finite_state_machine():
    game = DummyGame(Player("Test Player"))
    game.game_phase = DummyPhase.PHASE_ONE

    assert game.game_phase == DummyPhase.PHASE_ONE

    game.change_phase(DummyPhase.PHASE_TWO)
    assert game.game_phase == DummyPhase.PHASE_TWO


def test_event_notification():
    game = DummyGame(Player("Test Player"))
    events_triggered = []

    def on_phase_change(event, new_phase):
        events_triggered.append((event, new_phase))

    game.subscribe(GenericEvent.PHASE_CHANGE, on_phase_change)
    game.change_phase(DummyPhase.PHASE_ONE)

    assert len(events_triggered) == 1
    assert events_triggered[0][0] == GenericEvent.PHASE_CHANGE
    assert events_triggered[0][1] == DummyPhase.PHASE_ONE


def test_active_player():
    player = Player("Test Player")
    game = DummyGame(player)
    assert game.active_player.name == "Test Player"
