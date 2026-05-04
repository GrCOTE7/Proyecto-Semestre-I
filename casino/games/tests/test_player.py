from casino.games import Player
import pytest


def test_deposit():
    player = Player("Test Player")
    player.deposit(100)
    assert player.money == 1100


def test_withdraw():
    player = Player("Test Player")
    player.withdraw(50)
    assert player.money == 950


def test_withdraw_insufficient_funds():
    player = Player("Test Player")
    with pytest.raises(ValueError):
        player.withdraw(2000)
