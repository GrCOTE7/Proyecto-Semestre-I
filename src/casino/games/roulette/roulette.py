from casino.games import Game, Snapshot
from casino.games.game_manager import GameManager
from casino.games.generic_events import GenericEvent
from utils.event_listener import EventBus
from casino.player import PlayerBuyIn, PlayerView
from dataclasses import dataclass
from casino.games.roulette import bets
from casino.games.roulette.events import RouletteEvents
from utils.commands.command import CommandSchema, CommandParameter
from casino.games.roulette import commands
from casino.games.roulette.cells import Color, RouletteCell

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from casino.games.roulette.renderer import Renderer

from uuid import UUID
from enum import Enum
import random
from typing import Dict

class RouletteManager(GameManager):
    def __init__(
        self,
        game: Roulette,
        event_bus: EventBus,
        renderer: Renderer,
        buyin: PlayerBuyIn,
    ):
        super().__init__(game, event_bus, renderer, buyin)


@dataclass
class RoulettePlayer:
    id: UUID
    name: str
    funds: float = 0

    def to_view(self) -> RoulettePlayerView:
        return RoulettePlayerView(id=self.id, name=self.name, funds=self.funds)

@dataclass(frozen=True)
class RoulettePlayerView(PlayerView):
    funds: float


@dataclass(frozen=True)
class RouletteSnapshot(Snapshot):
    active_player: RoulettePlayerView
    bets: Dict[str, bets.RouletteBet]
    """A list of all bets currently placed on the table."""
    wheel: tuple[RouletteCell]
    """The table's wheel"""
    payouts: list[bets.RouletteBet]
    """List of winning bets from the last spin."""
    landing_cell: RouletteCell | tuple[RouletteCell, RouletteCell] | None
    """
    `landing_cell` will be a single RouletteCell if the ball landed clearly in one pocket, 
    or a tuple of two RouletteCells if it landed on the edge between them. It will be None if the wheel hasn't been spun yet.
    """
    available_commands: list[CommandSchema]
    """List of available commands for the player in the current game state."""


CELLS = 36
DEGREES_PER_POCKET = 360 / CELLS  # 36 pockets including 0
EDGE_THRESHOLD = 0.4 # If within 0.4 degrees of a border, it's on the edge

class Roulette(Game):
    wheel: tuple[RouletteCell]
    bets: Dict[str, bets.RouletteBet]
    player: RoulettePlayer
    payouts: list[bets.RouletteBet]  # List of winning bets from the last spin
    landing_cell: RouletteCell | tuple[RouletteCell, RouletteCell] | None = None

    def __init__(self, event_bus: EventBus, buyin: PlayerBuyIn):
        super().__init__(event_bus, buyin)
        self.wheel = Roulette.create_wheel()
        self.bets = {}
        self.payouts = []
        self.player = RoulettePlayer(id=buyin.player_id, name=buyin.name, funds=buyin.amount)
    
    def start(self):
        self.event_bus.notify(RouletteEvents.PLAYER_TURN_START, self.get_snapshot())
        self.event_bus.notify(GenericEvent.TURN_START, self.player.to_view())

    def get_pocket_color(number: int) -> Color:
        """Determines the color of a roulette pocket based on its number."""
        if number == 0:
            return Color.GREEN
        
        # Ranges 1-10 and 19-28: Odd is Red, Even is Black
        if (1 <= number <= 10) or (19 <= number <= 28):
            return Color.RED if number % 2 != 0 else Color.BLACK
            
        # Ranges 11-18 and 29-36: Odd is Black, Even is Red
        if (11 <= number <= 18) or (29 <= number <= 36):
            return Color.BLACK if number % 2 != 0 else Color.RED
        
        raise ValueError(value=f"Invalid roulette number: {number}")

    def create_wheel() -> tuple[RouletteCell]:
        """Creates a list of RouletteCell objects in the standard wheel sequence."""
        wheel_sequence = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10,
            5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
        ]
        
        return tuple(RouletteCell(number=num, color=Roulette.get_pocket_color(num)) for num in wheel_sequence)

    def place_bet(self, bet: bets.RouletteBet):
        """Places a bet on the table. The player must have sufficient funds to cover the bet amount, and the bet will be added to any existing bet of the same type on the table."""
        if bet.bet > self.player.funds:
            raise ValueError(f"Insufficient funds to place bet of ${bet.bet}. Current funds: ${self.player.funds}")

        key = bet.key

        if key in self.bets:
            self.bets[key].bet += bet.bet  # If the same bet already exists, just increase the amount
        else:
            self.bets[key] = bet

        self.player.funds -= bet.bet
        self.event_bus.notify(RouletteEvents.BET_PLACED, self.get_snapshot())
        self.event_bus.notify(RouletteEvents.PLAYER_TURN_START, self.get_snapshot())
        self.event_bus.notify(GenericEvent.TURN_START, self.player.to_view())

    def remove_bet(self, bet: bets.RouletteBet):
        """Removes a bet from the table, allowing the player to retrieve their funds. The bet must already exist on the table and the amount to remove cannot exceed the existing bet amount."""
        key = bet.key

        if key not in self.bets:
            raise ValueError("Bet not found on the table.")

        existing_bet = self.bets[key]

        if bet.bet > existing_bet.bet:
            raise ValueError(f"Cannot remove more than the existing bet amount of ${existing_bet.bet}.")

        existing_bet.bet -= bet.bet
        self.player.funds += bet.bet

        if existing_bet.bet == 0:
            del self.bets[key]

        self.event_bus.notify(RouletteEvents.BET_REMOVED, self.get_snapshot())
        self.event_bus.notify(RouletteEvents.PLAYER_TURN_START, self.get_snapshot())
        self.event_bus.notify(GenericEvent.TURN_START, self.player.to_view())

    def clear_bets(self):
        """Clears all bets from the table, allowing the player to retrieve all their funds."""
        total_refund = sum(bet.bet for bet in self.bets.values())
        self.player.funds += total_refund
        self.bets.clear()
        self.event_bus.notify(RouletteEvents.BET_REMOVED, self.get_snapshot())
        self.event_bus.notify(RouletteEvents.PLAYER_TURN_START, self.get_snapshot())
        self.event_bus.notify(GenericEvent.TURN_START, self.player.to_view())

    def spin_wheel(self):
        landing_degree = random.uniform(0, 360) # Random degree between 0 and 360

        # Determine which pocket index it's in
        pocket_index = int(landing_degree // DEGREES_PER_POCKET)

        # Find out exactly where inside that pocket the ball landed
        position_in_pocket = landing_degree % DEGREES_PER_POCKET
        
        current_cell = self.wheel[pocket_index]
        other_cell = None
    
        if position_in_pocket < EDGE_THRESHOLD:
            # On the edge with the previous pocket
            other_cell = self.wheel[(pocket_index - 1) % len(self.wheel)]
        elif position_in_pocket > (DEGREES_PER_POCKET - EDGE_THRESHOLD):
            # On the edge with the next pocket
            other_cell = self.wheel[(pocket_index + 1) % len(self.wheel)]

        self.landing_cell = (current_cell, other_cell) if other_cell else current_cell

        for bet in self.bets.values():
            # Check if the bet wins on either the current cell or the other cell (if on the edge)
            if bets.is_winning_bet(bet, current_cell) or (other_cell and bets.is_winning_bet(bet, other_cell)):
                self.player.funds += bet.earnings()
                self.payouts.append(bet)
        
        self.event_bus.notify(RouletteEvents.SPIN_RESULT, self.get_snapshot())

        # Clear data for the next round
        self.landing_cell = None
        self.payouts.clear()
        self.bets.clear()

        self.event_bus.notify(RouletteEvents.PLAYER_TURN_START, self.get_snapshot())
        self.event_bus.notify(GenericEvent.TURN_START, self.player.to_view())

    def end_round(self):
        self.event_bus.notify(GenericEvent.GAME_END, self.player.funds)

    def get_snapshot(self) -> RouletteSnapshot:
        return RouletteSnapshot(
            active_player=self.player.to_view(),
            bets=self.bets,
            wheel=self.wheel,
            payouts=self.payouts,
            landing_cell=self.landing_cell,
            available_commands=self.get_available_commands()
        )
    
    def get_available_commands(self):
        # todo run program a place bet
        comms = [
            CommandSchema(
                display_name="Place Bet",
                command_class=commands.PlaceBetCommand,
                parameters=[CommandParameter(name="bet", prompt_text="""Enter bet details (
- Straight: "Straight 17 50" for a $50 bet on number 17
- Split: "Split 17-20 30" for a $30 bet on the edge between 17 and 20
- Street: "Street 1-3 25" for a $25 bet on the row containing numbers 1, 2, and 3
- Corner: "Corner 1-2-4-5 20" for a $20 bet on the square containing numbers 1, 2, 4, and 5
- Line: "Line 1-6 15" for a $15 bet on the two rows containing numbers 1-6
- Dozen: "Dozen 1 100" for a $100 bet on the first dozen (1-12)
- Column: "Column 2 50" for a $50 bet on the second column (2,5,8,...35)
- Color: "Color Red 100" for a $100 bet on red
- Odd/Even: "OddEven Odd 50" for a $50 bet on odd numbers
- High/Low: "HighLow High 25" for a $25 bet on high numbers (19-36)
): """,
                                        parser=lambda input_str: bets.bet_from_string(input_str),
)]
            ),
            CommandSchema(
                display_name="Remove Bet",
                command_class=commands.RemoveBetCommand,
                parameters=[CommandParameter(name="bet", prompt_text="""Enter bet details (
- Straight: "Straight 17 50" for a $50 bet on number 17
- Split: "Split 17-20 30" for a $30 bet on the edge between 17 and 20
- Street: "Street 1-3 25" for a $25 bet on the row containing numbers 1, 2, and 3
- Corner: "Corner 1-2-4-5 20" for a $20 bet on the square containing numbers 1, 2, 4, and 5
- Line: "Line 1-6 15" for a $15 bet on the two rows containing numbers 1-6
- Dozen: "Dozen 1 100" for a $100 bet on the first dozen (1-12)
- Column: "Column 2 50" for a $50 bet on the second column (2,5,8,...35)
- Color: "Color Red 100" for a $100 bet on red
- Odd/Even: "OddEven Odd 50" for a $50 bet on odd numbers
- High/Low: "HighLow High 25" for a $25 bet on high numbers (19-36)
): """,
                                        parser=lambda input_str: bets.bet_from_string(input_str)
                                        )]
            ) if self.bets else None,  # Only show Remove Bet option if there are bets to remove
            CommandSchema(
                display_name="Spin Wheel",
                command_class=commands.SpinWheelCommand,
            ) if self.bets else None,  # Only allow spinning the wheel if there are bets placed
            CommandSchema(
                display_name="Clear Bets",
                command_class=commands.ClearBetsCommand,
            ) if self.bets else None,  # Only show Clear Bets option if there are bets to clear
            CommandSchema(
                display_name="Exit Game",
                command_class=commands.EndRoundCommand,
            )  
        ]


        return [command for command in comms if command]
