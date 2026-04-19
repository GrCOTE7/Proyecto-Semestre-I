from . import Game
from casino.player import Player
from utils.cards import Deck, Card, Rank
from utils.terminal import term, BG_COLOR, draw_bg
from dataclasses import dataclass
from time import sleep


@dataclass
class BlackJackPlayer(Player):
    player: Player
    cards: list[Card]


class Blackjack(Game):
    deck: Deck
    dealer = BlackJackPlayer
    player: BlackJackPlayer
    bet: float

    bet: float

    def __init__(self, player: Player):
        self.dealer = BlackJackPlayer(Player("Dealer"), [])
        self.player = BlackJackPlayer(player, [])
        self.deck = Deck(True)

    def start(self):
        super().start()

        bet = ""
        bet_overflow = False

        while True:
            with term.hidden_cursor():
                with term.location(0, term.height // 2):
                    prompt = (
                        term.center(
                            f"Enter your bet amount (max {self.player.player.money}$): {f'${bet}' if bet else ''}",
                            term.width,
                        )
                        if not bet_overflow
                        else term.center(
                            f"Bet exceeds available money! Enter a valid bet amount (max {self.player.player.money}$): {f'${bet}' if bet else ''}",
                            term.width,
                        )
                    )

                    print(
                        BG_COLOR + term.italic(prompt),
                        end="",
                    )

                with term.cbreak():
                    key = term.inkey()

                    if key.isdigit() or (key == "." and "." not in bet):
                        bet += key
                    elif key in ["\b", "\x7f"]:  # Handle backspace
                        bet = bet[:-1]
                    elif key in ["\n", "\r"] and bet:
                        self.bet = float(bet)
                        if self.bet > self.player.player.money:
                            bet = ""
                            bet_overflow = True
                        else:
                            self.player.player.money -= self.bet
                            break

        print(term.clear(), end="")
        draw_bg()
        with term.location(0, term.height - 2):
            hint = "Hit (h) or Stand (s)"
            print(BG_COLOR + "-" * term.width)
            print(BG_COLOR + term.center(hint, term.width))

    def run(self):
        player_busts = False

        self.dealer.cards = self.deck.deal(2)
        self.player.cards += self.deck.deal(2)

        self.print_hands()

        while True:
            with term.cbreak():
                choice = term.inkey().lower()

                match choice:
                    case "h":
                        new_card = self.deck.deal(1)[0]
                        self.player.cards.append(new_card)

                        self.print_hands()

                        evaluation = Blackjack.evaluate_hand(self.player.cards)

                        if evaluation > 21:
                            player_busts = True
                            break
                    case "s":
                        break

        while (
            evaluation := Blackjack.evaluate_hand(self.dealer.cards) < 17
            and not player_busts
        ):
            new_card = self.deck.deal(1)[0]
            self.dealer.cards.append(new_card)
            self.print_hands(True)

            sleep(0.7)  # Add a short delay for better user experience

            if evaluation > 21:
                break

        self.print_hands(True)

        final_dealer_value = Blackjack.evaluate_hand(self.dealer.cards)
        final_player_value = Blackjack.evaluate_hand(self.player.cards)

        with term.location(0, term.height - 2):
            if not player_busts and (
                final_player_value > final_dealer_value or final_dealer_value > 21
            ):
                payout = self.bet * 2
                self.player.player.money += payout
                print(
                    term.center(
                        BG_COLOR
                        + term.italic(
                            f"{self.player.player.name} wins ${payout} and now has ${self.player.player.money:.2f}."
                        ),
                        fillchar=BG_COLOR + " ",
                    ),
                    end="",
                )
            elif final_player_value == final_dealer_value:
                print(
                    term.center(
                        BG_COLOR
                        + term.italic(
                            f"{self.player.player.name} ties with the dealer and gets back their bet of ${self.bet:.2f}."
                        ),
                        fillchar=BG_COLOR + " ",
                    ),
                    end="",
                )
                self.player.player.money += self.bet
            else:
                print(
                    term.center(
                        BG_COLOR
                        + term.italic(
                            f"{self.player.player.name} loses the bet of ${self.bet:.2f} and now has ${self.player.player.money:.2f}."
                        ),
                        fillchar=BG_COLOR + " ",
                    ),
                    end="",
                )

            print(
                term.center("Press any key to return to the menu..."),
                end="",
                flush=True,
            )

            with term.cbreak():
                term.inkey()

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

    def print_hands(self, show_dealer_card: bool = False):
        player_cards_str = "  ".join(str(card) for card in self.player.cards)
        dealer_cards_str = "  ".join(
            str(card) if show_dealer_card or card != self.dealer.cards[0] else "??"
            for card in self.dealer.cards
        )

        Blackjack.draw_hand(
            term.width // 3,
            term.height // 2 - 2,
            player_cards_str,
            self.player.player.name,
        )
        Blackjack.draw_hand(
            term.width * 2 // 3, term.height // 2 - 2, dealer_cards_str, "Dealer"
        )

    def draw_hand(x: int, y: int, cards_str: str, label: str):
        # 1. Draw the cards
        with term.location(x, y):
            print(BG_COLOR + cards_str, end="")
            print(term.move_down, end="")

        # 2. Draw the label centered under the cards
        # We calculate the center based on the length of the cards string
        with term.location(x, y + 1):
            print(
                BG_COLOR
                + term.center(term.italic(label), len(cards_str), BG_COLOR + " "),
                end="",
            )
