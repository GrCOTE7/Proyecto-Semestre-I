from blessed import Terminal

# Global terminal instance for use throughout the application
term = Terminal()

BG_COLOR = term.on_color_hex("#2f6b4d")


def get_bg_at(x, y):
    """
    Determines what should be at a specific coordinate.
    Uses the coordinates as a seed so the 'randomness' is static.
    """
    # SUIT_COLOR = term.color_hex("#00FF7F")
    # SUITS = ["♠", "♣", "♥", "♦"]

    # if (x + y) % 5 == 0 and y % 2 == 0:
    #     return BG_COLOR + SUIT_COLOR + SUITS[(x + y) // 5 % len(SUITS)] + term.normal
    # else:
    #     return BG_COLOR + " " + term.normal

    return BG_COLOR + " " + term.normal


def draw_bg():
    """
    Draws the checkered background pattern.
    """
    for y in range(term.height):
        line = "".join(get_bg_at(x, y) for x in range(term.width))
        print(line, end="")
