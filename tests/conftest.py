import pytest
from unittest.mock import Mock
from uuid import uuid4


@pytest.fixture
def mock_context():
    """Provides the standard 'wiring' needed for any component."""
    return {"bus": Mock(), "cmd": Mock(), "id": uuid4()}
