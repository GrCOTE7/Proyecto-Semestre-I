from casino.player import Player
from casino.games import Game
from casino.games.blackjack import Blackjack

class Casino:
    """
    A class representing a casino, which can have multiple players.
    """

    name: str
    players: list[Player]
    games: list[Game]

    def __init__(self, name: str):
        self.name = name
        self.players = []
        self.games = [Blackjack]

    def add_player(self, player: Player):
        self.players.append(player)

    def remove_player(self, player: Player):
        if player in self.players:
            self.players.remove(player)

    def list_players(self):
        return [player.name for player in self.players]

    def menu(self):
        print(f"Welcome to {self.name}!")
        print("Available games:")
        for idx, game in enumerate(self.games, start=1):
            print(f"{idx}. {game.__name__}")

        choice = input("Select a game by entering its number: ")

        match choice:
            case '1':
                if not self.players:
                    print("No players available. Please add a player first.")
                    return
                player = self.players[0]  # For simplicity, we take the first playe
                bet = float(input(f"{player.name}, enter your bet: "))
                game_instance = Blackjack(player, bet)
                game_instance.start()
                game_instance.run()
                game_instance.end()
            case _:
                print("Invalid choice. Please select a valid game number.")

    def __str__(self):
        return f"Casino: {self.name}, Players: {', '.join(self.list_players())}"
