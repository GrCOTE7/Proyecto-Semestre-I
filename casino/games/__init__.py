from casino.player import Player
from utils.terminal import draw_bg, term, BG_COLOR
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum
from .generic_events import GenericEvent
from utils.event_listener import EventListener


@dataclass
class Area:
    """
    Represents a rectangular area on the terminal screen, defined by its top-left corner (x, y) and its width and height.
    """

    x: int
    y: int
    width: int
    height: int


class Game(EventListener):
    """
    A base class for all casino games, providing common functionality and structure.
    """

    header_area: Area
    game_area: Area
    hint_area: Area
    # A Finite State Machine. The current phase of the game, which can be used to manage game flow and logic.
    # This should be defined as an Enum in each specific game implementation.
    game_phase: Enum

    def __init__(self, name):
        self.name = name
        self.header_area = Area(0, 0, term.width, 3)
        self.game_area = Area(0, 3, term.width, term.height - 6)
        self.hint_area = Area(0, term.height - 3, term.width, 3)
        self.listeners = []

    @property
    @abstractmethod
    def active_player(self) -> Player:
        """Returns the currently active player in the game."""
        pass

    def change_phase(self, new_phase: Enum):
        """Changes the current game phase and notifies listeners of the phase change."""
        self.game_phase = new_phase
        self.notify(GenericEvent.PHASE_CHANGE, new_phase)

    def show_rules(self):
        raise NotImplementedError("Subclasses must implement the show_rules() method.")

    def show_hint(self, prompt: str):
        with term.location(self.hint_area.x, self.hint_area.y):
            print(BG_COLOR + "-" * self.hint_area.width, end="")
            print(BG_COLOR + term.center(prompt, self.hint_area.width), end="")

    @staticmethod
    def clear_area(area: Area):
        """Clears the specified area on the terminal screen by printing spaces over it."""
        with term.location(area.x, area.y):
            for _ in range(area.height):
                print(BG_COLOR + " " * area.width, end="")
                print(term.move_down, end="")
