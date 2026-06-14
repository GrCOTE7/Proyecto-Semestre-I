import flet as ft
from ui.models.cards import CardControl
from utils.cards import Card, CardView, Rank, Suit
from pathlib import Path

def main(page: ft.Page):
    card = Card(suit=Suit.SPADES, rank=Rank.ACE)

    page.title = "Flet on Arch!"
    page.add(ft.Text("Hello, Arch Linux with KDE!"))
    page.add(CardControl(card_view=CardView(rank=card.rank, suit=card.suit, is_face_up=False))) 


if __name__ == "__main__":
    current_dir = Path(__file__).parent
    assets_path = current_dir.parent / "assets"
    
    ft.run(main, assets_dir=str(assets_path))
