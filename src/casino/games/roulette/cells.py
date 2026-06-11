from enum import Enum
from dataclasses import dataclass

class Color(Enum):
    RED = 'red'
    BLACK = 'black'
    GREEN = 'green'

@dataclass(frozen=True)
class RouletteCell:
    number: int
    color: Color
