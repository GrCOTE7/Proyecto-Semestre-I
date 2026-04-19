from casino.player import Player
from casino.games import Game
from casino.games.blackjack import Blackjack

from utils import terminal
from utils.terminal import term, BG_COLOR


class Casino:
    """
    A class representing a casino, which can have multiple players.
    """

    name: str
    players: list[Player]
    games: list[Game]
    games_area: int
    profile_area: int

    def __init__(self, name: str):
        self.name = name
        self.players = []
        self.games = [Blackjack]

        self.games_area = term.width * 2 // 3  # The area where games are listed

    def add_player(self, player: Player):
        self.players.append(player)

    def remove_player(self, player: Player):
        if player in self.players:
            self.players.remove(player)

    def list_players(self):
        return [player.name for player in self.players]

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
                        selected_game: Game = self.games[game_index](self.players[0])
                        selected_game.start()
                        selected_game.run()
                        selected_game.end()
                elif choice.lower() == "q":
                    print(term.clear)
                    break

    def __str__(self):
        return f"Casino: {self.name}, Players: {', '.join(self.list_players())}"

    def games_area_menu(self):
        with term.location(0, 2):
            print(
                BG_COLOR
                + term.center(
                    f"Welcome to {self.name} Casino!", self.games_area, fillchar="-"
                )
            )
            print("")
            print(BG_COLOR + term.center("Available games:", self.games_area))
            for idx, game in enumerate(self.games, start=1):
                print(
                    BG_COLOR + term.center(f"{idx}. {game.__name__}", self.games_area)
                )

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
                + term.center(
                    f"{self.players[0].name}: ${self.players[0].money}", profile_area
                )
            )
