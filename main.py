from casino.casino import Casino
from casino.player import Player

def main():
    casino = Casino("Python Casino")
    casino.add_player(casino.players.append(Player("Alice")))

    while True:
        casino.menu()
        continue_playing = input("Do you want to play another game? (y/n): ").lower()
        if continue_playing != 'y':
            print("Thank you for visiting Python Casino! Goodbye!")
            break

if __name__ == "__main__":
    main()
