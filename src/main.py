import flet as ft
from ui.models.cards import CardControl
from utils.cards import Card, CardView, Rank, Suit
from pathlib import Path

def main(page: ft.Page, mypath="OKi"):
    card = Card(suit=Suit.SPADES, rank=Rank.ACE)

    current_dir = Path(__file__).parent.parent
    assets_path = current_dir / "assets"

    mypath = assets_path / "images" / "card_back.png"

    page.title = "Flet on Arch!"
    
    page.add(ft.Text("Hello, Arch Linux with KDE! → " + str(mypath)))
    
    page.add(CardControl(card_view=CardView(rank=card.rank, suit=card.suit, is_face_up=False))) 


if __name__ == "__main__":
    current_dir = Path(__file__).parent.parent
    # print(current_dir)
    assets_path = current_dir / "../assets"
    
    ft.run(main, assets_dir=str('../assets'))
