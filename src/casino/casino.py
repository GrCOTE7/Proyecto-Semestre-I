import uuid

from casino.games.blackjack.renderer import BlackjackTerminalRenderer
from casino.player import PlayerAccount
from casino.games.blackjack.blackjack import Blackjack
from casino.games.poker.poker import Poker, PokerManager
from casino.games.poker.renderer import PokerRenderer
from casino.games.game_manager import GameManager
from casino.games import Game
from dataclasses import dataclass
from utils.renderer import Renderer
from .games.generic_events import GenericEvent
from utils.commands.command_manager import CommandManager
from utils.event_listener import EventBus
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
    player: PlayerAccount
    games: list[CasinoGame]
    game_active: bool

    def __init__(self, name: str):
        self.name = name
        self.game_active = False

        self.games = [
            CasinoGame(
                name="Blackjack",
                game=Blackjack,
                manager=GameManager,
                renderer=BlackjackTerminalRenderer,
            ),
            # CasinoGame(
            #     name="Poker", game=Poker, manager=PokerManager, renderer=PokerRenderer
            # ),
        ]

        self.player = PlayerAccount(id=uuid.uuid4(), name="Player1", balance=1000)

    def menu(self):
        while True:
            print(f"Welcome to {self.name}!")
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
                manager = selected_game.manager(
                    selected_game.game,
                    self.player,
                    selected_game.renderer,
                    self.player.buy_in(100),
                )  # Example buy-in amount

                manager.event_bus.subscribe(GenericEvent.GAME_END, self.end_game)

                # Run game setup code before accepting player input
                manager.game.start()

                self.game_active = True
                while self.game_active:
                    if manager.player.is_my_turn:
                        choice = input("\nSelect an option: ")

                        try:
                            choice = int(choice) - 1
                            manager.player.handle_input(choice)
                        except ValueError:
                            print(
                                "Invalid input. Please enter a number corresponding to the available options."
                            )
            except (IndexError, ValueError):
                print("Invalid choice. Please try again.")

    def end_game(self, payout: float):
        self.game_active = False
        # Only update the player's balance if they won or lost money. If payout is <= 0, it means the player tied or lost.
        # Not withdrawing from the player balance in case of lost since the payout removes the bet amount from the balance,
        # and we don't want to double charge the player.
        if payout > 0:
            self.player.deposit(payout)
