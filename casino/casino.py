from casino.player import Player
from casino.games.blackjack import Blackjack
from casino.games.poker import Poker
from casino.games import Game

from utils import terminal
from utils.terminal import term, BG_COLOR


class Casino:
    """
    A class representing a casino, which can have multiple players.
    """

    name: str
    player: Player
    games: list[Game]
    games_area: int
    profile_area: int

    def __init__(self, name: str, player: Player):
        self.name = name
        self.player = player
        self.games = [
            Blackjack,
            Poker,
        ]

        self.games_area = term.width * 2 // 3  # The area where games are listed

    def menu(self):
        while True:
            print(term.clear())

            # Prints the checkered pattern background
            terminal.draw_bg()

            self.games_area_menu()
            self.profile_area_menu()

            with term.hidden_cursor():
                for y in range(term.height):
                    with term.location(self.games_area, y):
                        print(BG_COLOR + "|", end="")

            with term.location(0, term.height - 2):
                print(
                    BG_COLOR
                    + term.center(
                        "Enter the number of the game you want to play or 'Q' to quit",
                        self.games_area,
                    )
                )

            with term.cbreak():
                choice = term.inkey()

                if choice.isdigit():
                    game_index = int(choice) - 1
                    if 0 <= game_index < len(self.games):
                        print(term.clear())

                        selected_game: Game = self.games[game_index](self.player)
                        selected_game.start()
                        selected_game.run()
                        selected_game.end()
                elif choice.lower() == "q":
                    print(term.clear)
                    break

    def games_area_menu(self):
        game_strings = [f"{i+1}. {g.__name__}" for i, g in enumerate(self.games)]
        max_game_len = max(len(s) for s in game_strings) if game_strings else 0

        with term.location(0, 2):
            print(
                BG_COLOR
                + term.center(
                    f"Welcome to {self.name} Casino!", self.games_area, fillchar="-"
                ),
                end="",
            )
            print(term.move_down)
            print(BG_COLOR + term.center("Available games:", self.games_area))

            for s in game_strings:
                # First, pad the string to the max length (left-aligned)
                padded_game = s.ljust(max_game_len)

                # Second, center that full-width string in the games_area
                print(BG_COLOR + term.center(padded_game, self.games_area), end="")
                print(term.move_down, end="")

    def profile_area_menu(self):
        profile_area = term.width - self.games_area
        with term.location(self.games_area, 2):
            print(
                BG_COLOR + term.center("Player Profile", profile_area, fillchar="-"),
                end="",
            )

        with term.location(self.games_area, 4):
            print(
                BG_COLOR
                + term.center(f"{self.player.name}: ${self.player.money:.2f}", profile_area)
            )
