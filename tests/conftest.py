import pytest
from uuid import uuid4
from utils.event_listener import EventBus
from casino.player import PlayerAccount, PlayerController


@pytest.fixture
def mock_context():
    return {
        "bus": EventBus(),
        "player": PlayerAccount(uuid4(), "Test Player", 1000),
    }


@pytest.fixture
def mock_player_controller(mock_context):
    return PlayerController(
        mock_context["bus"], mock_context["cmd"], mock_context["player"].id
    )
