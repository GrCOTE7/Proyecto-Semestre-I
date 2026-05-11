from casino.games.blackjack.renderer import BlackjackTerminalRenderer
from casino.player import PlayerController
from casino.games.blackjack.blackjack import Blackjack, BlackjackManager
from casino.games.poker.poker import Poker, PokerManager
from casino.games.poker.renderer import PokerRenderer
from casino.games.game_manager import GameManager
from casino.games import Game
from dataclasses import dataclass
from utils.renderer import Renderer
from .games.generic_events import GenericEvent

from typing import Type


@dataclass
class CasinoGame:
    name: str
    game: Type[Game]
    manager: Type[GameManager]
    renderer: Type[Renderer]


class Casino:
    """
    A class representing a casino, which can have multiple players.
    """

    name: str
    player: PlayerController
    games: list[CasinoGame]
    game_active: bool

    def __init__(self, name: str, player: PlayerController):
        self.name = name
        self.player = player
        self.game_active = False

        self.games = [
            CasinoGame(
                name="Blackjack",
                game=Blackjack,
                manager=BlackjackManager,
                renderer=BlackjackTerminalRenderer,
            ),
            CasinoGame(
                name="Poker", game=Poker, manager=PokerManager, renderer=PokerRenderer
            ),
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

                # The actual instances of the games are created here, after the player has made their choice.
                # This allows us to subscribe to game events before the game loop starts.
                game = selected_game.game(player=self.player)
                _ = selected_game.renderer(game)
                manager = selected_game.manager(game)

                game.subscribe(GenericEvent.GAME_END, self.end_game)

                # Run game setup code before accepting player input
                game.start()

                self.game_active = True
                while self.game_active:
                    available_commands = manager.get_available_commands()
                    for key, cmd in available_commands.items():
                        print(f"{key}: {cmd.description}")

                    manager.handle_input(input("Enter your action: "))
            except (IndexError, ValueError):
                print("Invalid choice. Please try again.")

    def end_game(self):
        self.game_active = False
