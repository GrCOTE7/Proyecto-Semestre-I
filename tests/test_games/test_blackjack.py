from uuid import uuid4

from casino.games.blackjack import BlackjackPhase
from casino.games.blackjack.blackjack import Blackjack, BlackjackResult
from casino.games.blackjack import BlackjackEvent
from casino.player import PlayerController
from utils.cards import Card, Rank, Suit, CardView
from casino.player import PlayerBuyIn
from pytest import fixture


@fixture
def mock_player_controller(mock_context):
    return PlayerController(
        mock_context["bus"], mock_context["cmd"], mock_context["player"].id
    )


@fixture
def blackjack_game(mock_context, mock_player_controller):
    return Blackjack(
        mock_context["bus"],
        mock_player_controller,
        PlayerBuyIn(uuid4(), mock_context["player"].id, 100),
    )


def test_active_player(blackjack_game):
    game: Blackjack = blackjack_game
    assert game.active_player == game.buy_in.player_id

    game.change_phase(BlackjackPhase.DEALER_TURN)
    assert game.active_player == None


def test_hit_and_stand(blackjack_game):
    game: Blackjack = blackjack_game

    # Simulate player hitting
    game.hit(game.player)
    assert len(game.player.cards) == 1  # Initial 2 cards + 1 hit

    # Simulate player standing
    game.dealer_play()
    assert game.game_phase == BlackjackPhase.ROUND_END


def test_hand_value_calculation(blackjack_game):
    game: Blackjack = blackjack_game

    # Test hand value with number cards
    game.player.cards = [
        Card(Suit.HEARTS, Rank.TWO),
        Card(Suit.CLUBS, Rank.THREE),
    ]
    assert game.player.hand_value == 5

    # Test hand value with face cards
    game.player.cards = [Card(Suit.SPADES, Rank.JACK), Card(Suit.DIAMONDS, Rank.QUEEN)]
    assert game.player.hand_value == 20

    # Test hand value with aces
    game.player.cards = [Card(Suit.HEARTS, Rank.ACE), Card(Suit.CLUBS, Rank.SIX)]
    assert game.player.hand_value == 17

    # Test hand value with multiple aces
    game.player.cards = [
        Card(Suit.HEARTS, Rank.ACE),
        Card(Suit.CLUBS, Rank.ACE),
        Card(Suit.DIAMONDS, Rank.FIVE),
    ]
    assert game.player.hand_value == 17


def test_dealer_play(blackjack_game):
    game: Blackjack = blackjack_game

    events = []

    def on_dealer_hit(_):
        events.append(BlackjackEvent.DEALER_HIT)

    game.event_bus.subscribe(BlackjackEvent.DEALER_HIT, on_dealer_hit)

    # Simulate player standing immediately
    game.dealer_play()

    # Dealer should have at least 2 cards (initial hand)
    assert len(game.dealer.cards) >= 2
    # Check that the DEALER_HIT event was triggered at least once
    assert any(event == BlackjackEvent.DEALER_HIT for event in events)


def test_player_bust(blackjack_game):
    game: Blackjack = blackjack_game

    # Simulate player hitting until they bust
    while game.player.hand_value <= 21:
        game.hit(game.player)

    assert game.player.hand_value > 21
    assert game.game_phase == BlackjackPhase.ROUND_END


def test_dealer_bust(blackjack_game):
    game: Blackjack = blackjack_game

    game.dealer.cards = game.deck.deal(22)  # Force dealer to bust
    game.hit(game.dealer)

    assert game.dealer.hand_value > 21
    assert game.game_phase == BlackjackPhase.ROUND_END


def test_full_round(blackjack_game):
    game: Blackjack = blackjack_game

    # Simulate player hitting twice
    game.hit(game.player)
    game.hit(game.player)

    # Simulate player standing
    game.dealer_play()

    # Check that the round has ended
    assert game.game_phase == BlackjackPhase.ROUND_END


def test_player_wins(blackjack_game):
    game: Blackjack = blackjack_game
    result: BlackjackResult = None

    def on_player_win(res: BlackjackResult):
        nonlocal result
        result = res

    game.event_bus.subscribe(BlackjackEvent.PLAYER_WINS, on_player_win)

    game.player.cards = [Card(Suit.HEARTS, Rank.ACE), Card(Suit.CLUBS, Rank.NINE)]
    game.dealer.cards = [Card(Suit.SPADES, Rank.NINE), Card(Suit.DIAMONDS, Rank.SEVEN)]
    game.end_round()

    assert result is not None
    assert game.game_phase == BlackjackPhase.ROUND_END
    assert result.payout == game.buy_in.amount * 2  # Blackjack pays 1:1

    assert result.player_cards == [
        CardView.from_card(card) for card in game.player.cards
    ]
    assert result.dealer_cards == [
        CardView.from_card(card) for card in game.dealer.cards
    ]


def test_player_wins_blackjack(blackjack_game):
    game: Blackjack = blackjack_game
    result: BlackjackResult = None

    def on_player_win(res: BlackjackResult):
        nonlocal result
        result = res

    game.event_bus.subscribe(BlackjackEvent.PLAYER_WINS, on_player_win)

    game.player.cards = [Card(Suit.HEARTS, Rank.ACE), Card(Suit.CLUBS, Rank.QUEEN)]
    game.dealer.cards = [Card(Suit.SPADES, Rank.NINE), Card(Suit.DIAMONDS, Rank.SEVEN)]
    game.end_round()

    assert result is not None
    assert game.game_phase == BlackjackPhase.ROUND_END
    assert result.payout == game.buy_in.amount * 2.5  # Blackjack pays 3:2

    assert result.player_cards == [
        CardView.from_card(card) for card in game.player.cards
    ]
    assert result.dealer_cards == [
        CardView.from_card(card) for card in game.dealer.cards
    ]


def test_dealer_wins(blackjack_game):
    game: Blackjack = blackjack_game
    result: BlackjackResult = None

    def on_dealer_win(winner, res: BlackjackResult):
        nonlocal result
        result = res

    game.event_bus.subscribe(BlackjackEvent.DEALER_WINS, on_dealer_win)

    game.player.cards = [Card(Suit.HEARTS, Rank.TEN), Card(Suit.CLUBS, Rank.SIX)]
    game.dealer.cards = [Card(Suit.SPADES, Rank.NINE), Card(Suit.DIAMONDS, Rank.EIGHT)]
    game.end_round()

    assert game.game_phase == BlackjackPhase.ROUND_END
    assert result.payout == 0  # Player loses, so payout is 0

    assert result is not None
    assert result.player_cards == [
        CardView.from_card(card) for card in game.player.cards
    ]
    assert result.dealer_cards == [
        CardView.from_card(card) for card in game.dealer.cards
    ]
