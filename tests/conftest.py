import pytest
from uuid import uuid4
from utils.event_listener import EventBus
from utils.commands.command_manager import CommandManager
from casino.player import PlayerAccount


@pytest.fixture
def mock_context():
    return {
        "bus": EventBus(),
        "player": PlayerAccount(uuid4(), "Test Player", 1000),
    }
