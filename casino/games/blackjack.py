from . import Game
from casino.player import Player
from utils.cards import Deck, Card, Rank
from utils.inputs import enum_input
from enum import Enum
from dataclasses import dataclass

class Action(Enum):
    HIT = 'h'
    STAND = 's'

@dataclass
class BlackJackPlayer(Player):
    player: Player
    cards: list[Card]

class Blackjack(Game):
    deck: Deck
    dealer = BlackJackPlayer
    player: BlackJackPlayer

    bet: float

    def __init__(self, player: Player, bet: float):
        if bet <= 0:
            raise ValueError("Bet must be greater than zero.")
        if bet > player.money:
            raise ValueError("Bet cannot exceed player's balance.")

        self.dealer = BlackJackPlayer(Player("Dealer"), [])
        self.player = BlackJackPlayer(player, [])
        self.deck = Deck(True)

        self.bet = bet
        self.player.player.money -= bet

    def run(self):
        player_busts = False

        self.dealer.cards = self.deck.deal(2)
        print(f"Dealer's cards: {self.dealer.cards[0]} [?]")

        self.player.cards += self.deck.deal(2)

        print(f"{self.player.player.name}'s cards: {' '.join(str(card) for card in self.player.cards)}")

        while True:
            choice = enum_input(f"{self.player.player.name}, do you want to hit or stand? (h/s): ", Action)
                
            match choice:
                case Action.HIT:
                    new_card = self.deck.deal(1)[0]
                    self.player.cards.append(new_card)
                    
                    print(f"{self.player.player.name} hits {new_card} and now has: {'  '.join(str(card) for card in self.player.cards)}")

                    evaluation = Blackjack.evaluate_hand(self.player.cards)

                    if evaluation > 21:
                        print(f"{self.player.player.name} busts with a total of {evaluation}.")
                        player_busts = True
                        break
                case Action.STAND:
                    print(f"{self.player.player.name} stands.")
                    break
                case _:
                    print("Invalid choice. Please enter 'h' to hit or 's' to stand.")

      
        while evaluation := Blackjack.evaluate_hand(self.dealer.cards) < 17 and not player_busts:
            new_card = self.deck.deal(1)[0]
            self.dealer.cards.append(new_card)
            print(f"Dealer hits and receives {new_card} and now has: {'   '.join(str(card) for card in self.dealer.cards)}")

            if evaluation > 21:
                print(f"Dealer busts with a total of {evaluation}. {self.player.player.name} wins!")
                break

        final_dealer_value = Blackjack.evaluate_hand(self.dealer.cards)
        final_player_value = Blackjack.evaluate_hand(self.player.cards)

        print(f"Dealer's final hand: {' '.join(str(card) for card in self.dealer.cards)} with a total of {final_dealer_value}.")
        print(f"{self.player.player.name}'s final hand: {' '.join(str(card) for card in self.player.cards)} with a total of {final_player_value}.")

        if not player_busts and (final_player_value > final_dealer_value or final_dealer_value > 21):
            payout = self.bet * 2
            self.player.player.money += payout
            print(f"{self.player.player.name} wins ${payout} and now has ${self.player.player.money:.2f}.")
        elif final_player_value == final_dealer_value:
            print(f"{self.player.player.name} ties with the dealer and gets back their bet of ${self.bet:.2f}.")
            self.player.player.money += self.bet
        else:
            print(f"{self.player.player.name} loses the bet of ${self.bet:.2f} and now has ${self.player.player.money:.2f}.")

 
    def evaluate_hand(hand: list[Card]) -> int:
        """Calculate the total value of a hand of cards, accounting for Aces."""
        value = 0
        aces = 0

        for card in hand:
            if card.rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
                value += 10
            elif card.rank == Rank.ACE:
                aces += 1
                value += 11
            else:
                value += int(card.rank.value)

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value
