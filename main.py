from casino.casino import Casino
from casino.player import Player


def main():
    casino = Casino("Python Casino", Player("Alice"))
    casino.menu()


if __name__ == "__main__":
    main()
