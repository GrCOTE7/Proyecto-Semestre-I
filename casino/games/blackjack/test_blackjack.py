from casino.games.blackjack import BlackjackPhase
from casino.games.blackjack.blackjack import Blackjack
from casino.games.blackjack import BlackjackEvent
from casino.player import Player
from utils.cards import Card, Rank, Suit


def test_active_player():
    player = Player("Test Player")

    game = Blackjack(player)
    assert game.active_player.player.name == "Test Player"

    game.change_phase(BlackjackPhase.DEALER_TURN)
    assert game.active_player.player.name == "Dealer"


def test_hit_and_stand():
    player = Player("Test Player")
    game = Blackjack(player)
    game.accept_bet(100)

    # Simulate player hitting
    game.hit(game.active_player)
    assert len(game.active_player.cards) == 3  # Initial 2 cards + 1 hit

    # Simulate player standing
    game.dealer_play()
    assert game.game_phase == BlackjackPhase.ROUND_END


def test_hand_value_calculation():
    player = Player("Test Player")
    game = Blackjack(player)
    game.accept_bet(100)

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


def test_dealer_play():
    player = Player("Test Player")
    game = Blackjack(player)

    events = []

    def on_dealer_hit(event, _):
        events.append(event)

    game.subscribe(BlackjackEvent.DEALER_HIT, on_dealer_hit)

    game.accept_bet(100)
    # Simulate player standing immediately
    game.dealer_play()

    # Dealer should have at least 2 cards (initial hand)
    assert len(game.dealer.cards) >= 2
    # Check that the DEALER_HIT event was triggered at least once
    assert any(event == BlackjackEvent.DEALER_HIT for event in events)


def test_player_bust():
    player = Player("Test Player")
    game = Blackjack(player)
    game.accept_bet(100)

    # Simulate player hitting until they bust
    while game.active_player.hand_value <= 21:
        game.hit(game.active_player)

    assert game.active_player.hand_value > 21
    assert game.game_phase == BlackjackPhase.ROUND_END


def test_dealer_bust():
    player = Player("Test Player")
    game = Blackjack(player)
    game.accept_bet(100)

    game.dealer.cards = game.deck.deal(22)  # Force dealer to bust
    game.hit(game.dealer)

    assert game.dealer.hand_value > 21
    assert game.game_phase == BlackjackPhase.ROUND_END


def test_full_round():
    player = Player("Test Player")
    game = Blackjack(player)
    game.accept_bet(100)

    # Simulate player hitting twice
    game.hit(game.active_player)
    game.hit(game.active_player)

    # Simulate player standing
    game.dealer_play()

    # Check that the round has ended
    assert game.game_phase == BlackjackPhase.ROUND_END


def test_player_wins():
    player = Player("Test Player")
    game = Blackjack(player)
    bet = 100
    game.accept_bet(bet)
    events = []

    def on_player_win(event, player_cards, dealer_cards):
        events.append((event, player_cards, dealer_cards))

    game.subscribe(BlackjackEvent.PLAYER_WINS, on_player_win)

    game.player.cards = [Card(Suit.HEARTS, Rank.ACE), Card(Suit.CLUBS, Rank.NINE)]
    game.dealer.cards = [Card(Suit.SPADES, Rank.NINE), Card(Suit.DIAMONDS, Rank.SEVEN)]
    game.end_round()

    assert game.game_phase == BlackjackPhase.ROUND_END
    assert player.money == 1100  # Blackjack pays 1:1

    assert len(events) == 1
    assert events[0][0] == BlackjackEvent.PLAYER_WINS
    assert events[0][1] == game.player.cards
    assert events[0][2] == game.dealer.cards


def test_player_wins_blackjack():
    player = Player("Test Player")
    game = Blackjack(player)
    bet = 100
    game.accept_bet(bet)
    events = []

    def on_player_win(event, player_cards, dealer_cards):
        events.append((event, player_cards, dealer_cards))

    game.subscribe(BlackjackEvent.PLAYER_WINS, on_player_win)

    game.player.cards = [Card(Suit.HEARTS, Rank.ACE), Card(Suit.CLUBS, Rank.JACK)]
    game.dealer.cards = [Card(Suit.SPADES, Rank.NINE), Card(Suit.DIAMONDS, Rank.SEVEN)]
    game.end_round()

    assert game.game_phase == BlackjackPhase.ROUND_END
    assert player.money == 1150  # Blackjack pays 3:2

    assert len(events) == 1
    assert events[0][0] == BlackjackEvent.PLAYER_WINS
    assert events[0][1] == game.player.cards
    assert events[0][2] == game.dealer.cards


def test_dealer_wins():
    player = Player("Test Player")
    game = Blackjack(player)
    bet = 100
    game.accept_bet(bet)
    events = []

    def on_dealer_win(event, player_cards, dealer_cards):
        events.append((event, player_cards, dealer_cards))

    game.subscribe(BlackjackEvent.DEALER_WINS, on_dealer_win)

    game.player.cards = [Card(Suit.HEARTS, Rank.TEN), Card(Suit.CLUBS, Rank.SIX)]
    game.dealer.cards = [Card(Suit.SPADES, Rank.NINE), Card(Suit.DIAMONDS, Rank.EIGHT)]
    game.end_round()

    assert game.game_phase == BlackjackPhase.ROUND_END
    assert player.money == 900  # Player loses the bet

    assert len(events) == 1
    assert events[0][0] == BlackjackEvent.DEALER_WINS
    assert events[0][1] == game.player.cards
    assert events[0][2] == game.dealer.cards
