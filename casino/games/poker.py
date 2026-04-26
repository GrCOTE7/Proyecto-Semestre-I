from casino.games import Game, Area
from utils.terminal import term, BG_COLOR
from utils.cards import Deck, Card, Rank
from casino.player import Player
from dataclasses import dataclass
import time
import random
from itertools import combinations
from enum import Enum, IntEnum
from collections import Counter


@dataclass
class PokerPlayer:
    player: Player
    cards: list[Card]


class Action(Enum):
    FOLD = "f"
    CALL = "c"
    RAISE = "r"


class HandRank(IntEnum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9


class CardRank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Poker(Game):
    # The deck used in the game
    deck: Deck

    # The community cards on the table (the 5 cards that all players can use to make their hand)
    community_cards: list[Card]

    # All the cpus in the game
    cpus: list[PokerPlayer]
    # The human player in the game
    player: PokerPlayer

    # List of all active players in the current hand (those who haven't folded)
    active_players: list[PokerPlayer]

    # The index of the player whose turn it is currently
    current_player_idx: int
    # The index of the dealer (the player who is currently the dealer, which rotates each hand)
    dealer_idx: int

    # The big blind amount (for simplicity, we set it as a percentage of the player's money)
    big_blind: float
    # The total amount of money in the pot for the current hand
    pot: float

    # The current bet amount that players need to call to stay in the hand (starts at big blind and increases with raises)
    current_bet: float

    # A player must raise by at least the amount of the previous bet or raise in that same round.
    last_raise: float

    def __init__(self, player: Player):
        super().__init__("Poker")

        self.player = PokerPlayer(player, [])
        self.cpus = [PokerPlayer(Player(f"CPU {i+1}"), []) for i in range(5)]
        self.active_players = self.all_players

        self.deck = Deck()
        self.community_cards = []

        self.game_area = Area(
            0,
            self.header_area.y + self.header_area.height,
            term.width * 2 // 3,
            term.height - self.header_area.height - self.hint_area.height,
        )
        self.player_data_area = Area(
            term.width * 2 // 3,
            self.header_area.y + self.header_area.height,
            term.width - term.width * 2 // 3,
            term.height - self.header_area.height - self.hint_area.height,
        )

        self.big_blind = player.money * 0.05
        self.pot = 0

        self.current_bet = self.big_blind
        self.last_raise = self.big_blind

    @property
    def all_players(self):
        """Returns a list of all players in the game, with the human player first followed by the CPUs."""
        return [self.player] + self.cpus

    def start(self):
        super().start()

        self.print_player_data()
        self.choose_dealer()
        self.current_player_idx = (self.dealer_idx + 1) % len(self.all_players)

    def run(self):
        # Reset all game state for the new hand
        self.deck = Deck()
        self.community_cards = []
        self.active_players = self.all_players
        self.pot = 0
        self.last_raise = 0
        self.big_blind = self.player.player.money * 0.05
        self.current_bet = self.big_blind

        for player in self.all_players:
            player.cards = self.deck.deal(2)

        self.community_cards = self.deck.deal(5)
        self.print_game_area()

        # Post blinds at beggining of hand
        for i in range(2):
            blind = self.big_blind / (2 - i + 1)
            self.current_player.player.money -= blind  # Small blind is half the big blind, and the first player to act pays it
            self.pot += blind

            self.show_hint(
                f"{self.current_player.player.name} pays {'small' if i == 0 else 'big'} blind of ${blind:.2f}"
            )
            self.advance_turn()
            self.update_screen()
            time.sleep(2)  # Pause a moment between each blind for better visualization

        # To track how many players have called in the current betting round
        call_count = 0
        community_cards_revealed = 0
        while True:
            if (
                call_count >= len(self.active_players)
                or all(player.player.money == 0 for player in self.active_players)
                or len(self.active_players) == 1
            ):
                # Move to the next stage of the hand after everyone has called
                call_count = 0

                # Reveal the flop after first hand and then reveal one by one
                if community_cards_revealed == 0:
                    community_cards_revealed = 3
                else:
                    community_cards_revealed += 1

                if (
                    community_cards_revealed == 5
                    or len(self.active_players) == 1
                    or all(player.player.money == 0 for player in self.active_players)
                ):
                    # All community cards are revealed, only one player remains or everyone is all-in, end the hand
                    break

            # Skip inactive players (those who have folded) or those whove gone all in
            if (
                self.current_player not in self.active_players
                or self.current_player.player.money == 0
            ):
                self.advance_turn()
                self.update_screen(community_cards_revealed)
                continue

            # User action
            if self.current_player == self.player:
                action = self.player_input()

                match action:
                    case Action.FOLD:
                        self.active_players.remove(self.current_player)

                        self.show_hint(f"{self.current_player.player.name} folds")
                    case Action.CALL:
                        payment = min(
                            self.current_bet, self.current_player.player.money
                        )

                        self.pot += payment
                        self.current_player.player.money -= payment

                        # Only count as a call if the player is actually calling the current bet,
                        # and not just going all-in with a smaller amount
                        if payment == self.current_bet:
                            call_count += 1

                        self.show_hint(f"{self.current_player.player.name} calls")
                    case Action.RAISE:
                        new_bet = self.input_raise()
                        self.pot += new_bet

                        # If the player goes all-in with a raise that is less than the minimum raise, we still allow it
                        # but we don't update the last_raise amount, so that the next player's minimum raise is still
                        # based on the previous valid raise.
                        if (
                            new_bet == self.player.player.money
                            and new_bet >= self.current_bet + self.min_raise
                        ):
                            self.raise_bet(new_bet)
                            call_count = 0

                        self.current_player.player.money -= new_bet

                        if self.current_player.player.money == 0:
                            self.show_hint(
                                f"{self.current_player.player.name} goes all-in!"
                            )
                        else:
                            self.show_hint(
                                f"{self.current_player.player.name} raises to ${new_bet:.2f}"
                            )
            else:
                # CPU action
                self.show_hint(f"{self.current_player.player.name} is thinking...")
                time.sleep(random.uniform(1.5, 3.0))

                cpu_action = self.cpu_choice(self.current_player)

                match cpu_action:
                    case Action.CALL:
                        # Call the current bet
                        payment = min(
                            self.current_bet, self.current_player.player.money
                        )

                        self.pot += payment
                        self.current_player.player.money -= payment

                        # Only count as a call if the player is actually calling the current bet,
                        # and not just going all-in with a smaller amount
                        if payment == self.current_bet:
                            call_count += 1

                        self.show_hint(f"{self.current_player.player.name} calls")
                    case Action.RAISE:
                        min_bet = self.current_bet + self.min_raise
                        max_bet = self.current_player.player.money

                        # Clamp the random bet between the minimum raise and the maximum the CPU can afford, and round to 2 decimals
                        bet = min(
                            round(random.triangular(min_bet, max_bet, min_bet), 2),
                            max_bet,
                        )

                        self.current_player.player.money -= bet

                        if bet >= min_bet:
                            # Only update the current bet and last raise if the raise is valid (meets the minimum raise requirement),
                            # or if the player is going all-in with a raise that is greater than the minimum
                            # raise. If the player is going all-in with a raise that is less than the minimum raise, we allow it
                            # but we don't update the current bet or last raise, so that the next player's
                            # minimum raise is still based on the previous valid raise.
                            self.raise_bet(bet)
                            call_count = 0

                        if self.current_player.player.money == 0:
                            self.show_hint(
                                f"{self.current_player.player.name} goes all-in!"
                            )
                        else:
                            self.show_hint(
                                f"{self.current_player.player.name} raises to {bet}$"
                            )
                    case Action.FOLD:
                        self.active_players.remove(self.current_player)
                        self.show_hint(f"{self.current_player.player.name} folds")

            self.advance_turn()
            self.update_screen(community_cards_revealed)

            time.sleep(2)

        # The best hand of each active player is evaluated using their hole cards and the community cards,
        # and the winner(s) is determined based on who has the highest hand.
        final_hands: list[tuple[PokerPlayer, tuple[HandRank, list[CardRank]]]] = [
            (player, Poker.best_hand(player.cards, self.community_cards))
            for player in self.active_players
        ]

        print(
            [
                f"{player.player.name}: {hand[0].name}, tie-breaker: {hand[1]}"
                for player, hand in final_hands
            ]
        )
        time.sleep(10)

        # 1. Find the maximum score achieved at the table
        # We use the second element of the tuple (the hand score) for comparison
        max_score = max(final_hands, key=lambda x: x[1])[1]

        # 2. Identify all players who hold that max score
        winners = [player for player, score in final_hands if score == max_score]

        if winners:
            split_pot = self.pot / len(winners)
            for winner in winners:
                winner.player.money += split_pot

        self.print_game_area(community_cards=5, show_hands=True)

        if len(winners) == 1:
            self.show_hint(
                f"Game over. Winner: {winners[0].player.name} with {final_hands[0][1][0].name.replace('_', ' ').title()}! Press N to start a new game or Q to quit."
            )
        else:
            self.show_hint(
                f"Game over. It's a tie between: {', '.join(winner.player.name for winner in winners)} with {final_hands[0][1][0].name.replace('_', ' ').title()}! Press N to start a new game or Q to quit."
            )

    def end(self):
        with term.cbreak():
            while True:
                key = term.inkey().lower()
                if key == "n":
                    self.__init__(
                        self.player.player
                    )  # Reset the game with the same player

                    self.dealer_idx = (self.dealer_idx + 1) % len(
                        self.all_players
                    )  # Rotate dealer for next hand
                    self.run()
                    break
                elif key == "q":
                    self.show_hint("Thanks for playing! Press any key to exit.")
                    term.inkey()
                    break

    def choose_dealer(self):
        """Randomly selects a dealer from all players (including the human player) with a spinning wheel effect."""
        possible_dealers = [self.player] + self.cpus
        dealer_index = 0

        with term.location(0, 4):
            print(
                BG_COLOR
                + term.center(
                    "Dealer will be choosen randomly from all players: ",
                    self.game_area.width,
                )
            )

        # Start with a very small delay (fast)
        delay = 0.05
        # How much the delay increases each step (the "friction")
        friction = random.uniform(1.1, 1.3)
        max_delay = 0.6

        while delay < max_delay:
            # Move to the next item in the array
            dealer_index = (dealer_index + 1) % len(possible_dealers)

            with term.location(0, 6):
                # Print the current dealer candidate centered
                print(
                    BG_COLOR
                    + term.center(
                        possible_dealers[dealer_index].player.name, self.game_area.width
                    ),
                    end="",
                    flush=True,
                )

            # Wait, then slow down
            time.sleep(delay)
            delay *= friction

        self.dealer_idx = dealer_index

        with term.location(0, 6):
            # Print the current dealer candidate centered
            print(
                BG_COLOR
                + term.center(
                    "Dealer: " + self.dealer.player.name, self.game_area.width
                ),
                end="",
                flush=True,
            )
        time.sleep(1.5)  # Pause a moment on the final dealer

    @property
    def dealer(self) -> PokerPlayer:
        """Returns the current dealer."""
        return self.all_players[self.dealer_idx]

    @property
    def current_player(self) -> PokerPlayer:
        """Returns the current player."""
        return self.all_players[self.current_player_idx]

    def advance_turn(self):
        """Advances the turn to the next player."""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.all_players)

    def print_player_data(self):
        """
        Prints the player data (name and money) in the right area of the screen,
        with the human player at the top
        and the CPUs below, and the big blind amount and pot at the bottom.
        """

        data_area_x = self.player_data_area.x + 1

        for y in range(
            self.player_data_area.y,
            self.player_data_area.y + self.game_area.height,
        ):
            with term.location(self.player_data_area.x, y):
                print(BG_COLOR + "|", end="")

        with term.location(data_area_x, self.player_data_area.y + 1):
            print(
                BG_COLOR
                + term.bold
                + term.center(
                    "Players data",
                    self.player_data_area.width,
                ),
                end="",
            )

        with term.location(data_area_x, self.player_data_area.y + 3):
            print(
                BG_COLOR
                + term.center(
                    f"{term.bold} {self.player.player.name} (${self.player.player.money:.2f}) {term.normal}",
                    self.player_data_area.width,
                    fillchar=BG_COLOR + " ",
                ),
                end="",
            )
        for i, cpu in enumerate(self.cpus):
            with term.location(data_area_x, self.player_data_area.y + 4 + i):
                print(
                    BG_COLOR
                    + term.center(
                        f"CPU {i+1} (${cpu.player.money:.2f})",
                        self.player_data_area.width,
                        fillchar=BG_COLOR + " ",
                    ),
                    end="",
                )

        game_data_y = self.player_data_area.y + 4 + len(self.cpus) + 1
        with term.location(data_area_x, game_data_y + 1):
            print(
                BG_COLOR
                + term.center(
                    f"Big Blind: ${self.big_blind:.2f}",
                    self.player_data_area.width,
                    fillchar=BG_COLOR + " ",
                ),
                end="",
            )

        with term.location(data_area_x, game_data_y + 2):
            print(
                BG_COLOR
                + term.center(
                    f"Current bet: ${self.current_bet:.2f}",
                    self.player_data_area.width,
                    fillchar=BG_COLOR + " ",
                ),
                end="",
            )

        with term.location(data_area_x, game_data_y + 3):
            print(
                BG_COLOR
                + term.center(
                    f"Pot: ${self.pot:.2f}",
                    self.player_data_area.width,
                    fillchar=BG_COLOR + " ",
                ),
                end="",
            )

    def print_game_area(self, community_cards: int = 0, show_hands: bool = False):
        """
        Prints the game area, including the players' hands and the community cards.
        The human player's hand is always shown, while the CPUs' hands are hidden until revealed.
        The dealer is indicated with a bold label, and the small blind and big blind are also
        indicated next to the respective players.
        """

        with term.hidden_cursor():
            Game.clear_area(self.game_area)

            with term.location(self.game_area.x, self.game_area.y):

                # Print first 3 players above the community cards
                for i, player in enumerate(self.all_players[:3]):
                    player_active = player in self.active_players

                    cards_str = (
                        "  ".join(str(card) for card in player.cards)
                        if player == self.player or show_hands
                        else "??  ??"
                    )

                    Poker.print_hand(
                        self.game_area.x + (i + 1) * self.game_area.width // 4,
                        self.game_area.y + self.game_area.height // 2 - 3,
                        (term.red + cards_str if not player_active else cards_str),
                        f"{term.red if not player_active else ''}{player.player.name}{'(D)' if player == self.dealer else ''}{'(SB)' if player == self.all_players[(self.dealer_idx + 1) % len(self.all_players)] else ''}{'(BB)' if player == self.all_players[(self.dealer_idx + 2) % len(self.all_players)] else ''}",
                        bold=player == self.current_player,
                    )

                with term.location(
                    self.game_area.x, self.game_area.y + self.game_area.height // 2
                ):

                    print(
                        BG_COLOR
                        + term.center(
                            "Community Cards: "
                            + "  ".join(
                                [
                                    str(card)
                                    for card in self.community_cards[:community_cards]
                                ]
                            ),
                            self.game_area.width,
                        ),
                        end="",
                    )

                # Print last 3 players below the community cards (in reverse order to cycle clockwise through them)
                for i, player in enumerate(self.all_players[3:][::-1]):
                    cards_str = (
                        "  ".join(str(card) for card in player.cards)
                        if player == self.player or show_hands
                        else "??  ??"
                    )

                    Poker.print_hand(
                        self.game_area.x + (i + 1) * self.game_area.width // 4,
                        self.game_area.y + self.game_area.height // 2 + 3,
                        (
                            term.red + cards_str
                            if player not in self.active_players
                            else cards_str
                        ),
                        f"{term.red if player not in self.active_players else ''}{player.player.name}{'(D)' if player == self.dealer else ''}{'(SB)' if player == self.all_players[(self.dealer_idx + 1) % len(self.all_players)] else ''}{'(BB)' if player == self.all_players[(self.dealer_idx + 2) % len(self.all_players)] else ''}",
                        bold=player == self.current_player,
                    )

    def update_screen(self, community_cards: int = 0):
        self.print_player_data()
        self.print_game_area(community_cards)

    @staticmethod
    def print_hand(x: int, y: int, cards_str: str, label: str, bold: bool = False):
        """
        Utility function to print a player's hand at a specific location, with the cards and a label
        centered under the cards.
        Label should be bold for current player.
        """
        # 1. Draw the cards
        with term.location(x, y):
            print(BG_COLOR + cards_str, end="")
            print(term.move_down, end="")

        # 2. Draw the label centered under the cards
        # We calculate the center based on the length of the cards string
        with term.location(x, y + 1):
            label = term.italic(label)
            label = term.bold(label) if bold else label

            print(
                (BG_COLOR + term.center(label, len(cards_str), BG_COLOR + " ")),
                end="",
            )

    def player_input(self) -> Action:
        self.show_hint("Your turn! (Fold (F), Call (C), Raise (R))")

        while True:
            with term.cbreak():
                key = term.inkey().lower()
                try:
                    return Action(key)
                except ValueError:
                    # Keep looping until a valid key is pressed
                    continue

    def input_raise(self) -> float:
        """
        Prompts the player to input a raise amount, ensuring that it is a valid number and meets the minimum raise requirement.
        """
        amount = ""

        min_bet = self.current_bet + self.min_raise
        max_bet = self.player.player.money

        msg = f"Enter new bet (min: ${min_bet:.2f} max: ${max_bet:.2f}):"

        self.show_hint(msg)

        while True:
            with term.cbreak():
                key = term.inkey()
                if key.isdigit() or (key == "." and "." not in amount):
                    amount += key
                    self.show_hint(msg + " $" + amount)
                elif key.name == "KEY_BACKSPACE":
                    amount = amount[:-1]
                    self.show_hint(msg + f" ${amount}" if amount else msg)
                elif key.name == "KEY_ENTER":
                    float_amount = float(amount)
                    # Valid bets are between min and max bets or all-in (even if all in is less than min bet)
                    if (
                        float_amount >= min_bet and float_amount <= max_bet
                    ) or float_amount == max_bet:
                        return float_amount

    def raise_bet(self, new_bet: float):
        """
        Raises the game's bet to the new bet amount, and updates the last raise amount accordingly.
        This method should be called whenever a player raises, to ensure that the minimum raise amount is correctly calculated for
        subsequent raises.
        """
        self.last_raise = new_bet - self.current_bet
        self.current_bet = new_bet

    @property
    def min_raise(self) -> float:
        """Returns the minimum raise amount based on the last raise."""
        return self.last_raise

    @staticmethod
    def evaluate_hand(hand: list[Card]) -> tuple[HandRank, list[CardRank]]:
        """
        Evaluates a 5-card poker hand and returns a tuple containing the hand rank (e.g., pair, flush, straight)
        and a list of card ranks for tie-breaking purposes.
        The returned hand is comparable, meaning that a higher hand rank will always beat a lower one,
        and if two hands have the same rank, the tie-breaker list can be compared in order to determine the winner
        (e.g., for two pairs, the tie-breaker list would contain the ranks of the pairs and then the kicker).
        """
        # Sort ranks in descending order for easier evaluation of straights and high cards, and extract suits
        ranks = sorted([CardRank[c.rank.name] for c in hand], reverse=True)
        # The suits of all cards in the hand, used to check for flushes
        suits = [c.suit for c in hand]

        # Count the frequency of each rank in the hand, which is essential for identifying pairs, three of a kind, and four of a kind.
        counts = Counter(ranks)

        # Build a normalized 5-card comparison vector where duplicated ranks come first.
        # Examples:
        # - Pair: [pair, pair, kicker1, kicker2, kicker3]
        # - Two pair: [high_pair, high_pair, low_pair, low_pair, kicker]
        # - Trips: [trips, trips, trips, kicker1, kicker2]
        grouped_ranks = sorted(
            counts.items(), key=lambda item: (item[1], item[0]), reverse=True
        )
        score_sort = [rank for rank, freq in grouped_ranks for _ in range(freq)]

        is_flush = len(set(suits)) == 1
        is_straight = len(set(ranks)) == 5 and (max(ranks) - min(ranks) == 4)

        # Wheel Straight (A-5)
        if set(ranks) == {
            CardRank.ACE,
            CardRank.TWO,
            CardRank.THREE,
            CardRank.FOUR,
            CardRank.FIVE,
        }:
            is_straight = True
            score_sort = [
                CardRank.FIVE,
                CardRank.FOUR,
                CardRank.THREE,
                CardRank.TWO,
                CardRank.ACE,
            ]  # Ace is low in this straight

        # Return (HandRank, Tie-breaker-list)
        if is_straight and is_flush:
            return (
                (
                    HandRank.ROYAL_FLUSH
                    if score_sort[0] == CardRank.ACE
                    else HandRank.STRAIGHT_FLUSH
                ),
                score_sort,
            )

        hand_type = HandRank.HIGH_CARD

        if 4 in counts.values():
            hand_type = HandRank.FOUR_OF_A_KIND
        elif 3 in counts.values() and 2 in counts.values():
            hand_type = HandRank.FULL_HOUSE
        elif is_flush:
            hand_type = HandRank.FLUSH
        elif is_straight:
            hand_type = HandRank.STRAIGHT
        elif 3 in counts.values():
            hand_type = HandRank.THREE_OF_A_KIND
        elif list(counts.values()).count(2) == 2:
            hand_type = HandRank.TWO_PAIR
        elif 2 in counts.values():
            hand_type = HandRank.PAIR

        return (hand_type, score_sort)

    @staticmethod
    def best_hand(
        player_cards: list[Card], community_cards: list[Card]
    ) -> tuple[HandRank, list[CardRank]]:
        """
        Returns the best 5-card hand that can be made from 2 player cards and 5 community cards.

        The returned tuple is:
        - hand_score: (HandRank, tie_breaker_vector i.e. best hand) as produced by evaluate_hand
        """
        if len(player_cards) != 2:
            raise ValueError("best_hand expects exactly 2 player cards")
        if len(community_cards) != 5:
            raise ValueError("best_hand expects exactly 5 community cards")

        seven_cards = player_cards + community_cards

        best_five: list[Card] | None = None
        best_score: tuple[HandRank, list[CardRank]] | None = None

        for five_cards_tuple in combinations(seven_cards, 5):
            five_cards = list(five_cards_tuple)
            score = Poker.evaluate_hand(five_cards)

            if best_score is None or score > best_score:
                best_score = score
                best_five = five_cards

        # Guaranteed by combinations(7, 5), kept explicit for type-safety.
        if best_five is None or best_score is None:
            raise ValueError("Could not evaluate best hand")

        return best_score

    def cpu_choice(self, cpu: PokerPlayer) -> Action:
        """
        Determines the CPU's action (fold, call, or raise) based on a simple heuristic that considers the current bet and the CPU's money.
        The CPU will randomly choose to fold, call, or raise, but it will only choose to raise if it can afford at
        least the minimum raise.
        """
        min_bet = self.current_bet + self.min_raise

        if cpu.player.money < min_bet:
            # If the CPU can't afford to call the current bet, it will fold or go all-in (which is treated as a raise)
            return random.choice([Action.FOLD, Action.RAISE])

        return random.choice([Action.FOLD, Action.CALL, Action.RAISE])
