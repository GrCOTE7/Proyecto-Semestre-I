import flet as ft
from utils.cards import CardView, Suit
from pathlib import Path

SUIT_LOOKUP = {
    Suit.HEARTS: ft.Colors.RED_600,
    Suit.DIAMONDS: ft.Colors.RED_600,
    Suit.SPADES: ft.Colors.BLACK,
    Suit.CLUBS: ft.Colors.BLACK,
}

class CardControl(ft.Container):
    """A highly reusable graphic widget representing a single playing card."""
    
    def __init__(self, card_view: CardView, height: int = 100):
        super().__init__()
        self.height = height
        self.width = int(height * 0.7)  # Standard card aspect ratio
        self.border_radius = 8
        self.animate = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.card_view = card_view

        if not card_view.is_face_up or card_view is None:
            self._render_face_down()
        else:
            self._render_face_up()

    def _render_face_up(self):
        color = SUIT_LOOKUP.get(self.card_view.suit, ft.Colors.BLACK)
        
        self.bgcolor = ft.Colors.WHITE
        self.border = ft.Border.all(1, ft.Colors.GREY_300)
        self.shadow = ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK))
        
        self.content = ft.Stack([
            ft.Container(
                content=ft.Text(str(self.card_view.rank.value), size=14, weight=ft.FontWeight.BOLD, color=color),
                top=5,
                left=5,
            ),
            ft.Container(
                content=ft.Text(self.card_view.suit.value, size=28, color=color),
                alignment=ft.Alignment.CENTER,
            )
        ])

    def _render_face_down(self):
        self.border = ft.Border.all(2, ft.Colors.WHITE)
        self.shadow = ft.BoxShadow(blur_radius=4, color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK))
        
        # current_dir = Path(__file__)
        
        # print(current_dir.parent.parent.parent)
        # assets_path = current_dir / "assets"
    
        # src=str("/src/assets/images/card_back.png")
        # print(f"{src = }")

        # src=str(assets_path / "images" / "card_back.png"),
        # assets_path = current_dir / "assets"
        self.content = ft.Image(
            src="images/card_back.png",
            fit=ft.BoxFit.CONTAIN,
            border_radius=self.border_radius,
        )
