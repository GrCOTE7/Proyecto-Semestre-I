from .poker import Poker
from .events import PokerEvent
from casino.player import Player

def test_choose_dealer():
    player = Player("Test")
    game = Poker(player)

    game.choose_dealer()

    assert game.dealer == game.all_players[game.dealer_idx]

def test_deal_cards():
    player = Player("Test")
    game = Poker(player)

    game.deal_cards()

    assert all(map(lambda p: len(p.cards) == 2, game.all_players))

def test_pay_blinds():
    player = Player("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    assert game.all_players[(game.dealer_idx + 1) % len(game.all_players)].player.money == 1000 - game.big_blind / 2
    assert game.all_players[(game.dealer_idx + 2) % len(game.all_players)].player.money == 1000 - game.big_blind

def test_player_call():
    player = Player("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    # game.subscribe()

    game.player_call(game.active_player)

    assert game.active_player.player.money == 1000 - game.big_blind

def test_player_fold():
    player = Player("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    game.player_fold(game.active_player)

    assert game.active_player not in game.active_players

def test_player_raise():
    player = Player("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    min_raise = game.min_raise
    raise_by = 10

    game.player_raise(game.active_player, min_raise + raise_by)

    assert game.last_raise == raise_by