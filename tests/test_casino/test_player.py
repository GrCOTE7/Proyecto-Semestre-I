from casino.player import PlayerAccount
from uuid import uuid4


def test_deposit():
    player = PlayerAccount(id=uuid4(), name="Test Player", balance=1000)
    player.deposit(100)
    assert player.balance == 1100


def test_withdraw():
    player = PlayerAccount(id=uuid4(), name="Test Player", balance=1000)
    player.withdraw(50)
    assert player.balance == 950


def test_withdraw_insufficient_funds():
    player = PlayerAccount(id=uuid4(), name="Test Player", balance=1000)
    assert player.withdraw(2000) == False
