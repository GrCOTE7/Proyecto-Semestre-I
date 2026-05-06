from casino.games.blackjack.renderer import BlackjackTerminalRenderer
from casino.player import Player
from casino.games.blackjack.blackjack import Blackjack, BlackjackManager
from casino.games.poker import Poker
from utils.commands.game_manager import GameManager
from dataclasses import dataclass
from utils.renderer import Renderer
from .games.generic_events import GenericEvent


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
    game_active: bool

    def __init__(self, name: str, player: Player):
        self.name = name
        self.player = player
        self.game_active = False

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

                selected_game.manager.game.subscribe(
                    GenericEvent.GAME_END, self.end_game
                )

                self.game_active = True
                while self.game_active:
                    available_commands = selected_game.manager.get_available_commands()
                    for key, cmd in available_commands.items():
                        print(f"{key}: {cmd.description}")

                    selected_game.manager.handle_input(input("Enter your action: "))
            except (IndexError, ValueError):
                print("Invalid choice. Please try again.")

    def end_game(self):
        self.game_active = False
