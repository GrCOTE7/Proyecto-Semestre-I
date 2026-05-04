from casino.games.blackjack.renderer import BlackjackTerminalRenderer
from casino.player import Player
from casino.games.blackjack.blackjack import Blackjack, BlackjackManager
from casino.games.poker import Poker
from utils.commands.game_manager import GameManager
from dataclasses import dataclass
from utils.renderer import Renderer


@dataclass
class CasinoGame:
    name: str
    manager: GameManager
    renderer: Renderer


class Casino:
    """
    A class representing a casino, which can have multiple players.
    """

    name: str
    player: Player
    games: list[CasinoGame]

    def __init__(self, name: str, player: Player):
        self.name = name
        self.player = player

        blackjack = Blackjack(player)

        self.games = [
            CasinoGame(
                name="Blackjack",
                manager=BlackjackManager(blackjack),
                renderer=BlackjackTerminalRenderer(blackjack),
            ),
            # Poker,
        ]

    def menu(self):
        while True:
            print(f"Welcome to {self.name}, {self.player.name}!")
            print("Please select a game:")
            for idx, game in enumerate(self.games, start=1):
                print(f"{idx}. {game.name}")
            print("0. Exit")

            choice = input("Enter your choice: ")
            if choice == "0":
                print("Thank you for visiting the casino! Goodbye!")
                break

            try:
                selected_game = self.games[int(choice) - 1]
                while True:
                    for key, cmd in selected_game.manager.commands.items():
                        print(f"{key}: {cmd.description}")

                    selected_game.manager.handle_input(input("Enter your action: "))
            except (IndexError, ValueError):
                print("Invalid choice. Please try again.")
