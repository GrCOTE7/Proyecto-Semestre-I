from uuid import uuid4

from casino.games.poker.poker import Poker, HandRank
from casino.games.poker.events import PokerEvent
from casino.player import PlayerBuyIn, PlayerController
from pytest import fixture
from utils.cards import Card, Suit, Rank


@fixture
def poker_game(mock_context) -> Poker:
    return Poker(
        mock_context["bus"],
        PlayerBuyIn(mock_context["player"].id, mock_context["player"].name, 1000),
        [PlayerBuyIn(uuid4(), f"CPU {i + 1}", 1000) for i in range(3)],
    )


def test_choose_dealer(poker_game: Poker):
    poker_game.choose_dealer()

    assert poker_game.dealer == poker_game.all_players[poker_game.dealer_idx]


def test_deal_cards(poker_game: Poker):
    poker_game.choose_dealer()  # Running choose dealer to initialize the current_player_idx which is based on the dealer pos
    poker_game.deal_cards()

    assert all(map(lambda p: len(p.cards) == 2, poker_game.all_players))


def test_pay_blinds(poker_game: Poker):
    poker_game.choose_dealer()
    poker_game.pay_blinds()

    assert (
        poker_game.all_players[
            (poker_game.dealer_idx + 1) % len(poker_game.all_players)
        ].funds
        == 1000 - poker_game.big_blind / 2
    )
    assert (
        poker_game.all_players[
            (poker_game.dealer_idx + 2) % len(poker_game.all_players)
        ].funds
        == 1000 - poker_game.big_blind
    )


def test_player_call(poker_game: Poker):
    poker_game.choose_dealer()
    poker_game.pay_blinds()

    active_player = poker_game.active_player
    poker_game.player_call()

    assert active_player.funds == 1000 - poker_game.big_blind


def test_player_all_in_call(poker_game: Poker):
    poker_game.choose_dealer()
    poker_game.pay_blinds()

    missing = 1

    poker_game.active_player.funds = poker_game.current_bet - missing

    poker_game.player_call()

    assert poker_game.active_players[poker_game.current_player_idx - 1].funds == 0
    assert poker_game.call_count == 0


def test_player_fold(poker_game: Poker):
    poker_game.choose_dealer()
    poker_game.pay_blinds()

    active_player = poker_game.active_player
    poker_game.player_fold()

    assert active_player not in poker_game.active_players


def test_player_raise(poker_game: Poker):
    poker_game.choose_dealer()
    poker_game.pay_blinds()

    min_raise = poker_game.min_raise
    raise_by = 10

    poker_game.player_raise(poker_game.current_bet + min_raise + raise_by)

    assert poker_game.last_raise == min_raise + raise_by


def test_player_raise_all_in(poker_game: Poker):
    poker_game.choose_dealer()
    poker_game.pay_blinds()

    current_bet = poker_game.current_bet
    min_raise = poker_game.min_raise

    poker_game.active_player.funds = poker_game.current_bet + min_raise - 1

    min_raise = poker_game.min_raise

    poker_game.player_raise(poker_game.active_player.funds)

    assert (
        poker_game.active_players[
            (poker_game.current_player_idx - 1) % len(poker_game.active_players)
        ].funds
        == 0
    )
    assert poker_game.current_bet == current_bet


def test_best_hand(poker_game: Poker):
    poker_game.active_players[0].cards = [
        Card(Suit.SPADES, Rank.ACE),
        Card(Suit.SPADES, Rank.KING),
    ]
    poker_game.active_players[1].cards = [
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.HEARTS, Rank.KING),
    ]
    poker_game.active_players[2].cards = [
        Card(Suit.DIAMONDS, Rank.ACE),
        Card(Suit.DIAMONDS, Rank.KING),
    ]
    poker_game.active_players[3].cards = [
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.CLUBS, Rank.KING),
    ]

    poker_game.community_cards = [
        Card(Suit.SPADES, Rank.TWO),
        Card(Suit.SPADES, Rank.THREE),
        Card(Suit.SPADES, Rank.FOUR),
        Card(Suit.SPADES, Rank.FIVE),
        Card(Suit.SPADES, Rank.SIX),
    ]

    best_hands = [
        poker_game.best_hand(p.cards, poker_game.community_cards)
        for p in poker_game.active_players
    ]

    assert best_hands[0][0] == HandRank.STRAIGHT_FLUSH
    assert best_hands[1][0] == HandRank.STRAIGHT_FLUSH
    assert best_hands[2][0] == HandRank.STRAIGHT_FLUSH
    assert best_hands[3][0] == HandRank.STRAIGHT_FLUSH
