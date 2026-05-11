from .poker import Poker
from .events import PokerEvent
from casino.player import PlayerController


def test_choose_dealer():
    player = PlayerController("Test")
    game = Poker(player)

    game.choose_dealer()

    assert game.dealer == game.all_players[game.dealer_idx]


def test_deal_cards():
    player = PlayerController("Test")
    game = Poker(player)

    game.deal_cards()

    assert all(map(lambda p: len(p.cards) == 2, game.all_players))


def test_pay_blinds():
    player = PlayerController("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    assert (
        game.all_players[(game.dealer_idx + 1) % len(game.all_players)].player.money
        == 1000 - game.big_blind / 2
    )
    assert (
        game.all_players[(game.dealer_idx + 2) % len(game.all_players)].player.money
        == 1000 - game.big_blind
    )


def test_player_call():
    player = PlayerController("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    game.player_call(game.active_player)

    assert game.active_player.player.money == 1000 - game.big_blind


def test_player_all_in_call():
    player = PlayerController("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    missing = 1

    game.active_player.player.money = game.current_bet - missing

    game.player_call(game.active_player)

    assert game.active_player.player.money == 0
    assert game.call_count == 0


def test_player_fold():
    player = PlayerController("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    game.player_fold(game.active_player)

    assert game.active_player not in game.active_players


def test_player_raise():
    player = PlayerController("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    min_raise = game.min_raise
    raise_by = 10

    game.player_raise(game.active_player, min_raise + raise_by)

    assert game.last_raise == raise_by


def test_player_raise_all_in():
    player = PlayerController("Test")
    game = Poker(player)

    game.choose_dealer()
    game.pay_blinds()

    current_bet = game.current_bet
    min_raise = game.min_raise

    game.active_player.player.money = game.current_bet + min_raise - 1

    min_raise = game.min_raise

    game.player_raise(game.active_player, game.active_player.player.money)

    assert game.active_player.player.money == 0
    assert game.current_bet == current_bet
