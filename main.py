from casino.casino import Casino
from casino.player import PlayerController


def main():
    casino = Casino("Python Casino", PlayerController("Alice"))
    casino.menu()


if __name__ == "__main__":
    main()
