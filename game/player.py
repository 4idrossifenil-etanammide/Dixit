from abc import ABC, abstractmethod
from typing import List, Tuple
from typing_extensions import Self
import random

from card import Card

class Player(ABC):
    def __init__(self, player_name: str, points_to_win: int):
        self.player_name = player_name
        self.points_to_win = points_to_win
        self.points = 0
        self.cards_in_hand = []
   
    # The initial deck should have enough cards for all the players, so no check is needed
    def draw_initial_hand(self, images: List[Card]) -> List[Card]:
        self.cards_in_hand = random.sample(images, 6)

        for img in self.cards_in_hand:
            images.remove(img)

        return images

    def draw_card(self, images: List[Card]) -> List[Card]:
        drawn_card = random.choice(images)
        images.remove(drawn_card)

        self.cards_in_hand.append(drawn_card)
        return images

    def add_points(self, to_add: int) -> None:
        self.points += to_add

    def check_winning_condition(self) -> bool:
        return self.points >= self.points_to_win

    @abstractmethod
    def get_card_and_caption(self) -> Tuple[Card, str]:
        pass

    @abstractmethod
    def select_card_from_caption(self, caption: str) -> Card:
        pass

    @abstractmethod
    def get_most_likely_card(self, cards_on_table: List[Tuple[Self, Card]], caption: str) -> Self:
        pass
    
    def __repr__(self) -> str:
        return self.player_name
