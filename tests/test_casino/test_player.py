from casino.games import PlayerController
import pytest


def test_deposit():
    player = PlayerController("Test Player")
    player.deposit(100)
    assert player.money == 1100


def test_withdraw():
    player = PlayerController("Test Player")
    player.withdraw(50)
    assert player.money == 950


def test_withdraw_insufficient_funds():
    player = PlayerController("Test Player")
    with pytest.raises(ValueError):
        player.withdraw(2000)
